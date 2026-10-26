r"""Root lattices given by Gram matrices: automorphism orders and an E8 basis change.

The named constructors (``Lattices(ZZ)("E8")``) fix one basis per root lattice.
These specimens enter through the Gram-tensor constructor instead, in other
bases: the Cartan matrices of Conway--Sloane, Table 4.1 (roots of norm 2, joined
roots pairing to -1, Bourbaki numbering), and the E8 test matrix of the upstream
Indefinite.jl suite.  ``O(L)`` is a basis-free invariant, so each order must be
the one SPLAG chapter 4 states for that lattice: ``g = g_0 g_1`` (section 4).
Migrated from sage-indefinite-port, which consumes this definite route.
"""

import pytest

from sage_extensions.all import *

CARTAN_E8 = [
    [2, 0, -1, 0, 0, 0, 0, 0],
    [0, 2, 0, -1, 0, 0, 0, 0],
    [-1, 0, 2, -1, 0, 0, 0, 0],
    [0, -1, -1, 2, -1, 0, 0, 0],
    [0, 0, 0, -1, 2, -1, 0, 0],
    [0, 0, 0, 0, -1, 2, -1, 0],
    [0, 0, 0, 0, 0, -1, 2, -1],
    [0, 0, 0, 0, 0, 0, -1, 2],
]
INDEFINITE_JL_E8 = [
    [2, 0, 0, 0, 0, 0, 1, 0],
    [0, 2, -1, 0, -1, 1, 0, 1],
    [0, -1, 2, 1, 0, 0, 0, -1],
    [0, 0, 1, 2, 0, 0, 1, -1],
    [0, -1, 0, 0, 2, -1, 1, -1],
    [0, 1, 0, 0, -1, 2, 0, 0],
    [1, 0, 0, 1, 1, 0, 2, -1],
    [0, 1, -1, -1, -1, 0, -1, 2],
]

# (Gram matrix, |O(L)|, SPLAG chapter 4 entry)
GRAM_PRESENTED_ROOT_LATTICES = {
    "A2": ([[2, -1], [-1, 2]], 12, "section 6, A2: g_0 = 3!, g_1 = 2, g = 12"),
    "A3": (
        [[2, -1, 0], [-1, 2, -1], [0, -1, 2]],
        48,
        "section 6, A3 = D3: g_0 = 24, g_1 = 2, g = 48",
    ),
    "D4": (
        [[2, -1, 0, 0], [-1, 2, -1, -1], [0, -1, 2, 0], [0, -1, 0, 2]],
        1152,
        "section 7, n = 4: g_0 = 2^3 4!, g_1 = 3!",
    ),
    "E6": (
        [
            [2, 0, -1, 0, 0, 0],
            [0, 2, 0, -1, 0, 0],
            [-1, 0, 2, -1, 0, 0],
            [0, -1, -1, 2, -1, 0],
            [0, 0, 0, -1, 2, -1],
            [0, 0, 0, 0, -1, 2],
        ],
        103680,
        "section 8, E6: g_0 = |W(E6)| = 51840, G_1 = C_2",
    ),
    "E7": (
        [
            [2, 0, -1, 0, 0, 0, 0],
            [0, 2, 0, -1, 0, 0, 0],
            [-1, 0, 2, -1, 0, 0, 0],
            [0, -1, -1, 2, -1, 0, 0],
            [0, 0, 0, -1, 2, -1, 0],
            [0, 0, 0, 0, -1, 2, -1],
            [0, 0, 0, 0, 0, -1, 2],
        ],
        2903040,
        "section 8, E7: g_0 = |W(E7)| = 2903040, G_1 = 1",
    ),
    "E8 (Cartan)": (CARTAN_E8, 696729600, "section 8, E8: g_0 = 696729600, g_1 = 1"),
    "E8 (Indefinite.jl)": (
        INDEFINITE_JL_E8,
        696729600,
        "section 8, E8; chapter 2, Table 2.2: one even unimodular lattice in dimension 8",
    ),
}


@pytest.mark.parametrize("name", list(GRAM_PRESENTED_ROOT_LATTICES))
def test_gram_presented_root_lattice_has_the_conway_sloane_automorphism_order(name) -> None:
    gram, order, _entry = GRAM_PRESENTED_ROOT_LATTICES[name]
    assert Lattices(ZZ)(gram).Aut().order() == order


def test_an_isometry_between_two_e8_bases_preserves_the_form_and_inverts() -> None:
    r"""The two E8 Gram matrices present one even unimodular lattice (SPLAG 2, Table 2.2).

    So ``Isom`` between them is nonempty, and any element carries the pairing of
    one presentation to the other and is undone by its inverse.
    """
    source = Lattices(ZZ)(CARTAN_E8)
    target = Lattices(ZZ)(INDEFINITE_JL_E8)

    witness = source.Isom(target).an_element()
    inverse = ~witness

    assert witness.domain() is source
    assert witness.codomain() is target
    for left in source.module_generators():
        for right in source.module_generators():
            assert source.b(left, right) == target.b(witness(left), witness(right))
        assert inverse(witness(left)) == left
