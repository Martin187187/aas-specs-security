"""Regression checks for named object groups in the 3.0 schemas.

Install jsonschema==4.25.1, then run:
    python -m unittest discover -s tests
"""

import json
from pathlib import Path
import unittest
import warnings

from jsonschema import Draft7Validator

with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from jsonschema import RefResolver


JSON_DIR = (
    Path(__file__).resolve().parents[1]
    / "documentation/IDTA-01004/modules/ROOT/partials/json"
)
GROUP_REFS = {
    "access-rule-model.json": (
        "#/properties/AllAccessPermissionRules/properties/DEFOBJECTS/items"
    ),
    "aas-queries-and-access-rules-schema.json": (
        "#/definitions/AllAccessPermissionRules/properties/DEFOBJECTS/items"
    ),
}
DIRECT_OBJECTS = [{"REFERABLE": '$sme("*").DateOfPuttingIntoService'}]
GROUP_REFERENCES = ["public-data-points", "updated-data-points"]


class DefobjectsSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = {}
        for name, group_ref in GROUP_REFS.items():
            path = JSON_DIR / name
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft7Validator.check_schema(schema)
            cls.validators[name] = Draft7Validator(
                {"$ref": group_ref},
                resolver=RefResolver(base_uri=path.as_uri(), referrer=schema),
            )

    def assert_group_validity(self, group, expected):
        for name, validator in self.validators.items():
            with self.subTest(schema=name):
                errors = list(validator.iter_errors(group))
                self.assertEqual(not errors, expected, errors)

    def test_direct_objects(self):
        self.assert_group_validity(
            {"name": "direct", "objects": DIRECT_OBJECTS}, True
        )

    def test_group_references(self):
        self.assert_group_validity(
            {"name": "references", "USEOBJECTS": GROUP_REFERENCES}, True
        )

    def test_mixed_objects_and_references(self):
        self.assert_group_validity(
            {
                "name": "mixed",
                "objects": DIRECT_OBJECTS,
                "USEOBJECTS": GROUP_REFERENCES,
            },
            True,
        )

    def test_missing_objects_and_references(self):
        self.assert_group_validity({"name": "missing-entries"}, False)

    def test_missing_group_name(self):
        self.assert_group_validity(
            {"objects": DIRECT_OBJECTS, "USEOBJECTS": GROUP_REFERENCES}, False
        )


if __name__ == "__main__":
    unittest.main()
