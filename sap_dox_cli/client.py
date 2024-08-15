import json
from pathlib import Path
from typing import Callable

from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session

from sap_dox_cli.helper import create_url


class ExtractionException(Exception):

    def __init__(self, message, document_id):
        super().__init__(f"{message} (document id: {document_id})")


class HttpException(Exception):

    def __init__(self, message, status_code):
        super().__init__(f"HTTP {status_code}: {message}")


class DocumentExtractionClient:
    """
    Basic client to interact with the Document Extraction Service API.
    See https://help.sap.com/docs/document-information-extraction/document-information-extraction/api-reference
    for more details
    """

    def __init__(self, base_url: str, oauth_url: str, client_id: str, client_secret: str):
        """
        Create a new client to interact with the Document Extraction Service API

        :param base_url: base url of the document extraction service.
        :param oauth_url: base url for authentication
        :param client_id: id of the used client
        :param client_secret: secret to authenticate
        """
        self._oauth_url = create_url(oauth_url, "/oauth/token")
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._client = BackendApplicationClient(client_id=self._client_id)
        self._session = OAuth2Session(client=self._client)
        self._token = None

    def _renew(self) -> None:
        self.token = self._session.fetch_token(
            token_url=self._oauth_url,
            client_id=self._client_id,
            client_secret=self._client_secret
        )

    def _call_api(self, url: str, method: Callable, validation_http_status: int, **kwargs) -> dict:
        if self._token is None:
            self._renew()
        try:
            response = method(url, **kwargs)
        except TokenExpiredError:
            self._renew()
            response = method(url, **kwargs)
        if response.status_code > validation_http_status:
            raise HttpException(response.text, response.status_code)
        return response.json()

    def _post(self, url: str, **kwargs) -> dict:
        return self._call_api(url, self._session.post, 201, **kwargs)

    def _get(self, url: str, **kwargs) -> dict:
        return self._call_api(url, self._session.get, 200, **kwargs)

    def upload_pdf(self, document_path: str, document_type: str, schema_id: str) -> dict:
        """
        Upload a pdf to the document extraction service in order to extract its data.
        If the client specified by client_id and client_name do not exist it will be created.

        :param document_path: path to the pdf to be processed. File must be readable.
        :param document_type: type of the document. Must be one of
        :param schema_id: id of the schema to be used.
        :return: dictionary containing id, processedTime and status.
        See https://help.sap.com/docs/document-information-extraction/document-information-extraction/upload-document?locale=en-US#:~:text=Response-,Response%20Fields,-JSON%20Field
        for more details
        """

        filename = Path(document_path).name
        return self._post(
            create_url(self._base_url, "/document-information-extraction/v1/document/jobs"),
            files={"file": (filename, open(document_path, "rb"), "application/pdf")},
            data={
                "options": json.dumps({
                    "documentType": document_type,
                    "clientId": "default",
                    "schemaId": schema_id
                })
            }
        )

    def get_result(self, document_id: str) -> dict:
        """
        Returns the result for an extraction run.

        :param document_id: id of the document which data is being extracted
        :return: dictionary containing extracted data.
        See https://help.sap.com/docs/document-information-extraction/document-information-extraction/get-result?locale=en-US#:~:text=are%20not%20returned.-,Response,-Response%20Fields
        :raises ExtractionException in case the extraction process did not work
        """
        response = self._get(
            create_url(self._base_url, f"/document-information-extraction/v1/document/jobs/{document_id}")
        )

        if response["status"] == "FAILED":
            raise ExtractionException(message="extraction failed", document_id=document_id)
        return response

