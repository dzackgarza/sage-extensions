r"""The semigroup algebra of an affine monoid.

Every test takes its names from the session: the suite's lint (TL01) admits no
module import beside it, so the algebra categories are the session's
``AffineSemigroupAlgebras``, ``FreeAlgebras`` and ``SymmetricAlgebras`` and the
coefficient ring is the session's ``ZZ``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_linearly_independent_semigroup_generators_give_the_polynomial_algebra() -> None:
    r"""An injective degree map N^2 -> Z^2 has zero toric ideal."""
    algebra = AffineSemigroupAlgebras(ZZ)(((1, 0), (0, 1)), names=("x", "y"))

    assert algebra in AffineSemigroupAlgebras(ZZ)
    assert algebra in FreeAlgebras(ZZ)
    assert algebra in SymmetricAlgebras(ZZ)
    assert algebra.algebra_generating_set().cardinality() == 2
    coordinates = algebra.affine_semigroup_generator_coordinates()
    assert tuple(
        tuple(int(value) for value in coordinates[label])
        for label in coordinates.index_set()
    ) == ((1, 0), (0, 1))
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
    algebra = AffineSemigroupAlgebras(ZZ)(((1, 0), (0, 1), (1, 1)), names=("x", "y", "z"))
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    z = algebra.algebra_generator("z")

    assert z == x * y
    assert z * z == x**2 * y**2
    assert z != x
    assert x != y
    assert x * y == y * x
    assert x + y != z


def test_a_semigroup_algebra_keeps_its_identity_after_a_polynomial_ring_is_built() -> None:
    r"""``QQ[S]``'s identity and augmentation are arrows of its own ``Mor``.

    ``QQ[S]`` for ``S = <(1,0), (0,1)>`` is free on its two generators, so the
    degree-zero resolution it selects is the algebra itself and its
    augmentation is the identity.  That arrow is an arrow of the algebra's own
    ``QQ[S].Mor(QQ[S])``, the graded-algebra Mor of its category, whatever the
    session built before it.
    """
    QQ.polynomial_ring("y")
    algebra = AffineSemigroupAlgebras(QQ)(((1, 0), (0, 1)),)
    generator = algebra.algebra_generator(next(iter(algebra.algebra_generating_set())))

    identity = algebra.Mor(algebra).identity()
    assert identity(generator) == generator
    augmentation = algebra.algebra_framing_morphism()
    assert augmentation.parent() is algebra.Mor(algebra)
    assert augmentation in algebra.Mor(algebra)
    assert augmentation == identity
    assert augmentation(generator) == generator
    assert augmentation(generator * generator) == generator * generator


def test_a_free_semigroup_algebra_presents_itself_in_a_fresh_session() -> None:
    r"""``QQ[S]`` in a session that built nothing before it.

    ``QQ[S]`` for ``S = <(1,0), (0,1)>`` is the free commutative algebra on
    its two generators, so it is an algebra with a chosen finite presentation:
    its own generators and no relations.  In that session its arrows are the
    framed free-algebra arrows, its identity and the augmentation of its
    degree-zero resolution are arrows of ``QQ[S].Mor(QQ[S])``, it is its own
    presentation ring with no relations, and its quotient by ``s0 s1`` is
    presented on ``QQ[S]`` by that one relation, in which ``s0 s1 = 0`` while
    ``s0`` and ``s0^2`` are not zero.

    Sage orders the parent classes of two categories that are not
    subcategories of each other by the order the session built them, so the
    script runs in its own process; ``conftest.py`` holds it and the runner.
    """
    run = session_order_run(polynomial_ring_first=False)

    assert run.returncode == 0, run.stderr


def test_a_free_semigroup_algebra_presents_itself_after_a_polynomial_ring_is_built() -> None:
    r"""``QQ[S]`` in a session that built ``QQ[y]`` first.

    The same assertions as in a fresh session, in the other construction
    order: building a polynomial ring first constructs the free-algebra
    categories before the categories of algebras with a chosen finite
    presentation, and no answer about ``QQ[S]`` may depend on that.
    """
    run = session_order_run(polynomial_ring_first=True)

    assert run.returncode == 0, run.stderr
