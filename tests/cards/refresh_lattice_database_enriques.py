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

# The lattice cards whose primitive-isotropic-plane rows are read: the two
# Scattone rank-21 cards, and the Enriques period lattice 029J whose two
# O(N)-orbits of primitive isotropic planes (#295, #316) are Sterk's.
PLANE_ORBIT_TAGS = ("6JRX", "6JRY", "029J")
LATTICE_PATH = "lattices/{tag}.md"

# The Coble lattice card, whose discriminant-form rows #323 reads, and the card
# of U(2) + E8(-2), whose discriminant-form order is the index of the stable
# orthogonal group #369 generates.
DISCRIMINANT_FORM_TAGS = ("6JRR", "0125")

# The Enriques period lattice card, whose 0-cusp chamber rows #312 and #285
# read: the wall count of the restricted chamber at each of Sterk's five cusps.
CUSP_CHAMBER_TAGS = ("029J",)
# The Enriques period lattice card, whose 0-cusp chamber diagrams #254 reads.
CUSP_DIAGRAM_TAGS = ("029J",)

# The card of U(2) + E8(-2), whose g-e chamber row #355 reads: the twelve
# walls and the parabolic-subdiagram orbits of the chamber of W_e ⊂ G_e.
PARABOLIC_SUBDIAGRAM_TAGS = ("0125",)

# The catalogued lattices whose primitive-orbit rows #345 reads: the hyperbolic
# plane and U + D4(-1) + A1(-1), and the positive definite A2 that the
# lattice-database certify run of #375 certifies beside the hyperbolic plane.
PRIMITIVE_ORBIT_TAGS = ("0016", "026E", "0012")

# The catalogued lattice whose certified reflection verdict #344 reads.
REFLECTIVITY_TAGS = ("0026",)


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


def plane_orbits(ref: str, tag: str) -> dict:
    """The primitive-isotropic rows of one lattice card: its planes, and its lines.

    A card's group row carries ``planes`` (the 1-dimensional cusps), ``constant``
    where it states it (the number of its 0-dimensional cusps, which are the
    primitive isotropic *lines*), and ``orbit_lengths`` where its source states the
    sizes of the plane orbits and not only how many there are.  ``029J``'s
    ``Otilde+`` row states all three -- 528 lines, 24242 planes and their split
    527 + 23715 -- and names ``Otilde^+(N)`` acting on ``N = U + U(2) + E8(-2)``
    for them (Dutour Sikirić--Hulek, arXiv:2302.01679v2, section 3.6, p. 22), so a
    line count is read from the card by tag here and the ``constant`` key is
    renamed to the ``lines`` it states, and the per-orbit lengths are kept as the
    list the card states, in its citation's order.  A row keeping only some of them
    is kept with the ones it has.
    """
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    orbits = card["integral"]["primitive_orbits"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "aliases": card.get("aliases"),
        "signature": card.get("signature"),
        "determinant": card.get("determinant"),
        "rows": {
            group: {
                **({"planes": row["planes"]} if "planes" in row else {}),
                **(
                    {"orbit_lengths": [int(length) for length in row["orbit_lengths"]]}
                    if row.get("orbit_lengths") is not None
                    else {}
                ),
                **({"lines": row["constant"]} if "constant" in row else {}),
                "citation": row["reference"]["citation"],
            }
            # A group row that states neither count is a class number stated
            # elsewhere, not an orbit row.
            for group, row in orbits.items()
            if "planes" in row or "constant" in row
        },
    }


def cusp_diagrams(ref: str, tag: str) -> dict:
    r"""The Coxeter diagram of each 0-cusp chamber of one lattice card (#254).

    ``integral.cusp_chambers.<subgroup>`` is a list of chambers, and each row's
    ``walls`` and ``diagram`` state the chamber's Coxeter diagram: the walls are
    its vertices and each ``diagram`` entry is one bond, with its Coxeter order.
    ``#312`` reads the same block for the wall counts; this projection keeps the
    diagram itself, which is what an orbit query on the cusp diagrams consumes.
    The row is read by tag, so a test names the cusp's statement number and
    never transcribes its edges.
    """
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    block = card["integral"]["cusp_chambers"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "rank": card["rank"],
        "signature": card.get("signature"),
        "certification": card["certifications"]["integral.cusp_chambers"],
        "rows": {
            subgroup: [
                {
                    "statement": row["statement"],
                    "cusp": [int(entry) for entry in row["cusp"]],
                    "printed_page": row.get("printed_page"),
                    "figure": row.get("figure"),
                    "wall_count": row["wall_count"],
                    "vertices": [wall["name"] for wall in row["walls"]],
                    # A bond's order is the Coxeter entry: a positive integer, or
                    # the element of infinite order the card writes ``inf``, kept
                    # as JSON's null so the digest stays valid JSON.
                    "edges": [
                        {
                            "left": edge["a"],
                            "right": edge["b"],
                            "order": None
                            if edge["order"] in (float("inf"), "inf")
                            else int(edge["order"]),
                        }
                        for edge in row["diagram"]
                    ],
                }
                for row in rows
            ]
            for subgroup, rows in block.items()
        },
    }


def hyperbolic_reflectivity(ref: str, tag: str) -> dict:
    r"""One card's certified ``hyperbolic.reflective`` verdict, with the lattice it is about (#344).

    ``hyperbolic.reflective`` is the card's own decision, stored when the
    preamble's Vinberg search completes, and ``certifications`` stamps it; the
    lattice is the card's ``gram_tensor``.  A test builds the lattice from the
    card and compares the edgewalk's verdict with this field rather than typing a
    verdict of its own.  The card's ``references`` block carries the source the
    database cites for the value.
    """
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    block = card["hyperbolic"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "rank": card["rank"],
        "signature": card.get("signature"),
        "determinant": card.get("determinant"),
        "gram": [[int(entry) for entry in row] for row in card["gram_tensor"]],
        "reflective": bool(block["reflective"]),
        "certification": card["certifications"]["hyperbolic.reflective"],
        "references": card.get("references"),
    }


def primitive_orbit_series(ref: str, tag: str) -> dict:
    r"""The primitive-orbit rows of one catalogued lattice card (#345).

    ``integral.primitive_orbits`` is the card's own record, for ``O``, ``SO``,
    ``Otilde``, ``SOtilde`` and their ``+`` pieces, of the orbits of primitive
    vectors by norm: ``constant`` counts the orbits of primitive isotropic lines,
    ``z`` and ``w`` the orbits of positive and negative norm inside the card's
    own bound.  The lattice is stated by the card's ``gram_tensor``, so a test
    builds the lattice from the card and compares the series' terms with the row
    rather than typing a number.
    """
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    rows = card["integral"]["primitive_orbits"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "rank": card["rank"],
        "signature": card.get("signature"),
        "determinant": card.get("determinant"),
        "gram": [[int(entry) for entry in row] for row in card["gram_tensor"]],
        "certification": card["certifications"]["integral.primitive_orbits"],
        "rows": {
            subgroup: {
                "constant": int(row["constant"]),
                "z": [int(entry) for entry in row.get("z", [])],
                "w": [int(entry) for entry in row.get("w", [])],
            }
            for subgroup, row in rows.items()
        },
    }


def discriminant_form(ref: str, tag: str) -> dict:
    """The discriminant-form rows of one lattice card.

    ``orthogonal_group_order`` is the order of `O(A_L, q_L)` on the
    discriminant form of the card's Gram tensor, ``isotropic_classes`` the
    number of classes on which `q_L` vanishes, and ``isotropic_orbits`` the
    number of `O(A_L, q_L)`-orbits among them.  The card certifies the block,
    so the digest keeps the certificate with the numbers it stamps.
    """
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    rows = card["integral"]["discriminant_form"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "rank": card["rank"],
        "signature": card.get("signature"),
        "determinant": card.get("determinant"),
        "certification": card["certifications"]["integral.discriminant_form"],
        "orthogonal_group_order": rows["orthogonal_group_order"],
        "isotropic_classes": rows["isotropic_classes"],
        "isotropic_orbits": rows["isotropic_orbits"],
    }


def cusp_chambers(ref: str, tag: str) -> dict:
    """The 0-cusp chamber rows of one lattice card (#312, #285).

    ``integral.cusp_chambers.<subgroup>`` is a list of chambers: the cusp (the
    primitive isotropic vector, in the card's Gram coordinates), the paper's
    statement number for that diagram, the printed page and figure, and the
    walls as named root vectors with their number.  The row is what a chamber
    computation is compared with (#297), by tag and by cusp vector, so the
    number is never transcribed into a test.
    """
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    block = card["integral"]["cusp_chambers"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "rank": card["rank"],
        "signature": card.get("signature"),
        "certification": card["certifications"]["integral.cusp_chambers"],
        "rows": {
            subgroup: [
                {
                    "statement": row["statement"],
                    "cusp": row["cusp"],
                    "walls": row["wall_count"],
                    "printed_page": row.get("printed_page"),
                    "figure": row.get("figure"),
                }
                for row in rows
            ]
            for subgroup, rows in block.items()
        },
    }


def parabolic_subdiagrams(ref: str, tag: str) -> dict:
    """The subgroup chamber rows with their parabolic-subdiagram orbits (#355).

    ``integral.cusp_chambers.<subgroup>`` is a list of chambers, and a row keyed
    by a subgroup slug -- not one of the eight standard subgroups -- carries that
    subgroup's chamber with its walls as vectors and its maximal parabolic
    subdiagrams given as orbits modulo the subgroup's symmetries.  This
    projection keeps the walls, the orbits and the lattice's own Gram tensor,
    which is what the parabolic-subdiagram call's acceptance compares with; the
    wall count and the diagram itself stay in the cusp-chamber sections.  A row
    that states no ``parabolic_orbits`` is a computed chamber of the full
    reflection group and cites no source, so only the rows that state them are
    kept, by subgroup.
    """
    path = LATTICE_PATH.format(tag=tag)
    card = front_matter(fetch(ref, path), path)
    block = card["integral"]["cusp_chambers"]
    return {
        "tag": card["tag"],
        "path": path,
        "name": card["name"],
        "latex": card["latex"],
        "rank": card["rank"],
        "signature": card.get("signature"),
        "gram": [[int(entry) for entry in row] for row in card["gram_tensor"]],
        "certification": card["certifications"]["integral.cusp_chambers"],
        "rows": {
            subgroup: [
                {
                    "statement": row["statement"],
                    "printed_page": row.get("printed_page"),
                    "figure": row.get("figure"),
                    "wall_count": row["wall_count"],
                    "walls": [
                        [int(entry) for entry in wall["vector"]]
                        for wall in row["walls"]
                    ],
                    "parabolic_orbits": [
                        [list(subdiagram) for subdiagram in orbit["subdiagrams"]]
                        for orbit in row["parabolic_orbits"]
                    ],
                }
                for row in rows
            ]
            for subgroup, rows in block.items()
            if all("parabolic_orbits" in row for row in rows)
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
                "plane_orbits": "integral.primitive_orbits.{group}.planes and .orbit_lengths(per-orbit sizes) and .constant(the line count),reference.citation",
                "cusp_chambers": "integral.cusp_chambers.{subgroup}.{cusp,statement,wall_count,printed_page,figure},certifications.integral.cusp_chambers",
                "discriminant_form": "integral.discriminant_form.{orthogonal_group_order,isotropic_classes,isotropic_orbits},certifications.integral.discriminant_form",
                "cusp_diagrams": "integral.cusp_chambers.{subgroup}.{statement,cusp,walls,diagram,printed_page,figure},certifications.integral.cusp_chambers",
                "parabolic_subdiagrams": "gram_tensor,integral.cusp_chambers.{subgroup}.{walls,parabolic_orbits,statement,wall_count,printed_page,figure},certifications.integral.cusp_chambers",
                "primitive_orbit_series": "gram_tensor,integral.primitive_orbits.{subgroup}.{constant,z,w},certifications.integral.primitive_orbits",
                "hyperbolic_reflectivity": "gram_tensor,hyperbolic.reflective,certifications.hyperbolic.reflective,references",
            },
            "generated_by": "tests/cards/refresh_lattice_database_enriques.py",
        },
        "arithmetic_groups": groups,
        "polarization_counts": lattice_table4(ref, "0128"),
        "plane_orbits": {tag: plane_orbits(ref, tag) for tag in PLANE_ORBIT_TAGS},
        "discriminant_forms": {tag: discriminant_form(ref, tag) for tag in DISCRIMINANT_FORM_TAGS},
        "cusp_chambers": {tag: cusp_chambers(ref, tag) for tag in CUSP_CHAMBER_TAGS},
        "cusp_diagrams": {tag: cusp_diagrams(ref, tag) for tag in CUSP_DIAGRAM_TAGS},
        "parabolic_subdiagrams": {tag: parabolic_subdiagrams(ref, tag) for tag in PARABOLIC_SUBDIAGRAM_TAGS},
        "primitive_orbit_series": {tag: primitive_orbit_series(ref, tag) for tag in PRIMITIVE_ORBIT_TAGS},
        "hyperbolic_reflectivity": {tag: hyperbolic_reflectivity(ref, tag) for tag in REFLECTIVITY_TAGS},
    }
    DIGEST.write_text(json.dumps(digest, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(
        f"wrote {DIGEST} at database ref {ref}: {len(groups)} group cards, "
        f"{len(digest['polarization_counts']['rows'])} polarization-count degrees, "
        f"{len(digest['discriminant_forms'])} discriminant forms, "
        f"{sum(len(rows) for card in digest['cusp_chambers'].values() for rows in card['rows'].values())} cusp chambers",
        f"{sum(len(rows) for card in digest['cusp_diagrams'].values() for rows in card['rows'].values())} cusp diagrams, "
        f"{len(digest['primitive_orbit_series'])} primitive-orbit cards, "
        f"{len(digest['hyperbolic_reflectivity'])} reflectivity cards"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
