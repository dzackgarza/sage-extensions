r"""A registered lift carries the element it acts by on the divided classes.

A plane row splits the ambient ``O(L)``-orbit of a plane into ``Gamma``-orbits by
the double cosets ``rho(Gamma) \ rho(O(L)) / rho(Stab)``, and registers one
isometry per double coset: the lift ``s_P`` that carries the source plane onto
``P`` (D. Dutour Sikiric and Hulek, arXiv:2302.01679v2, Lemma 3.6, printed
p. 22).  A consumer of the row that wants what the lift does to the divided
classes of ``A_L = L^\#/L`` needs ``rho(s_P)``, and the registry keeps that
element beside the lift, read from the split's own evaluation of ``rho``.

The assertions are the two statements that make the pair one datum:

* at every plane cusp of the row, the registered element is the lift's own
  discriminant morphism, ``rho(s_P)`` -- not an image of it under some other
  convention;
* for every ordered pair of the row's planes, the composite's action is the
  product of the two registered elements, ``rho(s_P) rho(s_{P_0})^{-1}``, which
  is what a walk carrying one plane's classes to another composes.

Both are read on ``U + U(2) + <-2>``, whose two kernel rows the gate can
afford.  Neither row holds a lattice-database card (lattice-database#13), so
nothing here is a card value: the two plane cusps of each row are the row's own
and the pairs counted are the row's own.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_u_m2():
    r"""``U + U(2) + <-2>``: rank five, ``|A_L| = 2``, so neither kernel row is the ambient one."""
    return Lattices(ZZ)("U") + Lattices(ZZ)(((0, 2), (2, 0))) + Lattices(ZZ)(((-2,),))


def _kernel_rows():
    r"""The two kernel rows of ``U + U(2) + <-2>``, with their quotient's plane row built."""
    lattice = _u_u_m2()
    stable = lattice.stable_orthogonal_group()
    return (
        (lattice, stable),
        (lattice, stable.intersection(lattice.O_plus())),
    )


def _registered_planes(subgroup):
    r"""One ``(plane, lift, element)`` per plane cusp of ``subgroup``'s row."""
    quotient = subgroup.finite_character_quotient()
    registered = []
    for cusp in subgroup.cusps(2):
        plane = cusp.representative()
        lift, element = quotient.registered_isotropic_lift(plane)
        assert element == quotient.isotropic_lift_discriminant_of(plane)
        assert lift == quotient.isotropic_lift_of(plane)
        registered.append((plane, lift, element))
    return registered


def _assert_register_is_the_finite_element(subgroup) -> None:
    r"""Assert that every plane of the row carries its lift's own ``rho``, and the product law."""
    registered = _registered_planes(subgroup)
    # Two plane cusps, so a per-plane datum and a per-row one are different numbers.
    first, second = registered
    assert first[0] != second[0]
    for plane, lift, element in registered:
        assert element == lift.discriminant_morphism()
    for plane, lift, element in registered:
        for other_plane, other_lift, other_element in registered:
            composite = lift * ~other_lift
            assert element * ~other_element == composite.discriminant_morphism()

def test_the_otilde_row_registers_the_finite_element_beside_the_lift() -> None:
    r"""``Otilde`` on ``U + U(2) + <-2>``: ``rho(s_P)`` is the registered element."""
    _lattice, subgroup = _kernel_rows()[0]
    _assert_register_is_the_finite_element(subgroup)


def test_the_otilde_plus_row_registers_the_finite_element_beside_the_lift() -> None:
    r"""``Otilde+`` on ``U + U(2) + <-2>``: ``rho(s_P)`` is the registered element."""
    _lattice, subgroup = _kernel_rows()[1]
    _assert_register_is_the_finite_element(subgroup)
