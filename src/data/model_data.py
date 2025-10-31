import json
from pygltflib import GLTF2

JSON_PATH = "electric_guitar.json"


def load_schema():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_schema(schema):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)


def update_schema_from_glb(glb_path: str):
    schema = load_schema()
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

    for key, values in dynamic_keys.items():
        if key in schema and values:
            schema[key]["values"] = sorted(list(values))

    pickup_values = sorted(list(dynamic_keys["pickup_types"])) + ["none"]
    for slot in ["firstPickup", "secondPickup", "thirdPickup"]:
        if slot in schema:
            schema[slot]["values"] = pickup_values

    save_schema(schema)

#updating json files if necessary
if __name__ == "__main__":
    update_schema_from_glb("electric_guitar.glb")
