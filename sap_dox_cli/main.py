import json
import sys
import time

import click

from sap_dox_cli.client import DocumentExtractionClient
from sap_dox_cli.helper import map_type_to_schema


@click.command()
@click.option(
    "--oauth_client_id",
    required=True,
    help="The id of the client used for authentication. Note: this is not id of the client used for extraction."
)
@click.option(
    "--oauth_client_secret",
    required=True,
    help="The secret for authentication."
)
@click.option(
    "--oauth_url",
    required=True,
    help="URL to authenticate against"
)
@click.option(
    "--base_url",
    required=True,
    help="Base URL of the document extraction service"
)
@click.option(
    "--max_wait",
    type=int,
    default=15,
    help="seconds to wait for the document extraction service"
)
@click.option(
    "--document_type",
    type=click.Choice(["invoice", "paymentAdvice", "purchaseOrder"], case_sensitive=False),
    required=True,
    help="""Document type of the provided file. 
    Custom document types are not supported by now. 
    See also: https://help.sap.com/docs/document-information-extraction/document-information-extraction/supported-document-types-and-file-formats""")
@click.argument("file", type=click.Path(exists=True))
def run(oauth_client_id: str, oauth_client_secret: str, oauth_url: str, base_url: str, max_wait: int, document_type: str, file: str):
    """Extracts data from a pdf by using SAP Document Extraction Service"""
    client = DocumentExtractionClient(
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        oauth_url=oauth_url,
        base_url=base_url
    )
    _, schema_id = map_type_to_schema(document_type=document_type)
    uploaded_data = client.upload_pdf(document_path=file, document_type=document_type, schema_id=schema_id)
    document_id = uploaded_data["id"]
    for _ in range(max_wait):
        result = client.get_result(document_id=document_id)
        if result["status"] == "DONE":
            print(json.dumps(result, indent=4))
            sys.exit(0)
        time.sleep(1)
    print(f"""Document was not in status 'DONE' after {max_wait} seconds. 
This does not mean there was an error. Please check later.""")
    sys.exit(1)


if __name__ == '__main__':
    run(max_content_width=120, auto_envvar_prefix="SAP")

