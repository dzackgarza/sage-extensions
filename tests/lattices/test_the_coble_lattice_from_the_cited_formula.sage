r"""``T_Co`` from the formula of the source, and the discriminant values its orbit call needs.

``T_Co`` is the lattice ``N`` of D. Dolgachev and S. Kondo, *Enriques surfaces and
Borel--Weil--Bott type duality*, Izv. Math. 77:3 (2013), section 3, equation (3.6),
printed p. 513: ``N = <2> + E(2)`` with ``E = E8 + U``, and ``E8`` negative definite
(``E8(-1)``), which the source's own signature ``(2, 9)`` forces: ``<2>`` contributes
one positive square and ``(E8(-1) + U)(2)`` has signature ``(1, 9)``.  This file builds
that formula and checks that ``NamedLattices.Tco`` is the same lattice in the same
basis, so every value below is computed from the cited construction.

The group of the Coble divisor and its three restricted stabilizers are
``def:gamma-co-groups`` and ``prop:gamma-co-images`` of dzackgarza/research at
``38fa09935a``; what this file measures is the lattice and its discriminant form, the
two pieces of every row of that call.  The orbit calls themselves do not return yet on
``T_Co`` -- the stages and stacks are in ``results/issue286-tco-run.md`` -- so no orbit
count, index or incidence is stated here.

``A_{T_Co}`` has ``2048`` classes and ``528`` of them are isotropic, ``527`` of them
nonzero; the record of those two values is research's ``coble_528_isotropic_classes.py``
(runs of 2026-11-05, quoted in sage-extensions#286).  The single pass over the classes
below costs about sixty seconds on the adopted runtime.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513, in the catalogue's block order."""
    return Lattices(ZZ)([[2]]) + (NamedLattices.U + NamedLattices.E8).twist(2)


def test_the_cited_formula_builds_the_catalogue_lattice_in_the_same_basis() -> None:
    r"""The catalogue entry is the source's ``<2> + E(2)`` block for block, entry for entry."""
    lattice = _coble_lattice()
    catalogue = NamedLattices.Tco
    assert lattice.module_rank() == catalogue.module_rank()
    formula = tuple(lattice.module_generators())
    named = tuple(catalogue.module_generators())
    for first, left in enumerate(formula):
        for second, right in enumerate(formula):
            assert lattice.b(left, right) == catalogue.b(named[first], named[second])


def test_the_coble_lattice_has_the_signature_and_discriminant_of_the_source() -> None:
    r"""``T_Co`` is even, of signature ``(2, 9)`` and determinant ``-2048``: ``A = (Z/2)^11``."""
    lattice = _coble_lattice()
    assert lattice.signature_pair().first() == cardinal(2)
    assert lattice.signature_pair().second() == cardinal(9)
    assert lattice.determinant() == ZZ(-2048)
    assert lattice.is_even() is True
    assert lattice.is_p_elementary(ZZ(2)) is True
    assert lattice.discriminant_group().cardinality() == cardinal(2048)


def test_the_coble_discriminant_form_has_528_isotropic_classes_and_527_of_them_nonzero() -> None:
    r"""The isotropic class count of ``A_{T_Co}``, compared with the record of the source list."""
    lattice = _coble_lattice()
    discriminant = lattice.discriminant_group()
    zero = discriminant.zero()
    zero_value = discriminant.q(zero)
    isotropic = 0
    nonzero = 0
    for candidate in discriminant.elements():
        if discriminant.q(candidate) == zero_value:
            isotropic += 1
            if candidate != zero:
                nonzero += 1
    assert isotropic == 528
    assert nonzero == 527
