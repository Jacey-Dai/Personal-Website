"""Extract only selected glTF models and their dependencies from the owner's asset branch.

Usage: python3 tools/extract_art_sample.py /tmp/island-art-sources
No raw packs are copied into public/. Uses a pinned Git commit for reproducibility.
"""
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

SOURCE_COMMIT = "7b16930628d5adc01c6e5f98afde99199ea21e3a"
SELECTION = {
    "Medieval Village MegaKit[Standard]": [
        "Roof_RoundTiles_4x6", "Wall_Plaster_Straight", "Wall_Plaster_Door_Round",
        "Wall_Plaster_Window_Wide_Round", "Door_1_Round", "Window_Wide_Round1",
        "Prop_Chimney", "Prop_Crate", "Floor_WoodLight", "Prop_WoodenFence_Single",
        "Balcony_Simple_Straight",
    ],
    "Stylized Nature MegaKit[Standard]": [
        "CommonTree_1", "CommonTree_3", "Pine_5", "Bush_Common_Flowers",
        "Rock_Medium_1", "Rock_Medium_2", "Flower_3_Group",
    ],
}


def blob(path):
    return subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{path}"])


def extract(destination):
    destination.mkdir(parents=True, exist_ok=True)
    extracted = set()
    def save(path):
        relative = PurePosixPath(path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe source path: {path}")
        target = destination.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = blob(path)
        if target.exists() and target.read_bytes() != data:
            raise FileExistsError(f"Refusing to overwrite modified source: {target}")
        target.write_bytes(data)
        extracted.add(path)
        return data

    for pack, models in SELECTION.items():
        base = f"assests/{pack}"
        save(f"{base}/License_Standard.txt")
        for model in models:
            filename = f"{base}/glTF/{model}.gltf"
            data = json.loads(save(filename))
            for item in data.get("buffers", []) + data.get("images", []):
                uri = item.get("uri", "")
                if uri and not uri.startswith("data:"):
                    save(str(PurePosixPath(filename).parent / unquote(uri)))
    print(json.dumps({"source_commit": SOURCE_COMMIT, "models": sum(map(len, SELECTION.values())), "files": len(extracted), "destination": str(destination)}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tools/extract_art_sample.py DESTINATION")
    extract(Path(sys.argv[1]))
