import os
import json
import re


class SchemaService:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    JSON_PATH = os.path.join(BASE_DIR, "src", "data", "electric_guitar.json")
    DEFAULTS_PATH = os.path.join(BASE_DIR, "src", "data", "electric_guitar_defaults.json")

    def __init__(self):
        print(f"[DEBUG] BASE_DIR: {self.BASE_DIR}")
        print(f"[DEBUG] JSON_PATH: {self.JSON_PATH}")
        self.data = self.load_schema()
        self.defaults = self.load_defaults()

    def load_schema(self):
        if not os.path.exists(self.JSON_PATH):
            raise FileNotFoundError(f"Schema file not found: {self.JSON_PATH}")

        try:
            with open(self.JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON schema: {e}\nPath: {self.JSON_PATH}")

    def save_schema(self, schema):
        with open(self.JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)

    def load_defaults(self):
        if not os.path.exists(self.DEFAULTS_PATH):
            print(f"[WARN] Defaults file not found: {self.DEFAULTS_PATH}")
            return {}

        try:
            with open(self.DEFAULTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"[INFO] Defaults loaded successfully ({len(data)} fields)")
                return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse defaults JSON: {e}\nPath: {self.DEFAULTS_PATH}")

    def validate(self, data: dict):
        errors = []

        def validate_field(key_path, field_schema, value):
            ftype = field_schema.get("type")

            if ftype == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"{key_path}: expected boolean, got {type(value).__name__}")

            elif ftype == "enum":
                valid_values = field_schema.get("values", [])
                if value not in valid_values:
                    errors.append(f"{key_path}: '{value}' not in allowed values {valid_values}")

            elif ftype == "string":
                if not isinstance(value, str):
                    errors.append(f"{key_path}: expected string, got {type(value).__name__}")
                else:
                    pattern = field_schema.get("pattern")
                    if pattern and not re.match(pattern, value):
                        errors.append(f"{key_path}: string does not match pattern {pattern}")

            elif ftype == "number":
                if not isinstance(value, (int, float)):
                    errors.append(f"{key_path}: expected number, got {type(value).__name__}")
                else:
                    minv = field_schema.get("min")
                    maxv = field_schema.get("max")
                    if minv is not None and value < minv:
                        errors.append(f"{key_path}: below min {minv}")
                    if maxv is not None and value > maxv:
                        errors.append(f"{key_path}: above max {maxv}")

            elif ftype == "object":
                if not isinstance(value, dict):
                    errors.append(f"{key_path}: expected object, got {type(value).__name__}")
                else:
                    props = field_schema.get("properties", {})
                    for subkey, subfield in props.items():
                        if subkey not in value:
                            errors.append(f"{key_path}.{subkey}: missing")
                            continue
                        validate_field(f"{key_path}.{subkey}", subfield, value[subkey])

            elif ftype == "array":
                if not isinstance(value, list):
                    errors.append(f"{key_path}: expected array, got {type(value).__name__}")
                else:
                    items_schema = field_schema.get("items")
                    if not items_schema:
                        errors.append(f"{key_path}: 'items' schema missing for array")
                        return

                    for i, item in enumerate(value):
                        if "type" not in items_schema:
                            if not isinstance(item, dict):
                                errors.append(f"{key_path}[{i}]: expected object, got {type(item).__name__}")
                                continue
                            for subkey, subfield in items_schema.items():
                                if subkey not in item:
                                    errors.append(f"{key_path}[{i}].{subkey}: missing")
                                    continue
                                validate_field(f"{key_path}[{i}].{subkey}", subfield, item[subkey])
                        else:
                            validate_field(f"{key_path}[{i}]", items_schema, item)


            else:
                errors.append(f"{key_path}: unknown field type '{ftype}'")

        for key, value in data.items():
            if key not in self.data:
                errors.append(f"Unexpected field: '{key}'")
                continue
            validate_field(key, self.data[key], value)

        for key in self.data.keys():
            if key not in data:
                errors.append(f"Missing required field: '{key}'")

        if errors:
            raise ValueError("Validation failed:\n- " + "\n- ".join(errors))

        return True

