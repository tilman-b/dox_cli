from typing import Tuple


def map_type_to_schema(document_type: str) -> Tuple[str, str]:
    """
    Maps document type to a predefined schema.

    | document_type | schemaName               | schemaId                             |
    | invoice       | SAP_invoice_schema       | cf8cc8a9-1eee-42d9-9a3e-507a61baac23 |
    | paymentAdvice | SAP_paymentAdvice_schema | b7fdcfac-7853-42bb-89d2-ede2ba1ce803 |
    | purchaseOrder | SAP_purchaseOrder_schema | fbab052e-6f9b-4a5f-b42f-29a8162eb1bf |


    :param document_type: must be one of invoice, paymentAdvice, purchaseOrder
    :return: Tuple containing predefined schema name and id
    """

    if document_type.lower() == "invoice":
        return "SAP_invoice_schema", "cf8cc8a9-1eee-42d9-9a3e-507a61baac23"
    elif document_type.lower() == "paymentAdvice":
        return "SAP_paymentAdvice_schema", "b7fdcfac-7853-42bb-89d2-ede2ba1ce803"
    elif document_type.lower() == "purchaseOrder":
        return "SAP_purchaseOrder_schema", "fbab052e-6f9b-4a5f-b42f-29a8162eb1bf"
    else:
        raise ValueError(f"document type: {document_type} is not supported")


def create_url(base_url: str, path: str):
    """
    concatenates an url with a path.

    :param base_url: URL which serves as base (for example http://example)
    :param path: path which shall be added to the base_url
    :return: concatenation of base_url and path
    """
    # remove all trailing / from base_url
    while base_url.endswith("/"):
        base_url = base_url[:-1]
    # add / to path if necessary
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base_url}{path}"


def _simplify_fields(json: dict) -> dict:
    result = {}
    for k in ("name", "category", "value", "rawValue", "type", "label"):
        result[k] = json[k]
    return result


def simplify_json(json: dict) -> dict:
    """
    Simplifies the output of the document information extraction service by removing all fields except:
     - id
     - fileName
     - documentType
     - languageCodes
     - headerFields
        - name
        - category
        - value
        - rawValue
        - type
        - label
    - lineItems
        - name
        - category
        - value
        - rawValue
        - type
        - label

    :param json:
    :return: dict containing only the aforementioned keys
    """
    result = {}
    for k in ("id", "fileName", "documentType", "languageCodes"):
        result[k] = json[k]
    result["extraction"] = {
        "headerFields": [
            _simplify_fields(v) for v in json["extraction"]["headerFields"]
        ],
        "lineItems": [
            [_simplify_fields(e) for e in v] for v in json["extraction"]["lineItems"]
        ],
    }

    return result
