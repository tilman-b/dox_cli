import json
import sys
import time

import click

from dox_cli.client import DocumentExtractionClient
from dox_cli.helper import map_type_to_schema


def _add_env_var_help(env_var: str) -> str:
    return f"Can be omitted if {env_var} is set"


@click.command()
@click.option(
    "--oauth_client_id",
    required=True,
    help=f"""The id of the client used for authentication. Note: this is not id of the client used for extraction.
 {_add_env_var_help('DOX_OAUTH_CLIENT_ID')}""",
)
@click.option(
    "--oauth_client_secret",
    required=True,
    help=f"The secret for authentication. {_add_env_var_help('DOX_OAUTH_CLIENT_SECRET')}",
)
@click.option(
    "--oauth_url",
    required=True,
    help=f"URL to authenticate against. {_add_env_var_help('DOX_OAUTH_URL')}",
)
@click.option(
    "--base_url",
    required=True,
    help=f"Base URL of the document extraction service. {_add_env_var_help('DOX_BASE_URL')}",
)
@click.option(
    "--document_type",
    type=click.Choice(
        ["invoice", "paymentAdvice", "purchaseOrder"], case_sensitive=False
    ),
    required=True,
    help=f"""Document type of the provided file. 
    Custom document types are not supported by now. 
    See also: https://help.sap.com/docs/document-information-extraction/document-information-extraction/supported-document-types-and-file-formats
    {_add_env_var_help('DOX_DOCUMENT_TYPE')}
    """,
)
@click.option(
    "--keep_doc",
    is_flag=True,
    default=False,
    help=f"keep the document in the SAP Document Information Extraction Service after finished. {_add_env_var_help('DOX_KEEP_DOC')}",
)
@click.option(
    "--max_wait",
    type=int,
    default=60,
    show_default=True,
    help=f"Seconds to wait for the document extraction service. {_add_env_var_help('DOX_MAX_WAIT')}",
)
@click.argument("file", type=click.Path(exists=True))
def run(
    oauth_client_id: str,
    oauth_client_secret: str,
    oauth_url: str,
    base_url: str,
    keep_doc: bool,
    max_wait: int,
    document_type: str,
    file: str,
):
    """Extracts data from a pdf by using SAP Document Extraction Service"""
    client = DocumentExtractionClient(
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        oauth_url=oauth_url,
        base_url=base_url,
    )
    _, schema_id = map_type_to_schema(document_type=document_type)
    uploaded_data = client.upload_pdf(
        document_path=file, document_type=document_type, schema_id=schema_id
    )
    document_id = uploaded_data["id"]
    for _ in range(max_wait):
        result = client.get_result(document_id=document_id)
        if result["status"] == "DONE":
            print(json.dumps(result, indent=4))
            if not keep_doc:
                client.delete_document(document_id=document_id)
            sys.exit(0)
        time.sleep(1)
    print(
        f"""Document status not 'DONE' after {max_wait} seconds. 
This may not indicate an error. Please check again later."""
    )
    sys.exit(1)


if __name__ == "__main__":
    run(max_content_width=120, auto_envvar_prefix="DOX")
