import unittest

from sap_dox_cli.helper import create_url, map_type_to_schema


class TestHelpers(unittest.TestCase):

    def test_map_type_to_schema(self):
        self.assertEqual(
            map_type_to_schema("INVOICE"),
            ("SAP_invoice_schema", "cf8cc8a9-1eee-42d9-9a3e-507a61baac23"),
        )
        self.assertRaises(ValueError, map_type_to_schema, "DOES_NOT_EXIST")

    def test_create_url(self):
        self.assertEqual(create_url("http://example", "foo"), "http://example/foo")
        self.assertEqual(create_url("http://example", "/foo"), "http://example/foo")
        self.assertEqual(create_url("http://example/", "/foo"), "http://example/foo")
        self.assertEqual(create_url("http://example//", "foo"), "http://example/foo")
