r"""The orthogonal group of a lattice with a null plane has isometry generators.

\(L = U \oplus U(2) \oplus \langle -2 \rangle\) has rank five and signature
\((2,3)\), and the indefinite port computes a generating set of \(O(L)\) by
transports through pointed isometries.  Each generator is an isometry of \(L\):
it is a map of \(L\) onto itself that preserves the form, which is what makes
the set a set of generators of the orthogonal group rather than of a larger
group of maps.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_generators_preserve_the_form_on_the_generators() -> None:
    r"""Every generator fixes the form, pairwise, on the generators of \(L\)."""
    lattice = (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U").twist(2)
        + Lattices(ZZ)([[-2]])
    )
    group = lattice.stable_orthogonal_group()
    group_generators = tuple(group.group_generators())
    basis = tuple(lattice.module_generators())

    assert group_generators
    for generator in group_generators:
        assert generator.domain() is lattice
        assert generator.codomain() is lattice
        for left in basis:
            for right in basis:
                assert lattice.b(generator(left), generator(right)) == lattice.b(left, right)
