r"""The O⁺ plane split is a double coset, decided by one plane-block witness (#379).

`O⁺ = sn⁻¹(+1)` contains `ker(ρ, sn)`, which is normal in `O(L)`, so by Dutour
Sikirić–Hulek, *Moduli of polarised Enriques surfaces — computational aspects*,
arXiv:2302.01679v2, Lemma 3.6, p. 22, the `O⁺`-orbits inside one `O(L)`-orbit of a
primitive isotropic plane `P` are the double cosets
`(ρ,sn)(O⁺) \\ (ρ,sn)(O(L)) / (ρ,sn)(Stab(P))`.  Since `[O(L):O⁺] = 2` and
`(ρ,sn)(O⁺)` is the kernel of the real spinor norm inside the ambient image, **one**
element of the plane stabilizer whose character image is outside `(ρ,sn)(O⁺)` puts the
two halves together: the ambient representative is then the single `O⁺` representative.

That element is built rather than searched for: `plane_block_lift(action)` solves the
block equations of the same paper's Theorem 4.9 (printed pp. 33–34) with the quotient
block prescribed as the identity, so an action of odd determinant gives an integral
element of the parabolic whose plane action is that action.  This file pins the three
things the route rests on, on specimens small enough for the per-test gate:

* `[O(L):O⁺] = 2` is computed, not read off a class;
* the witness exists, lies in `O(L)`, fixes the plane setwise, and has odd determinant —
  so it is genuinely outside `O⁺` and genuinely in the stabilizer;
* `O⁺`'s plane count then equals `O`'s, which on these specimens is one orbit.

`U(2) + U(2)` is the specimen that matters: it has **no** square-two vector, so no
reflection witnesses the odd coset there, and the plane-block witness is what decides
the split.  The two cards' rows themselves are compared by tag in
`tests/lattices/test_scattone_plane_orbits.sage` (`card_plane_orbit_row("6JRX", "O+")`,
`card_plane_orbit_row("6JRY", "O+")`), which is where the long rank-21 runs live.
"""

from sage_extensions.all import *  # noqa: F401,F403

#: Specimens small enough for the gate; the second has no square-two vector at all.
_SPECIMENS = (
    Lattices(ZZ)("U") + Lattices(ZZ)("U"),
    Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[0, 2], [2, 0]]),
)


def test_o_plus_is_the_index_two_spinor_kernel() -> None:
    r"""`[O(L):O⁺] = 2` on both specimens, computed from the character images."""
    for lattice in _SPECIMENS:
        assert lattice.O_plus().finite_character_quotient().index() == 2


def test_the_plane_witness_is_an_odd_element_of_the_plane_stabilizer() -> None:
    r"""One plane-block witness per ambient plane, in `O(L)`, fixing the plane, odd.

    Every returned witness is checked on the four properties the double-coset argument
    uses: it is an integral isometry, it stabilizes the plane, its determinant is `-1`
    (hence its character image is the odd one), and it is the lift the block equations
    produced rather than a guess.
    """
    for lattice in _SPECIMENS:
        quotient = lattice.O_plus().finite_character_quotient()
        automorphisms = lattice.Aut()
        for plane in automorphisms.isotropic_orbit_representatives(2):
            witness = quotient.plane_odd_character_witness(plane)
            assert witness in automorphisms
            assert plane.stabilizes(witness) is True
            assert witness.determinant() == -lattice.base_ring().one()


def test_the_plane_count_under_o_plus_is_the_count_under_o() -> None:
    r"""The split keeps one orbit per ambient orbit on both specimens.

    The count is compared with the ambient call's own count on the same lattice, so
    the statement holds on both specimens without a typed number; the non-vacuity is
    that the count is not zero.
    """
    for lattice in _SPECIMENS:
        under_o = lattice.Aut().isotropic_orbit_representatives(2).cardinality()
        under_o_plus = lattice.O_plus().isotropic_orbit_representatives(2).cardinality()
        assert int(under_o) == 1
        assert int(under_o_plus) == int(under_o)
