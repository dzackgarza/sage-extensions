r"""The Gamma_{Co,2} plane row on T_Co, through the public call (#381).

`T_Co = <2> + U(2) + E8(-2)` is the Coble period lattice, D. Dolgachev and
S. Kondo, *Enriques surfaces and Borel--Weil--Bott type duality*, Izv. Math.
77:3 (2013), section 3, equation (3.6), printed p. 513, with `E8` negative
definite as the source's signature `(2, 9)` forces.  `Gamma_{Co,2} =
rho^{-1}(P)` is the preimage of the stabilizer `P` of `A_{U(2)}` in `O(q)`
(research `prop:gamma-co-images`), and the row this file exercises is its
orbits of primitive isotropic planes through the public call
`isotropic_orbit_representatives(2)`.

**The route.**  For each `O(T_Co)`-orbit of planes — there is one — the
`Gamma`-orbits inside it are the double cosets
`rho(Gamma) \\ rho(O(T_Co)) / rho(Stab(P))` (D. Dutour Sikirić and K. Hulek,
*Moduli of polarised Enriques surfaces -- computational aspects*, J. London
Math. Soc. 110 (2024), arXiv:2302.01679v2, Lemma 3.6, printed p. 22), and the
right-hand group `rho(Stab(P))` is supplied by the plane's own parabolic: the
block equations of Theorem 4.9 (printed pp. 33--34) are solved over `ZZ` at
any primitive isotropic plane, and `is_parabolic_complete` decides on three
computed indices whether the family they produce is the whole stabilizer
(#331, #366).  Where it is, the double cosets are computed from that family
by `splitting_isometries`, which walks `rho(Gamma)`-orbits on the coset
space, not the group.

**What is asserted.**  No count is typed: no lattice-database card holds a
`T_Co` value yet (lattice-database#7, which waits on this library's Coble
rows).  The assertion is what the cited construction guarantees for every
output: each representative is a primitive totally isotropic plane of
`T_Co`.

**What does not return, and why.**  The `Otilde(T_Co)` and `Otilde+(T_Co)`
plane rows and the Tits-building incidence are measured, not asserted here:
the two kernel rows' double cosets number `189720` each and the representative
realization at the measured rate of about one second per double coset is
beyond the test budget, and the incidence's flag route reaches the indefinite
port's generic stabilizer enumeration, which is killed at the memory guard on
this lattice.  The three counts and the obstruction are recorded in the
commit body of the push that lands this file.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + U(2) + E8(-2)``: Dolgachev--Kondo (3.6), p. 513."""
    return NamedLattices.Tco


def _span(form, family):
    r"""The span of a finite family of classes of `A_L` over `ZZ/2ZZ`, as a set."""
    closure = {form.zero()}
    for generator in family:
        closure |= {element + generator for element in closure}
    return frozenset(closure)


def _classes(lattice):
    r"""One class of `A_L` per named module generator: the primitive dual's class."""
    return {
        label: lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator(label)))
        for label in lattice.module_generating_set()
    }


def _decomposition(lattice):
    r"""`A_{U(2)}`, the span of the `U(2)`-generators' classes in `A_{T_Co}`."""
    form = lattice.discriminant_group()
    classes = _classes(lattice)
    return _span(form, (classes["ep"], classes["fp"]))


def _assert_primitive_isotropic_plane(lattice, plane) -> None:
    r"""``plane`` is a rank-two primitive totally isotropic subobject of ``lattice``."""
    assert plane.inclusion().codomain() is lattice
    assert plane.module_rank() == cardinal(2)
    assert plane.is_primitive() is True
    points = tuple(plane.inclusion().domain().module_generators())
    assert all(
        lattice.b(plane.inclusion()(left), plane.inclusion()(right)) == ZZ.zero()
        for left in points
        for right in points
    )


def test_the_coble_gamma_co_2_plane_row_returns() -> None:
    r"""The Gamma_{Co,2} plane row returns primitive isotropic planes of T_Co."""
    lattice = _coble_lattice()
    A_U2 = _decomposition(lattice)
    subgroup = lattice.Aut().discriminant_point_stabilizer(A_U2)

    planes = tuple(subgroup.isotropic_orbit_representatives(2))

    for plane in planes:
        _assert_primitive_isotropic_plane(lattice, plane)
