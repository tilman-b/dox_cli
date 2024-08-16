# DOX cli
![example workflow](https://github.com/tilman-b/sap_dox_cli/actions/workflows/python-app.yml/badge.svg)

## Introduction
This tool provides a solution for extracting data from invoices, purchase orders, or payment advices provided in PDF format. 
It leverages the [SAP Document Information Extraction service](https://help.sap.com/docs/document-information-extraction/document-information-extraction/what-is-document-information-extraction) and is designed for use with an SAP BTP trial account.

## Installation
To install the tool, simply execute the following command:
```bash
pip install git+https://github.com/tilman-b/dox_cli.git
```

## Usage
After successful installation you can use this tool by running `dox` on your shell.
`dox --help` shows an overview of all options.

General usage is `dox [options] FILE`

In order to use this tool it is assumed that you have an SAP BTP trial account created as described [here](https://developers.sap.com/tutorials/hcp-create-trial-account.html).
### Options
All options can be specified either as parameters when running the tool or as environment variables (in uppercase and prefixed with `DOX_`).
 - `--oauth_client_id|DOX_OAUTH_CLIENT_ID` 
(Required) The id of the client used for authentication. 
Note: this is not id of the client used for extraction.
 - `--oauth_client_secret|DOX_OAUTH_CLIENT_SECRET` 
(Required) The secret for authentication.
 - `--oauth_url|DOX_OAUTH_URL` 
(Required) URL to authenticate against
 - `--base_url|DOX_BASE_URL`
(Required) Base URL of the document extraction service
 - `--document_type|DOX_DOCUMENT_TYPE`
(Required) Document type of the provided file. Must be one of `invoice`, `paymentAdvice`, `purchaseOrder`.
Custom document types are not supported by now. More details can be found [here](https://help.sap.com/docs/document-information-extraction/document-information-extraction/supported-document-types-and-file-formats)
 - `--output_format|DOX_OUTPUT_FORMAT`
(Optional) Output format. Must be either `raw_json` (all fields are printed) or `simplified_json` (only some fields are printed). Default is `raw_json`
 - `--keep_doc|DOX_KEEP_DOC`
Flag to keep the document in the SAP Document Information Extraction Service after finished.
 - `--max_wait|DOX_MAX_WAIT`
(Optional) Seconds to wait for the document extraction service. Default is 60.

### Examples

#### Use parameters

```bash
dox --oauth_client_id <oauth_client_id> \
--oauth_client_secret <oauth_client_secret> \
--oauth_url <oauth_url> \
--base_url <base_url> \
--document_type <document_type> \
invoice.pdf
```

#### Use env vars
```bash
export DOX_OAUTH_CLIENT_ID=<oauth_client_id>
export DOX_OAUTH_CLIENT_SECRET=<oauth_client_secret>
export DOX_OAUTH_URL=<oauth_url>
export DOX_BASE_URL=<base_url>
export DOX_DOCUMENT_TYPE=<document_type>

dox invoice.pdf
```


## Limitations
- used client is limited to the `default` client which is the only possible client in a trial account
- only one file can be processed per cli call
- only pdf files are supported

## Disclaimer
This project is an independent initiative and is not affiliated with, endorsed by, or connected to SAP SE in any way. The author is not associated with SAP SE, and any trademarks or brand names mentioned belong to their respective owners.