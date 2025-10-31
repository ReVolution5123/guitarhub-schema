import json
import os
from pygltflib import GLTF2
from src.services.schema_service import SchemaService


def update_schema_from_glb(glb_path: str):
    schema = SchemaService()
    glb = GLTF2().load(glb_path)

    dynamic_keys = {
        "body": set(),
        "bridge": set(),
        "neck": set(),
        "pickup_types": set()
    }

    for node in glb.nodes:
        if not node.name:
            continue
        name = node.name.lower()

        if name.endswith("-body"):
            dynamic_keys["body"].add(name.replace("-body", ""))
        elif name.endswith("-bridge"):
            dynamic_keys["bridge"].add(name.replace("-bridge", ""))
        elif name.endswith("-pick-metal"):
            dynamic_keys["pickup_types"].add(name.replace("-pick-metal", ""))
        elif name.endswith("-neck"):
            dynamic_keys["neck"].add(name.replace("-neck", ""))

    def custom_sort(values: set, priority_items: tuple[str, ...] = ()):
        priority_map = {name: i for i, name in enumerate(priority_items)}
        return sorted(values, key=lambda x: (priority_map.get(x, len(priority_items)), x))

    for key in ["body", "bridge", "neck"]:
        values = dynamic_keys[key]
        if key in schema.data and values:
            schema.data[key]["values"] = custom_sort(values, ("st", "te"))

    pickup_sorted = custom_sort(dynamic_keys["pickup_types"], ("single",))
    pickup_values = pickup_sorted + ["none"]
    for slot in ["firstPickup", "secondPickup", "thirdPickup"]:
        if slot in schema.data:
            schema.data[slot]["values"] = pickup_values

    schema.save_schema(schema.data)

    defaults = {}

    for key, prop in schema.data.items():
        t = prop.get("type")

        if t == "enum":
            values = prop.get("values", [])
            defaults[key] = values[0] if values else None

        elif t == "boolean":
            defaults[key] = True

        elif t == "string":
            pattern = prop.get("pattern", "")
            if "0-9a-fA-F" in pattern:
                defaults[key] = "#FFFFFF"
            else:
                defaults[key] = ""

        elif t == "object" and key == "bodyPaint":
            defaults[key] = {
                "mode": "solid",
                "plane": "xy",
                "angleDeg": 0,
                "power": 1,
                "smooth": 1,
                "stops": [{"pos": 0, "color": "#FFFFFF"}]
            }

        else:
            defaults[key] = None

    try:
        schema.validate(defaults)
    except ValueError as e:
        print(str(e))
        return

    defaults_path = os.path.join(os.path.dirname(schema.JSON_PATH), "electric_guitar_defaults.json")
    with open(defaults_path, "w", encoding="utf-8") as f:
        json.dump(defaults, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Defaults file created at: {defaults_path}")


if __name__ == "__main__":
    update_schema_from_glb("electric_guitar.glb")
