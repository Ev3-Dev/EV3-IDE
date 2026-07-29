import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent
    full_path = base_path / relative_path
    if not full_path.exists():
        print(f"⚠️ WARNUNG: Datei nicht gefunden: {full_path}")
        print(f"   Base path: {base_path}")
        print(f"   Relative path: {relative_path}")
    full_path = str(full_path).replace("\\", "/")
    return full_path