#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import re
import shutil
import tarfile
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / ".bootstrap" / "Circuit.tar.xz.b64"
TRACK_DIR = ROOT / "tracks" / "circuit"
INDEX = ROOT / "index.json"
LINKS = ROOT / "TRACK_URLS.md"
README = ROOT / "README.md"
RAW_BASE = "https://raw.githubusercontent.com/kyotostudios/ks_racing_tracks/main/tracks/circuit"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("&", " and ")
    value = value.replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "track"


def main() -> None:
    if not PAYLOAD.exists():
        raise SystemExit(f"Payload not found: {PAYLOAD}")

    archive_bytes = base64.b64decode(PAYLOAD.read_text(encoding="utf-8"), validate=True)

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "Circuit.tar.xz"
        archive.write_bytes(archive_bytes)

        TRACK_DIR.mkdir(parents=True, exist_ok=True)
        for old in TRACK_DIR.glob("*.json"):
            old.unlink()

        tracks = []
        used = set()

        with tarfile.open(archive, mode="r:xz") as tf:
            members = [
                m for m in tf.getmembers()
                if m.isfile() and m.name.lower().endswith(".json")
            ]
            members.sort(key=lambda m: Path(m.name).name.casefold())

            for member in members:
                original_filename = Path(member.name).name
                original_name = Path(original_filename).stem

                extracted = tf.extractfile(member)
                if extracted is None:
                    raise RuntimeError(f"Unable to read {member.name}")

                raw = extracted.read()

                # Validate the track before publishing it.
                data = json.loads(raw.decode("utf-8-sig"))
                if not isinstance(data, list) or not data:
                    raise ValueError(f"{original_filename}: expected a non-empty JSON array")
                for idx, checkpoint in enumerate(data):
                    if not isinstance(checkpoint, dict) or "coords" not in checkpoint:
                        raise ValueError(f"{original_filename}: invalid checkpoint at index {idx}")

                base_slug = slugify(original_name)
                slug = base_slug
                suffix = 2
                while slug in used:
                    slug = f"{base_slug}-{suffix}"
                    suffix += 1
                used.add(slug)

                destination = TRACK_DIR / f"{slug}.json"
                destination.write_bytes(raw)

                raw_url = f"{RAW_BASE}/{slug}.json"
                tracks.append({
                    "name": original_name,
                    "slug": slug,
                    "file": f"tracks/circuit/{slug}.json",
                    "raw_url": raw_url,
                    "checkpoints": len(data),
                    "layout": "circuit",
                })

    if len(tracks) != 86:
        raise ValueError(f"Expected 86 tracks, found {len(tracks)}")

    tracks.sort(key=lambda x: x["name"].casefold())

    INDEX.write_text(
        json.dumps(
            {
                "repository": "kyotostudios/ks_racing_tracks",
                "category": "circuit",
                "count": len(tracks),
                "tracks": tracks,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Circuit track RAW URLs",
        "",
        "Links diretos para importar no KS Racing App.",
        "",
        "| Pista | Checkpoints | URL RAW |",
        "|---|---:|---|",
    ]
    for track in tracks:
        lines.append(
            f'| {track["name"].replace("|", "\\|")} | {track["checkpoints"]} | '
            f'[{track["slug"]}.json]({track["raw_url"]}) |'
        )
    LINKS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    readme = f"""# Kyoto Studios — Racing Tracks

Repositório público de pistas usadas pelo **KS Racing App / Eclipse RP**.

## Estrutura

- `tracks/circuit/`: {len(tracks)} pistas de circuito em JSON.
- `index.json`: índice legível por aplicações, com nome, caminho, quantidade de checkpoints e URL RAW.
- `TRACK_URLS.md`: lista completa de links diretos para importação.

## Importar uma pista

No KS Racing App, abra **Importar pista** e cole a URL RAW da pista no campo **URL da pista**.

Exemplo:

```text
{tracks[0]["raw_url"]}
```

Os arquivos publicados em `tracks/circuit/` preservam o JSON original; apenas os nomes de arquivo foram normalizados para URLs estáveis.
"""
    README.write_text(readme, encoding="utf-8")

    # The encoded source archive is only a bootstrap transport file.
    PAYLOAD.unlink()


if __name__ == "__main__":
    main()
