r"""A flag's stabilizer family is seeded from the parabolic at its own plane.

``OrthogonalCharacterQuotient.exact_isotropic_stabilizer_generators`` certifies
the finite image of the stabilizer of a representative: it bounds that image
above by the stabilizer of the representative's divided discriminant classes and
closes the image to the bound by exhibiting elements of the stabilizer.  The
family it starts from must therefore consist of elements of the stabilizer.

For a primitive isotropic flag $l \subset P$ the stabilizer is
$\mathrm{Stab}_{O(L)}(P) \cap \mathrm{Stab}_{O(L)}(l)$, by the definition of a
stabilizer, and $\mathrm{Stab}_{O(L)}(P)$ is the parabolic at the plane, whose
elements the plane's own block equations exhibit (D. Dutour Sikirić and
K. Hulek, *Moduli of polarised Enriques surfaces -- computational aspects*,
arXiv:2302.01679v2, Theorem 4.9, the block form of an isometry preserving an
isotropic plane).  What this file holds is that premise: an element of the
plane's parabolic family that carries the flag's line onto itself carries every
term of the flag onto itself.

$U + U(2) + \langle -2 \rangle$ is the specimen: its isotropic planes have a
parabolic family whose elements do not all preserve a given line in the plane,
so the restriction is not vacuous.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""$U + U(2) + \langle -2 \rangle$, the rank-five lattice of the line rows."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[-2]])
    )


def test_the_parabolic_at_the_plane_holds_the_elements_that_fix_the_line():
    r"""The parabolic's elements that stabilize the line stabilize the whole flag."""
    lattice = _specimen()
    flag = next(iter(lattice.Aut().isotropic_orbit_representatives(2, flag=True)))
    line, plane = tuple(flag.terms())

    stabilizing = tuple(
        generator
        for generator in plane.parabolic_stabilizer_generators()
        if line.stabilizes(generator)
    )

    assert sum(1 for _generator in stabilizing) > int(0)
    assert all(
        term.stabilizes(generator) for generator in stabilizing for term in flag.terms()
    )
    assert all(generator in lattice.Aut() for generator in stabilizing)


def test_an_element_of_the_parabolic_that_moves_the_line_is_not_used():
    r"""The restriction removes elements: some parabolic element moves the line."""
    lattice = _specimen()
    flag = next(iter(lattice.Aut().isotropic_orbit_representatives(2, flag=True)))
    line, plane = tuple(flag.terms())

    moving = tuple(
        generator
        for generator in plane.parabolic_stabilizer_generators()
        if not line.stabilizes(generator)
    )

    assert sum(1 for _generator in moving) > int(0)
    assert all(not line.stabilizes(generator) for generator in moving)
