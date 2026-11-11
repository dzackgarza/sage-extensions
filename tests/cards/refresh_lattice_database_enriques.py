#!/usr/bin/env python3
"""Refresh the Enriques card digest that ``tests/cards/README.md`` describes.

The cards are the authority for the numbers the acceptance compares against, so
they are read from ``dzackgarza/lattice-database`` rather than retyped here.
This script fetches the 87 arithmetic-group cards of the 87 numerical
polarizations and lattice card ``0128`` at one database ref, keeps only the rows
the acceptance reads, and writes ``lattice-database-enriques.json`` beside it.

    python3 tests/cards/refresh_lattice_database_enriques.py --ref <database commit>

Pass ``--ref`` a full commit SHA: the digest records it, and a run whose ref is
a branch name cannot be reproduced once the branch moves.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DIGEST = HERE / "lattice-database-enriques.json"
RAW = "https://raw.githubusercontent.com/dzackgarza/lattice-database/{ref}/{path}"

# The two card paths, as the database lays them out.
ARITHMETIC_GROUP_PATH = "arithmetic-groups/{slug}.md"
LATTICE_PATH = "lattices/{tag}.md"


def fetch(ref: str, path: str) -> str:
    return subprocess.run(
        ["curl", "-sfL", "--max-time", "120", RAW.format(ref=ref, path=path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def front_matter(text: str, path: str) -> dict:
    if not text.startswith("---\n"):
        raise ValueError(f"{path} does not begin with a YAML front matter block")
    head, separator, _body = text.split("---\n", 1)[1].partition("\n---\n")
    if not separator:
        raise ValueError(f"{path} has an unterminated YAML front matter block")
    return yaml.safe_load(head)


def arithmetic_group(ref: str, slug: str) -> dict:
    path = ARITHMETIC_GROUP_PATH.format(slug=slug)
    card = front_matter(fetch(ref, path), path)
    data = card["data"]
    return {
        "tag": card["slug"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "lattice": card["lattice"],
        "parent_group": card.get("parent_group"),
        "cardinality": data["cardinality"],
        "abstract_structure": data.get("abstract_structure"),
        "line_orbits": data["line_orbits"],
        "plane_orbits": data["plane_orbits"],
        "flag_orbits": data["flag_orbits"],
        "citation": data["reference"]["citation"],
    }


def lattice_table4(ref: str, tag: str) -> dict:
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    counts = card["integral"]["polarization_counts"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "rows": {
            str(int(degree)): {
                "degree": int(degree),
                "primitive_classes": row["#h"],
                "group_classes": row["#Γ̄_h"],
                "citation": row["reference"]["citation"],
                "url": row["reference"].get("url"),
            }
            for degree, row in counts.items()
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", required=True, help="full lattice-database commit SHA")
    arguments = parser.parse_args(argv)
    ref = arguments.ref
    if len(ref) != 40 or any(character not in "0123456789abcdef" for character in ref):
        print("--ref must be a full 40-character lowercase commit SHA", file=sys.stderr)
        return 2

    groups = {
        f"gamma-h-{index}": arithmetic_group(ref, f"gamma-h-{index}")
        for index in range(1, 88)
    }
    digest = {
        "_provenance": {
            "repository": "dzackgarza/lattice-database",
            "ref": ref,
            "cards": {
                "arithmetic_group": ARITHMETIC_GROUP_PATH,
                "lattice": LATTICE_PATH,
            },
            "rows": {
                "arithmetic_group": [
                    "data.cardinality",
                    "data.abstract_structure",
                    "data.line_orbits",
                    "data.plane_orbits",
                    "data.flag_orbits",
                    "data.reference.citation",
                    "latex",
                    "lattice",
                    "parent_group",
                ],
                "lattice": "integral.polarization_counts.{degree}.{#h,#Γ̄_h,reference.citation}",
            },
            "generated_by": "tests/cards/refresh_lattice_database_enriques.py",
        },
        "arithmetic_groups": groups,
        "polarization_counts": lattice_table4(ref, "0128"),
    }
    DIGEST.write_text(json.dumps(digest, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(
        f"wrote {DIGEST} at database ref {ref}: {len(groups)} group cards, "
        f"{len(digest['polarization_counts']['rows'])} polarization-count degrees"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
