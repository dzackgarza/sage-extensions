r"""Every Enriques and K3 orbit row of the known families, against the card that states it.

This is the acceptance entry point of #319: the verification half of #286.  It is
not collected by pytest -- its file name does not begin with ``test_`` -- because
each row builds an arithmetic group of an indefinite lattice and calls the public
isotropic-orbit classifier on it, and the rows are minutes or hours each.  The
whole module is one matrix of CI jobs that reports later
(``.github/workflows/enriques-polarization-rows-full.yml``), never the per-test
gate.

    python3 tests/enriques_polarization_rows_by_card.py                 # every row
    python3 tests/enriques_polarization_rows_by_card.py --tags 6JRX --rows planes
    python3 tests/enriques_polarization_rows_by_card.py --one 029J:gamma-en-2:planes
    python3 tests/enriques_polarization_rows_by_card.py --budget 18000

**Every expected value is a card's, read by tag.**  The rows live in
``tests/cards/lattice-database-enriques.json``, generated from
``dzackgarza/lattice-database`` at the database commit its ``_provenance.ref``
names by ``tests/cards/refresh_lattice_database_enriques.py``, and are read through
``sage_extensions.lattice_database`` -- ``card_line_orbit_row``,
``card_plane_orbit_row``, ``card_arithmetic_group_row``, ``card_polarization_row``.
No expected number is typed in this file, and no row is skipped: the module
enumerates every row it knows, and a row whose card states nothing is reported as
such rather than compared against an invented value.

**The rows, and the numbered statement of each.**  A row is named by the paper
and the table, proposition, theorem, corollary, lemma or section the card cites for
it, with the page references stripped: a row names its paper and its numbered
statement, not a page.

* card ``029J`` -- $N = U \oplus U(2) \oplus E_8(-2)$, the Enriques period
  lattice, with rows ``O``, ``Otilde+`` and ``gamma-en-2``: H. Sterk,
  *Compactifications of the period space of Enriques surfaces, Part I*,
  Math. Z. 207 (1991), Propositions 4.5 and 4.6 (the two $O(N)$-orbits of
  primitive isotropic lines and of planes) and Proposition 4.2.3 with
  Remark 4.2.4 ($\Gamma_{\mathrm{En},2}$'s five $0$-cusps); D. Dutour Sikirić,
  K. Hulek, *Moduli of polarised Enriques surfaces -- computational aspects*,
  J. London Math. Soc. 110 (2024), arXiv:2302.01679, Section 3.6 (the Tits
  building); V. Alexeev, P. Engel, D. Z. Garza, L. Schaffler, *Compact moduli of
  Enriques surfaces of degree 2*, Nagoya Math. J. 259 (2025), Definitions 2.6 and
  2.7 with Corollary 3.12 and Section 3.3.
* card ``otilde-plus-t-en`` -- the arithmetic group
  $\widetilde O^+(T_{\mathrm{En}})$, same two rows, same Section 3.6 statement.
* cards ``6JRX`` and ``6JRY`` -- Scattone's degree-two and degree-four period
  lattices $\Lambda_2$ and $\Lambda_4$, rows ``O``, ``O+`` and ``Otilde+``:
  J. Scattone, *On the compactification of moduli spaces for algebraic K3
  surfaces*, Mem. Amer. Math. Soc. 374 (1987), Proposition 5.4.7 with
  Corollary 5.4.8(2) and Sections 6.2 and 6.3 (the plane rows), Section 6 (the
  $O^+$ rows) and Theorem 4.0.1 (the $\widetilde O^+$ rows).
* cards ``gamma-h-1`` .. ``gamma-h-87`` -- the 87 numerical polarizations, rows
  ``lines``, ``planes`` and ``flags``, each from Table 1 or Table 2 of Dutour
  Sikirić--Hulek as the card itself cites it.
* card ``0128`` -- $U \oplus E_8(-1)$, Table 4 rows: ``#h``, the number of
  orbits of primitive vectors of square $2d$ under $O(U \oplus E_8(-1))$, and
  ``#Γ̄_h``, the number of classes of polarizing groups occurring there.

**What each row is compared with.**  The public call of #286, on the lattice and
group the row names:

* ``lines``: ``group.isotropic_orbit_representatives(1).cardinality()``;
* ``planes``: ``group.isotropic_plane_orbits(representatives).cardinality()``
  where the group is a proper subgroup of the Enriques lattice's orthogonal
  group -- Sterk's two representatives are the argument -- and
  ``group.isotropic_orbit_representatives(2).cardinality()`` otherwise;
* ``flags``: ``group.isotropic_orbit_representatives(2, flag=True).cardinality()``;
* ``#h``: ``W.Aut().vector_orbit_representatives(2d, content=1).cardinality()`` --
  the orbits of *primitive* vectors of square $2d$, which is what Table 4's first
  line states (Section 3.4), the source having fixed the primitivity of ``h`` in
  Section 2, the paragraph introducing (3).  The square-$2d$ shell of $W$ carries,
  besides those, the classes $c \cdot w$ of every content $c > 1$ with
  $c^2 \mid 2d$ and $w$ primitive of square $2d/c^2$; an isometry preserves
  content, so they are $O(W)$-classes of their own.  They are numerical
  polarizations in the source's sense and the source disregards them: comparing
  its list with [CDGK, Appendix], "the list of [CDGK, Appendix] also contains
  nonprimitive numerical polarizations, which we disregard in our approach since
  they do not lead to new moduli spaces" (Section 3.5).  Table 4 counts the
  primitive classes, so this row does too.
* ``#Γ̄_h``: the number of distinct line/plane/flag triples the call returns over
  the ``#h`` classes.  A triple of orbit counts is an invariant of the group, so
  the computed number is at most the card's; a degree where it is smaller says the
  three counts did not separate that degree's classes, and which of the two values
  is right there is decided by proof, as the issue's acceptance requires.

**The `#h` rows are the guard that keeps this reading.**  Dropping the stratum is a
one-argument change in this file, and nothing else in the repository fails when it is
made: `tests/lattices/test_the_enriques_polarization_degrees_by_card.py` is a
library-level test -- it imports only the session and calls `NamedLattices.E10.Aut()`
itself -- so it cannot see this module's row and is not this guard.  The guard is the
scheduled `0128:#h` row: every degree of the card is in `_rows()`, the row fails when
the stratum is dropped (`#h: expected 2, call 3` at degree 8), and the image job
`enriques-polarization-rows` runs it.

**A row that does not decide is not a pass.**  Each row runs in a child process of
its own, so a row that hangs or that grows past the machine's memory is reported as
that row's outcome instead of taking the run's report with it; the report says
which rows returned, which did not return inside ``--cap``, which died, and which
the run's ``--budget`` never reached.  A row whose card states no such value is
reported ``MISSING``, naming the card.  Any outcome other than ``PASS`` makes the
run exit non-zero, and a row that disagrees with its card is printed as a ``DEFECT``
block naming the lattice, the group, the expected value, the computed value and the
card's citation, ready to be filed as an issue against this repository.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass

from sage_extensions.all import *  # noqa: F401,F403

#: D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, equation (7): the Gram
#: matrix of the extreme-ray generators $g_1, \ldots, g_{10}$, a $\mathbb{Z}$-basis
#: of $U \oplus E_8(-1)$, the lattice of card ``0128``.  A construction datum: the
#: acceptance's expected values are the cards', and this matrix is what the card's
#: lattice is built from.
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

#: The source's node labels for the ten basis vectors of the diagram, fixed
#: against Table 3 of the paper and used by the 87 polarization rows.
NODE_TO_WALL = {-1: 1, 0: 2, 1: 4, 2: 6, 3: 8, 4: 9, 5: 10, 6: 7, 7: 3, 8: 5}

#: The card of the Enriques period lattice and the parent group it names; a card
#: that names anything else is a card this module cannot build, and it says so.
ENRIQUES_LATTICE_TAG = "029J"
ENRIQUES_PARENT_GROUP = "o-t-en"

#: The card of $O(U \oplus E_8(-1))$'s Table 4.
TABLE4_TAG = "0128"

#: A page reference in a card's citation, which a row does not name.
_PAGE_REFERENCES = (
    re.compile(r"\(\s*pp?\.\s*\d+(?:\s*[-\u2013]\s*\d+)?\s*\)"),
    re.compile(r",?\s*\bpp?\.\s*\d+(?:\s*[-\u2013]\s*\d+)?(?!\d)"),
)

#: A numbered statement: the word and the number that follows it.
_NUMBERED_STATEMENT = re.compile(
    r"\b(?:Table|Proposition|Theorem|Corollary|Lemma|Section|Definition|Remark)\s+\d"
)

#: The line the child process writes its outcome on.
_OUTCOME_PREFIX = "@@ROW@@ "

#: What a child's failure to write an outcome may cost beyond the row's own cap:
#: the interpreter starts, imports the library and builds nothing.
_STARTUP_ALLOWANCE = 180


@dataclass(frozen=True)
class Row:
    r"""One row of one card: which group, which quantity, and (for 0128) the degree."""

    card: str
    group: str
    quantity: str
    degree: int = 0

    def identifier(self) -> str:
        r"""The row's name in this module, which its selection and its report use."""
        if self.card == TABLE4_TAG:
            return f"{self.card}:{self.quantity}:{self.degree}"
        if self.group:
            return f"{self.card}:{self.group}:{self.quantity}"
        return f"{self.card}:{self.quantity}"


def _rows() -> tuple:
    r"""Every row this module compares, in report order.

    The 87 polarizations and card ``0128``'s degrees are enumerated from the
    digest, so a card that gains or loses a row changes the run rather than this
    file.
    """
    rows = []
    for group in ("O", "Otilde+", "gamma-en-2"):
        for quantity in ("lines", "planes"):
            rows.append(Row(ENRIQUES_LATTICE_TAG, group, quantity))
    for quantity in ("lines", "planes"):
        rows.append(Row("otilde-plus-t-en", "", quantity))
    for tag in ("6JRX", "6JRY"):
        for group, quantity in (
            ("O", "planes"),
            ("O+", "lines"),
            ("O+", "planes"),
            ("Otilde+", "lines"),
        ):
            rows.append(Row(tag, group, quantity))
    for tag in card_arithmetic_group_tags():
        if not tag.startswith("gamma-h-"):
            continue
        for quantity in ("lines", "planes", "flags"):
            rows.append(Row(tag, "", quantity))
    for degree in card_polarization_degrees():
        for quantity in ("#h", "#Gamma_h"):
            rows.append(Row(TABLE4_TAG, "", quantity, degree))
    return tuple(rows)


def _select(rows, tags, degrees, quantities):
    r"""The rows a run asks for: by card, by degree and by quantity, or all of them."""
    selected = []
    for row in rows:
        if tags and row.card not in tags:
            continue
        if degrees and (row.card != TABLE4_TAG or row.degree not in degrees):
            continue
        if quantities and row.quantity not in quantities:
            continue
        selected.append(row)
    return tuple(selected)


def _statement(citation: str) -> str:
    r"""The card's citation with its page references removed.

    A row names its paper and its numbered table or statement, not a page: the two
    readings are checked here rather than assumed, because a citation that stops
    naming a numbered statement has stopped saying which statement the row is.
    """
    trimmed = citation
    for pattern in _PAGE_REFERENCES:
        trimmed = pattern.sub("", trimmed)
    stripped = re.sub(r"\s+", " ", trimmed).replace(" .", ".").strip()
    if re.search(r"\bpp?\.\s*\d", stripped):
        raise ValueError(f"a page reference survives in {stripped!r}")
    if _NUMBERED_STATEMENT.search(stripped) is None:
        raise ValueError(
            f"the citation {stripped!r} names no numbered table, proposition, theorem, "
            "corollary, lemma, section, definition or remark"
        )
    return stripped


class CardMissing(Exception):
    r"""The card states no such row, or the digest carries no such card."""


def _expected(row: Row):
    r"""The card's own value for ``row``, or :class:`CardMissing` if it states none."""
    try:
        if row.card == TABLE4_TAG:
            entry = card_polarization_row(row.degree)
            return entry["primitive_classes" if row.quantity == "#h" else "group_classes"]
        if row.card.startswith("gamma-h-") or row.card == "otilde-plus-t-en":
            return card_arithmetic_group_row(row.card, row.quantity)
        read = card_line_orbit_row if row.quantity == "lines" else card_plane_orbit_row
        return read(row.card, row.group)
    except KeyError as missing:
        raise CardMissing(str(missing)) from None


def _citation(row: Row) -> str:
    r"""The card's citation for ``row``: its paper, with the numbered statement."""
    if row.card == TABLE4_TAG:
        return card_polarization_row(row.degree)["citation"]
    if row.card.startswith("gamma-h-") or row.card == "otilde-plus-t-en":
        return card_arithmetic_group(row.card)["citation"]
    return card_lattice(row.card)["rows"][row.group]["citation"]


def _card_lattice(tag: str):
    r"""The lattice card ``tag`` describes, built from the decomposition it states.

    The Enriques period lattice is the catalogue's ``T_En``; Scattone's period
    lattices are $U^2 \oplus E_8(-1)^2 \oplus \langle -2k \rangle$ with $2k$ read
    off the card's own determinant.  The two invariants the card states -- its
    signature and its determinant -- are what the built lattice is checked against,
    so a lattice that is not the card's is refused rather than compared.
    """
    card = card_lattice(tag)
    if tag == ENRIQUES_LATTICE_TAG:
        lattice = NamedLattices.TEn
    else:
        determinant = int(card["determinant"])
        if determinant % 2:
            raise ArithmeticError(f"card {tag} states determinant {determinant}, not twice an integer")
        lattice = (
            Lattices(ZZ)("U")
            + Lattices(ZZ)("U")
            + Lattices(ZZ)("E8")
            + Lattices(ZZ)("E8")
            + Lattices(ZZ)([[determinant]])
        )
    signature = lattice.signature_pair()
    built = [int(signature.first()), int(signature.second())]
    if built != [int(entry) for entry in card["signature"]]:
        raise ArithmeticError(
            f"the lattice built for card {tag} has signature {built}, "
            f"against the card's {card['signature']}"
        )
    if lattice.determinant() != ZZ(card["determinant"]):
        raise ArithmeticError(
            f"the lattice built for card {tag} has determinant {lattice.determinant()}, "
            f"against the card's {card['determinant']}"
        )
    return lattice


def _sterk_plane_representatives(lattice):
    r"""Sterk's two $O(N)$-orbit representatives of primitive isotropic planes.

    $P_1 = \mathbb{Z} e_1 + \mathbb{Z} e_3$ and $P_2 = \mathbb{Z}(2 e_1 + 2 e_2 +
    w) + \mathbb{Z} e_3$ with $w$ of norm $-8$ in $E_8(-2)$ (H. Sterk,
    *Compactifications of the period space of Enriques surfaces, Part I*,
    Math. Z. 207 (1991), Proposition 4.6), in the standard bases $(e_1, e_2)$ of
    $U$ and $(e_3, e_4)$ of $U(2)$ that Dutour Sikirić--Hulek use.  They are the
    argument of the subgroup plane call, not an expected value: the count that
    comes back is the card's.
    """
    basis = list(lattice.module_generators())
    first, second, third = basis[0], basis[1], basis[2]
    w = basis[4] + basis[5]
    if lattice.q(w) != ZZ(-8):
        raise ArithmeticError(f"the vector w has square {lattice.q(w)}, not -8")
    representatives = (
        lattice.primitive_isotropic_subobject(first, third),
        lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third),
    )
    for plane in representatives:
        if plane.module_rank() != cardinal(2) or plane.is_primitive() is not True:
            raise ArithmeticError(f"{plane} is not a primitive isotropic plane")
        for left in plane.module_generating_set():
            for right in plane.module_generating_set():
                if lattice.b(
                    plane.inclusion()(plane.module_generator(left)),
                    plane.inclusion()(plane.module_generator(right)),
                ) != ZZ(0):
                    raise ArithmeticError(f"{plane} is not totally isotropic")
    return representatives


def _subgroup(lattice, name: str):
    r"""The group a card row names, on ``lattice``.

    ``O`` is the whole orthogonal group, ``O+`` its index-two subgroup, and
    ``Otilde+`` the kernel of the discriminant character intersected with it.
    """
    if name == "O":
        return lattice.Aut()
    if name == "O+":
        return lattice.O_plus()
    if name == "Otilde+":
        return lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    if name == "gamma-en-2":
        return _gamma_en_2()
    raise ValueError(f"{name!r} is not a group a card row of this module names")


def _gamma_en_2():
    r"""$\Gamma_{\mathrm{En},2}$, Alexeev--Engel--Garza--Schaffler, Definition 2.6.

    The image in $O(T_{\mathrm{En}})$ of $\{g \in O(L) : g I_{\mathrm{En}} =
    I_{\mathrm{En}} g,\ g(h) = h\}$ at the degree-two polarization $h$, built by the
    coinvariant construction rather than from a description of its image in
    $O(q)$.
    """
    invariant = Involutions.I_En.invariant_lattice()
    basis_elements = list(invariant.module_generators())
    marks = []
    for left, left_vector in enumerate(basis_elements):
        for right, right_vector in enumerate(basis_elements):
            if right <= left:
                continue
            if (
                invariant.q(left_vector) == ZZ.zero()
                and invariant.q(right_vector) == ZZ.zero()
                and invariant.b(left_vector, right_vector) != ZZ.zero()
            ):
                marks.append((left, right, invariant.b(left_vector, right_vector)))
    left, right, _pairing = next(entry for entry in marks if entry[2] == ZZ(2))
    h_invariant = basis_elements[left] + basis_elements[right]
    polarized = Involutions.I_En.polarized(invariant.inclusion()(h_invariant))
    return polarized.coinvariant_extension_subgroup()


def _card_subset(latex: str):
    r"""Return ``(nodes, barred)`` for the subset factor of a polarization card's LaTeX.

    A card writes $\overline{\Gamma}_{h,N}(\overline{\{0\}})$ when the printed
    subset is the complement of the generating set, and
    $\overline{\Gamma}_{h,N}(\{4, 6, 3, 5\})$ when the subset itself is the
    generating set; the card's own LaTeX carries that bar, so the decode reads it
    rather than inferring it from the size.
    """
    opening = latex.rfind("(")
    closing = latex.rfind(")")
    if opening < 0 or closing < opening:
        raise ValueError(f"the card's LaTeX names no subset: {latex}")
    text = latex[opening + 1 : closing]
    return tuple(int(part) for part in re.findall(r"-?\d+", text)), "overline" in text


def _support(nodes, barred) -> tuple:
    r"""The $g$-basis support the card's subset denotes."""
    walls = tuple(NODE_TO_WALL[node] for node in nodes)
    if barred:
        return tuple(sorted(walls))
    return tuple(wall for wall in WALL_INDICES if wall not in walls)


class Enriques:
    r"""The polarization lattice of card ``0128``, and the $\Gamma_h$ construction."""

    def __init__(self):
        self.invariant = Involutions.I_En.invariant_lattice()
        self.unimodular = Lattices(ZZ)([list(row) for row in W_ROWS])
        self.doubled = Lattices(ZZ)([[2 * entry for entry in row] for row in W_ROWS])
        self.transport = self.doubled.isometry_to(self.invariant)
        self.labels = tuple(self.doubled.module_generating_set())
        self.ambient = Involutions.I_En.formed_coinvariants()
        if self.unimodular.determinant() != ZZ(-1):
            raise ArithmeticError("U + E8(-1) is not unimodular")
        if self.ambient.determinant() != ZZ(1024):
            raise ArithmeticError("the anti-invariant lattice is not the determinant-1024 T_En")
        if not self.ambient.is_isometric(NamedLattices.TEn):
            raise ArithmeticError("the anti-invariant lattice is not T_En")

    def doubled_point(self, support_indices):
        r"""The polarization supported on the card's $g$-basis subset."""
        return sum(
            (self.doubled.module_generator(self.labels[index - 1]) for index in support_indices),
            self.doubled.zero(),
        )

    def doubled_from_unimodular(self, vector):
        r"""The same coordinate vector read in $M = 2W$, where its square doubles."""
        coordinates = vector.to_vector()
        target_labels = tuple(self.doubled.module_generating_set())
        source_labels = tuple(self.unimodular.module_generating_set())
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
        r"""$\Gamma_h$: the image of $O(M, h)$, transported, preimage in $O(N)$."""
        vector_in_M = self.transport(vector_of_doubled)
        return Involutions.I_En.polarized(
            self.invariant.inclusion()(vector_in_M)
        ).coinvariant_extension_subgroup()

    def polarization_group(self, card):
        r"""The group a polarization card names, built from the card's own subset."""
        if card["lattice"] != ENRIQUES_LATTICE_TAG:
            raise CardMissing(
                f"the card names lattice {card['lattice']}, not {ENRIQUES_LATTICE_TAG}"
            )
        if card["parent_group"] != ENRIQUES_PARENT_GROUP:
            raise CardMissing(
                f"the card names parent group {card['parent_group']}, not {ENRIQUES_PARENT_GROUP}"
            )
        nodes, barred = _card_subset(card["latex"])
        return self.group(self.doubled_point(_support(nodes, barred)))


def _computed(row: Row) -> int:
    r"""The number the public call of #286 returns for ``row``."""
    if row.card == TABLE4_TAG:
        return _computed_table4_row(row)
    if row.card.startswith("gamma-h-"):
        group = Enriques().polarization_group(card_arithmetic_group(row.card))
        return _orbit_count(group, row.quantity, None)
    if row.card == "otilde-plus-t-en":
        lattice = _card_lattice(card_arithmetic_group(row.card)["lattice"])
        return _orbit_count(
            _subgroup(lattice, "Otilde+"),
            row.quantity,
            _sterk_plane_representatives(lattice),
        )
    lattice = _card_lattice(row.card)
    representatives = (
        _sterk_plane_representatives(lattice)
        if row.card == ENRIQUES_LATTICE_TAG and row.group != "O"
        else None
    )
    return _orbit_count(_subgroup(lattice, row.group), row.quantity, representatives)


def _orbit_count(group, quantity: str, representatives) -> int:
    r"""One public orbit count of the group ``group``."""
    if quantity == "lines":
        return int(group.isotropic_orbit_representatives(1).cardinality())
    if quantity == "planes":
        if representatives is not None:
            return int(group.isotropic_plane_orbits(representatives).cardinality())
        return int(group.isotropic_orbit_representatives(2).cardinality())
    if quantity == "flags":
        return int(group.isotropic_orbit_representatives(2, flag=True).cardinality())
    raise ValueError(f"{quantity!r} is not an orbit quantity this module compares")


def _computed_table4_row(row: Row) -> int:
    r"""Card ``0128``'s Table 4 row: ``#h``, or the number of distinct group classes.

    Both rows are read off the same classes, and the source's classes are those of
    *primitive* vectors of square ``row.degree``: Section 2, the paragraph
    introducing (3), fixes the primitivity of ``h``, and Section 3.4 states Table 4's
    first line as the number of orbits of primitive vectors in a given degree.  The
    square-``2d`` shell also carries the classes ``c * w`` of every content ``c > 1``
    with ``c^2 | 2d``, which no isometry can carry onto a primitive vector: they are
    the nonprimitive numerical polarizations the source lists and disregards
    (Section 3.5), and Table 4 does not count them.
    """
    orthogonal = Enriques()
    classes = orthogonal.unimodular.Aut().vector_orbit_representatives(
        row.degree, content=1
    )
    count = int(classes.cardinality())
    if row.quantity == "#h":
        return count
    if row.quantity != "#Gamma_h":
        raise ValueError(f"{row.quantity!r} is not a Table 4 quantity")
    triples = []
    for representative in tuple(classes):
        group = orthogonal.group(orthogonal.doubled_from_unimodular(representative))
        triples.append(
            tuple(
                _orbit_count(group, quantity, None)
                for quantity in ("lines", "planes", "flags")
            )
        )
    return len(set(triples))


def _lattice_and_group(row: Row) -> tuple:
    r"""The lattice and the group a row is about, named as its card names them.

    A defect names the lattice and the group, so the two are read from the card
    rather than restated: a lattice card names its lattice, and an
    arithmetic-group card names both its lattice and itself.
    """
    if row.card == TABLE4_TAG:
        lattice = card_polarization_lattice()
        return (f"{lattice['tag']}: {lattice['name']}", f"O({lattice['name']})")
    if row.card.startswith("gamma-h-") or row.card == "otilde-plus-t-en":
        group = card_arithmetic_group(row.card)
        lattice = card_lattice(group["lattice"])
        return (f"{lattice['tag']}: {lattice['name']}", group["name"])
    lattice = card_lattice(row.card)
    return (f"{row.card}: {lattice['name']}", row.group)


def _outcome(row: Row, cap: int) -> dict:
    r"""One row's outcome: the card's value, the call's value, and which is which."""
    outcome = {
        "id": row.identifier(),
        "card": row.card,
        "group": row.group,
        "quantity": row.quantity,
        "degree": row.degree or None,
    }
    try:
        expected = _expected(row)
        citation = _citation(row)
    except CardMissing as missing:
        outcome.update(state="MISSING", detail=str(missing))
        return outcome
    outcome["expected"] = int(expected)
    outcome["statement"] = _statement(citation)
    outcome["lattice"], outcome["group"] = _lattice_and_group(row)
    started = time.time()

    def interrupt(signum, frame):
        raise TimeoutError

    signal.signal(signal.SIGALRM, interrupt)
    signal.alarm(cap)
    try:
        computed = int(_computed(row))
        signal.alarm(0)
    except TimeoutError:
        outcome.update(
            state="UNDECIDED",
            detail=f"the public call did not return inside {cap} s",
            elapsed=round(time.time() - started, 1),
        )
        return outcome
    except Exception as error:  # a row that raises is that row's outcome, not the run's
        outcome.update(
            state="BROKEN",
            detail=f"{type(error).__name__}: {error}",
            elapsed=round(time.time() - started, 1),
        )
        return outcome
    finally:
        signal.alarm(0)
    outcome["computed"] = computed
    outcome["elapsed"] = round(time.time() - started, 1)
    outcome["state"] = "PASS" if computed == outcome["expected"] else "FAIL"
    return outcome


def _run_row_in_child(row: Row, cap: int) -> dict:
    r"""Run one row in a child process of its own and return its outcome.

    A row that hangs past its cap or that grows past the machine's memory is that
    row's outcome: the child is killed and reported, and the run's report survives
    to name it.
    """
    command = [
        sys.executable,
        os.path.abspath(__file__),
        "--one",
        row.identifier(),
        "--cap",
        str(cap),
    ]
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=cap + _STARTUP_ALLOWANCE,
        )
    except subprocess.TimeoutExpired:
        return {
            "id": row.identifier(),
            "card": row.card,
            "group": row.group,
            "state": "UNDECIDED",
            "detail": f"the row did not finish inside {cap + _STARTUP_ALLOWANCE} s",
            "elapsed": round(time.time() - started, 1),
        }
    for line in completed.stdout.splitlines():
        if line.startswith(_OUTCOME_PREFIX):
            return json.loads(line[len(_OUTCOME_PREFIX) :])
    tail = completed.stderr.strip().splitlines()
    return {
        "id": row.identifier(),
        "card": row.card,
        "group": row.group,
        "state": "BROKEN",
        "detail": (
            f"the child exited {completed.returncode} with no outcome; "
            f"{tail[-1] if tail else 'no stderr'}"
        ),
        "elapsed": round(time.time() - started, 1),
    }


def _run_exit(outcomes) -> int:
    r"""The run's exit status: 0 only when every row agrees with its card.

    An absent row is not an agreement.  A selection that matches none of the rows
    this module enumerates is 2, so a matrix entry whose arguments miss every row
    fails instead of comparing nothing; any row that is not ``PASS`` -- ``FAIL``,
    ``MISSING``, ``UNDECIDED``, ``BROKEN`` or ``NOT REACHED`` -- is 1, so a skipped,
    absent or undecided row can never be counted as agreement.
    """
    if not outcomes:
        return 2
    return 0 if all(outcome["state"] == "PASS" for outcome in outcomes) else 1


def _retain(outcomes, run_exit) -> str:
    r"""Append one JSON object per row to the run's own record under ``.timings/``.

    CONTRIBUTING.md ENV-03 keeps a run's record where the workflow uploads it, so
    every outcome carries its row identity, the card it was read from, the lattice
    and group its card names, both values, the state, the revision and the run's
    exit status.  One line per row makes a current raw outcome retrievable per row
    rather than only as prose in a log, which is what an audit of these rows needs.
    """
    from sage_extensions.timing import current_commit, timing_directory

    directory = timing_directory()
    directory.mkdir(parents=True, exist_ok=True)
    revision = current_commit()
    path = directory / f"rows-{revision[:12]}-{os.getpid()}.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        for outcome in outcomes:
            handle.write(
                json.dumps({**outcome, "revision": revision, "run_exit": run_exit})
                + "\n"
            )
    return f"{path}"


def _append_ledger(paths, outcomes, revision: str) -> None:
    r"""Append one durable line per attempted row: card, dimension, what it returned, and when.

    The ledger is the acceptance's raw record, so a line is written for *every*
    attempt and none is edited afterwards: a row that raised carries the
    exception's text in ``detail`` and ``returned`` is ``null``, a row that did not
    return inside its cap carries the state it reached, and a row that improved on
    a later revision is a second line rather than a replacement of the first.  The
    dimension is the card's quantity and, for card ``0128``, the degree, so
    coverage can be read per dimension rather than per family.
    """
    written = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for path in paths:
        with open(path, "a", encoding="utf-8") as handle:
            for outcome in outcomes:
                handle.write(
                    json.dumps(
                        {
                            "row": outcome["id"],
                            "card": outcome["card"],
                            "quantity": outcome.get("quantity"),
                            "degree": outcome.get("degree"),
                            "lattice": outcome.get("lattice"),
                            "group": outcome.get("group"),
                            "expected": outcome.get("expected"),
                            "returned": outcome.get("computed"),
                            "detail": outcome.get("detail"),
                            "state": outcome["state"],
                            "elapsed": outcome.get("elapsed"),
                            "revision": revision,
                            "measured_at": written,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )


def _revision() -> str:
    r"""The revision these rows are measured at, as the library records its own source."""
    from sage_extensions.timing import current_commit

    return current_commit()


def _latest_attempts(paths) -> dict:
    r"""Every attempt each row has over ``paths``, in the order the lines were appended."""
    attempts = {}
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                attempt = json.loads(stripped)
                attempts.setdefault(attempt["row"], []).append(attempt)
    return attempts


def _coverage(rows, latest) -> tuple:
    r"""Which required rows the ledger decides, and which it does not.

    The card is the oracle and a ledger line is a claim about it.  The ``state`` on
    a line is the state the measuring run reached, not a comparison it made against
    anything: it is written by whichever run measured the row, at whichever
    revision, and read here by a process that measured nothing.  So a line decides
    nothing by its label.  What it is read for is the value it says the call
    returned, set against the number the row's card states -- read by the row's tag
    here and now, never out of the line's own ``expected`` field.

    A row's attempts are read at the latest revision it was tried at, and every one
    of them has to pass that comparison: an operation that raises on one attempt and
    returns the card's number on the next has not decided the row at that revision,
    and a later happy run cannot erase the attempt that raised.  A required row is
    therefore absent when the ledger holds no attempt for it at all, when its card
    states no such row, when any attempt at that revision is not a ``PASS``, when
    two of them returned different numbers, and when the number they returned is not
    the card's.
    """
    attempted = {}
    for row in rows:
        attempts = latest.get(row.identifier())
        if attempts:
            attempted[row.identifier()] = attempts
    decided, absent = [], []
    for row in rows:
        attempts = attempted.get(row.identifier())
        if not attempts:
            absent.append((row, "no attempt recorded"))
            continue
        try:
            stated = int(_expected(row))
        except CardMissing as missing:
            absent.append((row, f"the card states no such row: {missing}"))
            continue
        revision = attempts[-1]["revision"]
        at_revision = [attempt for attempt in attempts if attempt["revision"] == revision]
        broken = [attempt for attempt in at_revision if attempt["state"] != "PASS"]
        if broken:
            absent.append(
                (
                    row,
                    f"{len(broken)} of {len(at_revision)} attempts at {revision[:12]} "
                    f"are not PASS; the latest is {broken[-1]['state']}: {broken[-1].get('detail')}",
                )
            )
            continue
        values = {attempt["returned"] for attempt in at_revision}
        if len(values) > 1:
            absent.append(
                (
                    row,
                    f"the attempts at {revision[:12]} returned different numbers: "
                    f"{sorted(values)}",
                )
            )
            continue
        returned = at_revision[-1]["returned"]
        if returned != stated:
            absent.append(
                (
                    row,
                    f"the attempts at {revision[:12]} returned {returned} and the card "
                    f"states {stated}",
                )
            )
            continue
        decided.append((row, at_revision[-1]))
    return decided, absent


def _coverage_report(selected, decided, absent) -> None:
    r"""Print coverage per dimension, then name every absent row with its reason."""
    dimensions = {}
    for row, _attempt in decided:
        dimensions.setdefault(_dimension(row), [0, 0])[0] += 1
    for row, _reason in absent:
        dimensions.setdefault(_dimension(row), [0, 0])[1] += 1
    _log("")
    _log(f"COVERAGE over the {len(selected)} required rows of this selection")
    for name in sorted(dimensions):
        agreed, missing = dimensions[name]
        _log(f"  {name}: {agreed} decided, {missing} absent")
    _log(f"  decided {len(decided)}, absent {len(absent)}")
    revisions = {}
    for _row, attempt in decided:
        revisions[attempt["revision"][:12]] = revisions.get(attempt["revision"][:12], 0) + 1
    if revisions:
        _log(
            "  the decided rows rest on the revision each was measured at: "
            + ", ".join(f"{revision} ({count})" for revision, count in sorted(revisions.items()))
        )
    for row, reason in absent:
        _log(f"  ABSENT {row.identifier()}: {reason}")


def _dimension(row: Row) -> str:
    r"""The dimension a row is counted in: its card and quantity, with the degree for ``0128``."""
    if row.card == TABLE4_TAG:
        return f"{row.card} {row.quantity} at 2d = {row.degree}"
    return f"{row.card} {row.quantity}"


def _log(message: str = "") -> None:
    print(message, flush=True)


def _report(outcome: dict) -> None:
    r"""Print one row's outcome, and its defect block when it disagrees with its card."""
    _log("")
    _log(f"ROW {outcome['id']}  [{outcome['state']}]")
    if "statement" in outcome:
        _log(f"  lattice {outcome['lattice']}   group {outcome['group']}")
        _log(f"  card: {outcome['statement']}")
    if outcome["state"] == "MISSING":
        _log(f"  MISSING: {outcome['detail']}")
        return
    if "expected" in outcome:
        _log(f"  expected {outcome['expected']}  call {outcome.get('computed', '-')}"
             f"   ({outcome.get('elapsed', '-')} s)")
    if outcome["state"] != "PASS":
        _log(f"  {outcome['state']}: {outcome.get('detail', 'no detail')}")
    if outcome["state"] == "FAIL":
        _log("  DEFECT")
        _log(f"    card: {outcome['card']}")
        _log(f"    lattice: {outcome['lattice']}")
        _log(f"    group: {outcome['group']}")
        _log(f"    expected: {outcome['expected']}")
        _log(f"    computed: {outcome['computed']}")
        _log(f"    citation: {outcome['statement']}")


def _parse(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--one", default=None, help="one row's identifier, run in this process")
    parser.add_argument("--tags", default=None, help="comma-separated card tags")
    parser.add_argument("--degrees", default=None, help="comma-separated degrees of card 0128")
    parser.add_argument(
        "--rows",
        default=None,
        help="comma-separated quantities: lines, planes, flags, #h, #Gamma_h",
    )
    parser.add_argument(
        "--cap",
        type=int,
        default=int(os.environ.get("ENRIQUES_CALL_CAP", "1800")),
        help="seconds one row's public calls may take before the row is undecided",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=int(os.environ.get("ENRIQUES_ROW_BUDGET", "0")),
        help="seconds for the whole run; 0 runs every selected row",
    )
    parser.add_argument(
        "--ledger",
        default=None,
        help="append every attempted row to each named JSONL ledger, comma separated",
    )
    parser.add_argument(
        "--coverage",
        default=None,
        help=(
            "comma-separated ledgers to check instead of computing: exit 1 and name "
            "every required row whose latest attempt there is not a PASS"
        ),
    )
    return parser.parse_args(argv)


def _split(value):
    return () if value is None else tuple(part.strip() for part in value.split(",") if part.strip())


def main(argv=None) -> int:
    arguments = _parse(argv)
    rows = _rows()
    if arguments.one is not None:
        matches = tuple(row for row in rows if row.identifier() == arguments.one)
        if not matches:
            _log(f"no row has the identifier {arguments.one!r}")
            return 2
        outcome = _outcome(matches[0], arguments.cap)
        status = _run_exit([outcome])
        _log(_OUTCOME_PREFIX + json.dumps(outcome))
        if arguments.ledger:
            _append_ledger(_split(arguments.ledger), [outcome], _revision())
        _log(f"record: {_retain([outcome], status)}")
        return status

    tags = _split(arguments.tags)
    degrees = tuple(int(degree) for degree in _split(arguments.degrees))
    quantities = _split(arguments.rows)
    selected = _select(rows, tags, degrees, quantities)
    if not selected:
        _log(
            f"no row of the {len(rows)} this module enumerates matches the selection: "
            f"tags {tags}, degrees {degrees}, quantities {quantities}"
        )
        return 2

    if arguments.coverage:
        ledgers = _split(arguments.coverage)
        _log(f"coverage of {len(selected)} required rows against {', '.join(ledgers)}")
        decided, absent = _coverage(selected, _latest_attempts(ledgers))
        _coverage_report(selected, decided, absent)
        if absent:
            _log("")
            _log(
                f"{len(absent)} of the {len(selected)} required rows have no PASS in the "
                f"ledger; the aggregate comparison is not a pass"
            )
            return 1
        _log("")
        _log(f"all {len(selected)} required rows have a PASS in the ledger")
        return 0

    _log(f"rows: {len(rows)} known, {len(selected)} selected")
    provenance = card_provenance()
    _log(f"cards: {provenance['repository']} at its commit {provenance['ref']}")
    _log(f"per-row cap {arguments.cap} s, budget {arguments.budget or 'unbounded'} s")

    deadline = time.time() + arguments.budget if arguments.budget else None
    outcomes = []
    for row in selected:
        if deadline is not None and time.time() > deadline:
            outcomes.append(
                {
                    "id": row.identifier(),
                    "card": row.card,
                    "group": row.group,
                    "state": "NOT REACHED",
                    "detail": f"the run's {arguments.budget} s budget ended before this row",
                }
            )
            continue
        outcome = _run_row_in_child(row, arguments.cap)
        _report(outcome)
        outcomes.append(outcome)

    _log("")
    _log("SUMMARY")
    for state in ("PASS", "FAIL", "MISSING", "UNDECIDED", "BROKEN", "NOT REACHED"):
        named = [outcome["id"] for outcome in outcomes if outcome["state"] == state]
        _log(f"  {state}: {len(named)}")
        for identifier in named:
            _log(f"    {identifier}")
    defects = [outcome for outcome in outcomes if outcome["state"] == "FAIL"]
    for defect in defects:
        _log("")
        _log(
            f"DEFECT {defect['id']}: {defect['lattice']} under {defect['group']}: "
            f"expected {defect['expected']}, computed {defect['computed']}"
        )
        _log(f"  {defect['statement']}")
    decided = sum(1 for outcome in outcomes if outcome["state"] == "PASS")
    _log("")
    _log(f"{decided} of {len(outcomes)} rows agree with their cards")
    status = _run_exit(outcomes)
    if arguments.ledger:
        _append_ledger(_split(arguments.ledger), outcomes, _revision())
    _log(f"record: {_retain(outcomes, status)}")
    return status


if __name__ == "__main__":
    sys.exit(main())
