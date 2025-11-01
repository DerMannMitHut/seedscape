#!/usr/bin/env python3
"""
Seedscape Build-Check für Poetry
--------------------------------
Dieses Skript überprüft, ob das Poetry-Paket korrekt konfiguriert ist:

1. Führt `poetry build` aus (erstellt sdist + wheel)
2. Listet Inhalte des sdist (tar.gz) auf
3. Prüft, ob src/seedscape/ gefunden wurde
4. Prüft, ob optionale Verzeichnisse (frontend, rules, data) enthalten sind
"""

import tarfile
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(cmd: list[str]) -> str:
    print(">", " ".join(cmd))
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit(e.returncode)

def build_poetry_package():
    dist = ROOT / "dist"
    if dist.exists():
        for f in dist.iterdir():
            f.unlink()
    print("📦 Building with Poetry…")
    run(["poetry", "build"])
    tgz_files = list(dist.glob("*.tar.gz"))
    if not tgz_files:
        print("❌ Kein sdist gefunden.")
        sys.exit(1)
    return tgz_files[0]

def inspect_archive(archive_path: Path):
    print(f"🔍 Überprüfe Inhalt von {archive_path.name}")
    found = {"seedscape": False, "frontend": False, "rules": False, "data": False}
    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getnames():
            if "seedscape/__init__.py" in member:
                found["seedscape"] = True
            for key in ["frontend", "rules", "data"]:
                if f"/{key}/" in member:
                    found[key] = True
    return found

def main():
    archive = build_poetry_package()
    results = inspect_archive(archive)
    print("\n📋 Ergebnis:")
    for key, ok in results.items():
        mark = "✅" if ok else "⚠️"
        print(f"  {mark} {key}")
    if all(results.values()):
        print("\n🎉 Alles korrekt enthalten!")
    else:
        print("\nBitte prüfe die 'include'-Sektion in deiner pyproject.toml:")
        print("packages = [{ include = 'seedscape', from = 'src' }]")
        print("include = [{ path = 'frontend', format = 'sdist' }, { path = 'rules', format = 'sdist' }, { path = 'data', format = 'sdist' }]")


if __name__ == "__main__":
    main()
