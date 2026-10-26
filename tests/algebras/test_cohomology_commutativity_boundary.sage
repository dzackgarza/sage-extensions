r"""Cohomology of differential graded algebras with zero differential."""

from sage_extensions.all import *  # noqa: F401,F403


def _free_associative_dga():
    r"""``ZZ<x, y>`` with ``|x| = |y| = 1`` and ``d = 0``, so ``H = ZZ<x, y>``."""
    tensor = Modules(ZZ).free_module(("x", "y")).tensor_algebra()
    x = tensor.algebra_generator("x")
    y = tensor.algebra_generator("y")
    dga = DifferentialGradedAlgebras(ZZ)(tensor, {x: tensor.zero(), y: tensor.zero()})
    return dga, dga(x), dga(y)


def test_cohomology_of_the_free_associative_dga_is_noncommutative() -> None:
    r"""With ``d = 0``, ``H(ZZ<x,y>) = ZZ<x,y>``, so ``[x][y] ≠ ±[y][x]``: cohomology of
    a DGA need not be graded-commutative."""
    dga, x, y = _free_associative_dga()
    cohomology = dga.cohomology_algebra()
    x_class = cohomology.class_of(x)
    y_class = cohomology.class_of(y)

    assert x_class * y_class != y_class * x_class
    assert x_class * y_class != -(y_class * x_class)
    assert x_class * y_class != cohomology.zero()


def test_swap_of_generators_induces_the_swap_on_cohomology() -> None:
    r"""``H`` is a functor: ``σ : x ↔ y`` induces ``H(σ)`` with ``H(σ)[x] = [y]``,
    ``H(σ)([x][y]) = [y][x]`` and ``H(σ)^2 = id``."""
    dga, x, y = _free_associative_dga()
    swap = dga.Mor(dga)({x: y, y: x})
    cohomology = dga.cohomology_algebra()
    induced = DifferentialGradedAlgebras(ZZ).cohomology_algebra()(swap)
    x_class = cohomology.class_of(x)
    y_class = cohomology.class_of(y)

    assert induced(x_class) == y_class
    assert induced(y_class) == x_class
    assert induced(x_class * y_class) == y_class * x_class
    assert induced(induced(x_class * y_class)) == x_class * y_class


def test_a_degree_one_class_over_gf2_can_have_nonzero_square() -> None:
    r"""Over ``GF(2)``, ``GF(2)[x]`` with ``|x| = 1`` and ``d = 0`` is graded-commutative
    (signs are trivial) but ``[x]^2 = [x^2] ≠ 0``: graded commutativity does not
    force odd classes to square to zero in characteristic 2."""
    polynomial = Modules(GF(2)).free_module(("x",)).symmetric_algebra()
    x = polynomial.algebra_generator("x")
    dga = DifferentialGradedAlgebras(GF(2))(polynomial, {x: polynomial.zero()})
    cohomology = dga.cohomology_algebra()
    x_class = cohomology.class_of(dga(x))

    assert dga(x).degree() == 1
    assert x_class * x_class != cohomology.zero()
    assert x_class * x_class * x_class != cohomology.zero()


def test_euler_derivation_of_the_free_associative_algebra_multiplies_by_word_length() -> None:
    r"""The derivation ``E`` with ``E(x) = x``, ``E(y) = y`` on ``ZZ<x, y>`` acts on a
    word of length ``n`` by ``n``: ``E(xy) = 2xy``, ``E(xyx) = 3xyx`` (Leibniz rule)."""
    tensor = Modules(ZZ).free_module(("x", "y")).tensor_algebra()
    x = tensor.algebra_generator("x")
    y = tensor.algebra_generator("y")
    euler = tensor.derivations()({x: x, y: y})

    assert euler(x * y) == 2 * x * y
    assert euler(x * y * x) == 3 * x * y * x
    assert euler(x * y + y) == 2 * x * y + y
