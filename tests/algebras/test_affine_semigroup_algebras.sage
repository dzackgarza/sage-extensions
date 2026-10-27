r"""The semigroup algebra of an affine monoid."""

from sage_extensions.all import *  # noqa: F401,F403


def test_linearly_independent_semigroup_generators_give_the_polynomial_algebra() -> None:
    r"""An injective degree map N^2 -> Z^2 has zero toric ideal."""
    algebra = Algebras(ZZ).semigroup_algebra(((1, 0), (0, 1)), names=("x", "y"))

    assert algebra in FreeAlgebras(ZZ)
    assert algebra in SymmetricAlgebras(ZZ)
    assert algebra.algebra_generating_set().cardinality() == 2
    coordinates = algebra.affine_semigroup_generator_coordinates()
    assert tuple(tuple(int(value) for value in coordinates[label]) for label in coordinates.index_set()) == (
        (1, 0),
        (0, 1),
    )
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    assert x * y == y * x
    assert x != y


def test_semigroup_algebra_of_the_monoid_generated_by_e1_e2_and_their_sum_satisfies_z_equals_xy() -> None:
    r"""In ``ZZ[S]`` for ``S = <(1,0), (0,1), (1,1)>`` the monomials multiply by adding exponents.

    Since ``(1,1) = (1,0) + (0,1)`` in ``S``, the generator ``z = t^(1,1)`` equals
    ``xy``; since ``S = NN^2`` the algebra is the polynomial ring in ``x, y``.
    Derivation: ``t^a t^b = t^(a+b)`` in a semigroup algebra.
    """
    algebra = Algebras(ZZ).semigroup_algebra(((1, 0), (0, 1), (1, 1)), names=("x", "y", "z"))
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    z = algebra.algebra_generator("z")

    assert z == x * y
    assert z * z == x**2 * y**2
    assert z != x
    assert x != y
    assert x * y == y * x
    assert x + y != z
