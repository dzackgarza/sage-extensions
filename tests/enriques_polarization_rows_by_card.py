r"""The 87 numerical polarizations and cart 0128's Table 4 rows, against their cards.

This is the acceptance entry point of #319: the verification half of #286.  It
is not collected by pytest (its file name does not begin with ``test_``), because
every row builds an arithmetic subgroup of $O(N)$ for the Enriques period
lattice and calls the public orbit classifier on it; the rows are long by
construction and belong in the CI job ``enriques-polarization-rows`` that
reports later, not in the per-test gate.

    sage -python tests/enriques_polarization_rows_by_card.py            # every row
    sage -python tests/enriques_polarization_rows_by_card.py --tags gamma-h-1
    sage -python tests/enriques_polarization_rows_by_card.py --degrees 2,4,6
    sage -python tests/enriques_polarization_rows_by_card.py --budget 18000

The rows are the cards' ``tests/cards/lattice-database-enriques.json``, read
from ``dzackgarza/lattice-database`` at database commit
``587d56febe5856d54c6bc9fc023fa5a425f76bfb`` by
``tests/cards/refresh_lattice_database_enriques.py``.  Every expected value is
that file's, with the card's own citation naming the paper, its table and page
of the version read:

* the 87 arithmetic-group cards ``gamma-h-1`` .. ``gamma-h-87`` state
  ``#I_1``, ``#I_2``, ``#I_12`` -- the numbers of orbits of isotropic lines,
  planes and flags in $N$ under $\Gamma^+_h$ -- from D. Dutour Sikirić and
  K. Hulek, *Moduli of polarised Enriques surfaces -- computational aspects*,
  J. London Math. Soc. 110 (2024), arXiv:2302.01679v2 (26 Sep 2023), Table 1,
  p. 13 (cards 1-41) and Table 2, p. 14 (cards 42-87).
* lattice card ``0128`` ($U \oplus E_8(-1)$, the Enriques lattice $M(1/2)$)
  states, per degree $2d = 2, \dots, 72$, ``#h`` -- the number of
  $O(M(1/2))$-orbits of primitive vectors of square $2d$ -- and ``#\bar\Gamma_h``
  -- the number of conjugacy classes of groups $\bar\Gamma_h$ occurring in that
  degree -- from the same paper, Table 4, p. 17.

What is compared, and through which public call of #286:

* a ``gamma-h-N`` row is built as its card states it -- the card names the
  lattice (``029J``, $N = U \oplus U(2) \oplus E_8(-2)$) and the parent group
  (``o-t-en``, $O(N)$), and its LaTeX names the subset $S$ of the Coxeter
  diagram of $O(U \oplus E_8(-1))$ that $h$ is orthogonal to -- and the three
  counts are ``group.isotropic_orbit_representatives(1)``,
  ``(2)`` and ``(2, flag=True)``, the public call of #286
  (``PredicateSubgroups.isotropic_orbit_representatives``, with ``cusps`` and
  ``tits_building_incidence`` built on it).
* a ``0128`` row's ``#h`` is ``L.Aut().vector_orbit_representatives(2d)`` on the
  card's own lattice, the same public orbit classifier restricted to the
  group of the card being read, and its ``#\bar\Gamma_h`` is the number of
  distinct line/plane/flag triples the call returns over those classes: the
  paper's own class invariant is the order and the orbit sizes of the group
  (p. 11), and the orbit sizes are what the call reports.

A row passes only when the call's numbers equal the card's.  A row whose call
does not return inside the per-call cap is reported ``UNDECIDED`` with the cap
and the stage that ran out -- that is not a pass and the run is red.  A
mismatch prints a defect block naming the lattice, the group, the row and the
citation, ready to be filed against this repository; nothing here repairs the
call and no expected value is adjusted.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import sys
import time
from pathlib import Path

from sage_extensions.all import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parents[1]
DIGEST_PATH = ROOT / "tests" / "cards" / "lattice-database-enriques.json"

# D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, equation (7), p. 9: the
# Gram matrix of the extreme-ray generators g_1, ..., g_10, a Z-basis of
# U + E_8(-1), the lattice of card 0128.  Species (6) of the same page is the
# paper's other normalization; W is unimodular of signature (1, 9).
W_ROWS = (
    (0, 1, 2, 2, 3, 3, 4, 4, 5, 6),
    (1, 2, 4, 4, 6, 6, 8, 8, 10, 12),
    (2, 4, 4, 6, 7, 8, 9, 10, 12, 14),
    (2, 4, 6, 6, 9, 9, 12, 12, 15, 18),
    (3, 6, 7, 9, 10, 12, 14, 15, 18, 21),
    (3, 6, 8, 9, 12, 12, 16, 16, 20, 24),
    (4, 8, 9, 12, 14, 16, 18, 20, 24, 28),
    (4, 8, 10, 12, 15, 16, 20, 20, 25, 30),
    (5, 10, 12, 15, 18, 20, 24, 25, 30, 36),
    (6, 12, 14, 18, 21, 24, 28, 30, 36, 42),
)

WALL_INDICES = tuple(range(1, 11))

# The source's node labels for the ten basis vectors, fixed against Table 3 and
# used by tests/lattices/test_enriques_polarization_orbits.sage (case 1 {0} ->
# g_2, case 3 {7} -> g_3, ..., case 5 {-1,7} -> g_1 + g_3).
NODE_TO_WALL = {-1: 1, 0: 2, 1: 4, 2: 6, 3: 8, 4: 9, 5: 10, 6: 7, 7: 3, 8: 5}

# The card's stated lattice and parent group; a card naming anything else is a
# card this runner cannot build, and it says so instead of substituting.
ENRIQUES_LATTICE_TAG = "029J"
ENRIQUES_PARENT_GROUP = "o-t-en"


class RowUndecided(Exception):
    """A call did not return inside the per-call cap."""


def _alarm(signum, frame):
    raise RowUndecided


signal.signal(signal.SIGALRM, _alarm)


def log(message=""):
    print(message, flush=True)


def card_subset(latex):
    r"""Return ``(nodes, barred)`` for the subset factor of a card's LaTeX name.

    A card writes $\overline{\Gamma}_{h,N}(\overline{\{0\}})$ when the printed
    subset is the complement of the generating set, and
    $\overline{\Gamma}_{h,N}(\{4, 6, 3, 5\})$ when the subset itself is the
    generating set (the paper's convention, p. 12); the card's own LaTeX carries
    that bar, so the decode reads it rather than inferring it from the size.
    """
    opening = latex.rfind("(")
    closing = latex.rfind(")")
    if opening < 0 or closing < opening:
        raise ValueError(f"the card's LaTeX names no subset: {latex}")
    text = latex[opening + 1 : closing]
    barred = "overline" in text
    # The node labels are the only integers in the factor; \emptyset has none.
    return tuple(int(part) for part in re.findall(r"-?\d+", text)), barred


def support(nodes, barred):
    """Return the $g$-basis support Table 3 / the card's set denotes."""
    walls = tuple(NODE_TO_WALL[node] for node in nodes)
    if barred:
        return tuple(sorted(walls))
    return tuple(wall for wall in WALL_INDICES if wall not in walls)


def describe_subset(nodes, barred):
    printed = "{" + ",".join(str(node) for node in nodes) + "}"
    return f"overline{printed}" if barred else printed


def orbit_rows(group, cap):
    """Return the card's three rows -- lines, planes, flags -- from the public call."""
    rows = []
    for label, rank, flag in (("lines", 1, False), ("planes", 2, False), ("flags", 2, True)):
        started = time.time()
        signal.alarm(cap)
        try:
            count = group.isotropic_orbit_representatives(rank, flag=flag).cardinality()
            signal.alarm(0)
        except RowUndecided:
            raise RowUndecided(
                f"{label}: the public call did not return inside {cap} s "
                f"({time.time() - started:.0f} s elapsed)"
            )
        finally:
            signal.alarm(0)
        rows.append((int(count), time.time() - started))
    return tuple(rows)


class Enriques:
    r"""The card's lattice, its polarization lattice, and the $\Gamma_h$ construction."""

    def __init__(self):
        self.invariant = Involutions.I_En.invariant_lattice()
        # The card's own lattice M(1/2) = U + E8(-1) is W; M = U(2) + E8(-2) is
        # 2W on the same coordinates, and the invariant lattice is isometric to
        # it.  The doubling multiplies every square by two, which is the source's
        # own normalization: a polarization of degree h^2 = 2d is a vector of
        # square 2d in M(1/2) and of square 4d in M.
        self.unimodular = Lattices(ZZ)([list(row) for row in W_ROWS])
        self.doubled = Lattices(ZZ)([[2 * entry for entry in row] for row in W_ROWS])
        self.transport = self.doubled.isometry_to(self.invariant)
        self.labels = tuple(self.doubled.module_generating_set())
        self.ambient = Involutions.I_En.formed_coinvariants()
        if self.unimodular.determinant() != ZZ(-1):
            raise ArithmeticError("W is not unimodular")
        if self.ambient.determinant() != ZZ(1024):
            raise ArithmeticError("the anti-invariant lattice is not the determinant-1024 T_En")
        if not self.ambient.is_isometric(NamedLattices.TEn):
            raise ArithmeticError("the anti-invariant lattice is not T_En")

    def doubled_point(self, support_indices):
        """The polarization supported on the card's $g$-basis subset."""
        return sum(
            (self.doubled.module_generator(self.labels[index - 1]) for index in support_indices),
            self.doubled.zero(),
        )

    def doubled_from_unimodular(self, vector):
        """The same coordinate vector read in M = 2W, where its square doubles."""
        coordinates = vector.to_vector()
        source_labels = tuple(self.unimodular.module_generating_set())
        target_labels = tuple(self.doubled.module_generating_set())
        image = sum(
            (
                self.doubled.scalar_multiple(
                    coordinates(source_label), self.doubled.module_generator(target_label)
                )
                for source_label, target_label in zip(source_labels, target_labels, strict=True)
            ),
            self.doubled.zero(),
        )
        if image.q() != ZZ(2) * vector.q():
            raise ArithmeticError(
                f"the coordinate transfer took square {vector.q()} to {image.q()}, not twice it"
            )
        return image

    def group(self, vector_of_doubled):
        r"""$\Gamma_h$ of the card: the image of $O(M, h)$, transported, preimage in $O(N)$."""
        vector_in_M = self.transport(vector_of_doubled)
        return Involutions.I_En.polarized(
            self.invariant.inclusion()(vector_in_M)
        ).coinvariant_extension_subgroup()


def report_card_row(orthogonal, card, cap):
    """Compare one ``gamma-h-N`` card with the public call on the group it names."""
    tag = card["tag"]
    label = f"{tag}"
    log("")
    log(f"ROW {label}  ({card['name']})")
    log(f"  citation: {card['citation']}")
    if card["lattice"] != ENRIQUES_LATTICE_TAG:
        log(f"  UNDECIDED: the card names lattice {card['lattice']}, not {ENRIQUES_LATTICE_TAG}")
        return "undecided", None
    if card["parent_group"] != ENRIQUES_PARENT_GROUP:
        log(f"  UNDECIDED: the card names parent group {card['parent_group']}, not {ENRIQUES_PARENT_GROUP}")
        return "undecided", None
    nodes, barred = card_subset(card["latex"])
    indices = support(nodes, barred)
    log(f"  group: S = {describe_subset(nodes, barred)}, h = sum of g_{{{','.join(map(str, indices))}}}, "
        f"|Gamma-bar_h| = {card['cardinality']}")
    expected = (card["line_orbits"], card["plane_orbits"], card["flag_orbits"])
    started = time.time()
    try:
        group = orthogonal.group(orthogonal.doubled_point(indices))
        rows = orbit_rows(group, cap)
    except RowUndecided as undecided:
        log(f"  UNDECIDED: {undecided} (after {time.time() - started:.0f} s)")
        return "undecided", None
    got = tuple(count for count, _elapsed in rows)
    timings = ", ".join(f"{elapsed:.0f} s" for _count, elapsed in rows)
    log(f"  expected lines/planes/flags = {expected[0]}/{expected[1]}/{expected[2]}")
    log(f"  call     lines/planes/flags = {got[0]}/{got[1]}/{got[2]}   ({timings})")
    if got == expected:
        log(f"  PASS (row total {time.time() - started:.0f} s)")
        return "pass", None
    log(f"  FAIL (row total {time.time() - started:.0f} s)")
    defect = {
        "card": tag,
        "lattice": card["lattice"],
        "group": f"{card['name']}, S = {describe_subset(nodes, barred)}, |Gamma-bar_h| = {card['cardinality']}",
        "expected": f"lines/planes/flags = {expected[0]}/{expected[1]}/{expected[2]}",
        "actual": f"lines/planes/flags = {got[0]}/{got[1]}/{got[2]}",
        "citation": card["citation"],
    }
    return "fail", defect


def report_table4_row(orthogonal, lattice_card, degree, cap):
    """Compare one degree row of card 0128's Table 4 with the public call."""
    row = lattice_card["rows"][str(degree)]
    log("")
    log(f"ROW 0128 degree={degree} (genus {degree // 2})")
    log(f"  citation: {row['citation']}")
    started = time.time()

    # h^2 = 2d in M(1/2) is square 2 * (2d) in M = 2W.
    signal.alarm(cap)
    try:
        classes = orthogonal.unimodular.Aut().vector_orbit_representatives(degree)
        signal.alarm(0)
        counts = int(classes.cardinality())
    except RowUndecided:
        signal.alarm(0)
        log(f"  UNDECIDED #h: the vector orbit call did not return inside {cap} s")
        return "undecided", None
    finally:
        signal.alarm(0)
    expected_counts = int(row["primitive_classes"])
    log(f"  #h: expected {expected_counts}, call {counts}   ({time.time() - started:.0f} s)")
    outcome = "pass" if counts == expected_counts else "fail"
    defect = None
    if outcome == "fail":
        defect = {
            "card": "0128",
            "lattice": "0128 (U + E8(-1), rank 10, unimodular, signature (1, 9))",
            "group": "O(U + E8(-1))",
            "expected": f"#h = {expected_counts} at degree {degree}",
            "actual": f"#h = {counts}",
            "citation": row["citation"],
        }

    triples = []
    representatives = tuple(classes)
    for index, representative in enumerate(representatives):
        log(f"  class {index + 1}/{len(representatives)}: q = {representative.q()}")
        try:
            group = orthogonal.group(orthogonal.doubled_from_unimodular(representative))
            rows = orbit_rows(group, cap)
        except RowUndecided as undecided:
            log(f"  UNDECIDED #Gamma-bar_h: {undecided} (after {time.time() - started:.0f} s)")
            return "undecided", defect
        triples.append(tuple(count for count, _elapsed in rows))
        log(f"    lines/planes/flags = {'/'.join(str(count) for count in triples[-1])}")
    distinct = len(set(triples))
    expected_distinct = int(row["group_classes"])
    log(f"  #Gamma-bar_h: expected {expected_distinct}, call {distinct}   "
        f"({time.time() - started:.0f} s)")
    if distinct != expected_distinct:
        outcome = "fail"
        defect = {
            "card": "0128",
            "lattice": "0128 (U + E8(-1), rank 10, unimodular, signature (1, 9))",
            "group": f"the {counts} classes of primitive vectors of square {degree}",
            "expected": f"#Gamma-bar_h = {expected_distinct} at degree {degree}",
            "actual": f"#Gamma-bar_h = {distinct} from the triples {sorted(set(triples))}",
            "citation": row["citation"],
        }
    log(f"  {'PASS' if outcome == 'pass' else 'FAIL'} (row total {time.time() - started:.0f} s)")
    return outcome, defect


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tags", default=None, help="comma-separated gamma-h-N cards")
    parser.add_argument("--degrees", default=None, help="comma-separated degrees 2d of card 0128")
    parser.add_argument("--cap", type=int, default=int(os.environ.get("ENRIQUES_CALL_CAP", "1800")),
                        help="seconds one public call may take before its row is undecided")
    parser.add_argument("--budget", type=int, default=int(os.environ.get("ENRIQUES_ROW_BUDGET", "0")),
                        help="seconds for the whole run; 0 runs every selected row")
    arguments = parser.parse_args(argv)

    digest = json.loads(DIGEST_PATH.read_text())
    provenance = digest["_provenance"]
    log(f"cards: {provenance['repository']} at {provenance['ref']}")
    log(f"replica of the paper read: arXiv:2302.01679v2 (26 Sep 2023), Tables 1 and 2 pp. 13-14, Table 4 p. 17")
    log(f"per-call cap {arguments.cap} s, budget {arguments.budget or 'unbounded'} s")

    tags = (
        arguments.tags.split(",")
        if arguments.tags and arguments.tags != "none"
        else []
        if arguments.tags == "none"
        else sorted(digest["arithmetic_groups"], key=lambda tag: int(tag.rsplit("-", 1)[1]))
    )
    degrees = (
        [] if arguments.degrees == "none"
        else [int(degree) for degree in arguments.degrees.split(",")]
        if arguments.degrees
        else sorted(int(degree) for degree in digest["polarization_counts"]["rows"])
    )

    orthogonal = Enriques()
    log(f"lattice {ENRIQUES_LATTICE_TAG} is T_En: rank {orthogonal.ambient.module_rank()}, "
        f"determinant {orthogonal.ambient.determinant()}")

    deadline = time.time() + arguments.budget if arguments.budget else None
    outcomes = {"pass": [], "fail": [], "undecided": [], "notreached": []}
    defects = []

    for tag in tags:
        if deadline is not None and time.time() > deadline:
            outcomes["notreached"].append(tag)
            continue
        outcome, defect = report_card_row(orthogonal, digest["arithmetic_groups"][tag], arguments.cap)
        outcomes[outcome].append(tag)
        if defect is not None:
            defects.append(defect)

    lattice_card = digest["polarization_counts"]
    for degree in degrees:
        if deadline is not None and time.time() > deadline:
            outcomes["notreached"].append(f"0128 degree {degree}")
            continue
        outcome, defect = report_table4_row(orthogonal, lattice_card, degree, arguments.cap)
        outcomes[outcome].append(f"0128 degree {degree}")
        if defect is not None:
            defects.append(defect)

    log("")
    log("SUMMARY")
    for name in ("pass", "fail", "undecided", "notreached"):
        log(f"  {name}: {len(outcomes[name])}")
        for row in outcomes[name]:
            log(f"    {row}")
    for defect in defects:
        log("")
        log("DEFECT")
        for key in ("card", "lattice", "group", "expected", "actual", "citation"):
            log(f"  {key}: {defect[key]}")
    if outcomes["fail"] or outcomes["undecided"] or outcomes["notreached"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
