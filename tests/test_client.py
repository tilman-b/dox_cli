import json
import unittest
from unittest.mock import patch

from oauthlib.oauth2 import TokenExpiredError
from requests import Response

from sap_dox_cli.client import (
    DocumentExtractionClient,
    ExtractionException,
    HttpException,
)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = DocumentExtractionClient(
            base_url="http://extraction-service",
            oauth_url="http://oauth-url",
            client_id="test",
            client_secret="secret",
        )

    @staticmethod
    def _create_response(status_code: int, **kwargs) -> Response:
        response = Response()
        response.status_code = status_code
        response._content = json.dumps(kwargs).encode(encoding="utf-8")

        return response

    def test_upload_pdf(self):
        with patch.object(self.client, "_session") as mock:
            mock.post.return_value = self._create_response(201)
            # we want to check if the request was correct therefore we do not care about the return value
            _ = self.client.upload_pdf(
                document_path="tests/data/test.pdf",
                document_type="invoice",
                schema_id="schema_1",
            )

            called_url = mock.post.call_args.args
            payload = mock.post.call_args.kwargs
            self.assertEqual(
                called_url[0],
                "http://extraction-service/document-information-extraction/v1/document/jobs",
            )
            self.assertEqual(payload["files"]["file"][0], "test.pdf")

    def test_get_result(self):
        with patch.object(self.client, "_session") as mock:
            mock.get.return_value = self._create_response(200, status="READY")

            # ignore response
            _ = self.client.get_result(document_id="1234")
            called_url = mock.get.call_args.args

            self.assertEqual(
                called_url[0],
                "http://extraction-service/document-information-extraction/v1/document/jobs/1234",
            )

    def test_upload_pdf_failure(self):
        with patch.object(self.client, "_session") as mock:
            mock.post.return_value = self._create_response(500)

            self.assertRaises(
                HttpException,
                self.client.upload_pdf,
                document_path="tests/data/test.pdf",
                document_type="invoice",
                schema_id="schema_1",
            )

    def test_get_result_failure(self):
        with patch.object(self.client, "_session") as mock:
            mock.get.return_value = self._create_response(500)

            self.assertRaises(HttpException, self.client.get_result, document_id="123")

    def test_get_result_failure_state(self):
        with patch.object(self.client, "_session") as mock:
            mock.get.return_value = self._create_response(200, status="FAILED")

            self.assertRaises(
                ExtractionException, self.client.get_result, document_id="1234"
            )

    def test_oauth_call(self):
        with patch.object(self.client, "_session") as mock:
            mock.get.side_effect = [
                TokenExpiredError(),
                self._create_response(200, status="READY"),
            ]
            _ = self.client.get_result(document_id="1234")

            self.assertEqual(mock.fetch_token.call_count, 2)
