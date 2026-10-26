r"""The tensor and symmetric algebras of ``V = Q^2`` with basis ``a, b``.

``T(V)`` is the free associative algebra on ``a, b``: it is associative and unital,
``ab != ba``, and an algebra map out of it is any choice of images of ``a`` and
``b`` (its universal property).  So the swap ``a <-> b`` is an involution of
``T(V)``, and ``T(V) -> Q[a, b]`` sending each letter to itself kills the
commutator ``ab - ba``: ``Sym(V) = T(V)/(ab - ba)`` is the polynomial ring
``Q[a, b]``, commutative of Krull dimension two.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_tensor_algebra_is_associative_unital_and_noncommutative() -> None:
    tensor = QQ.free_module(("a", "b")).tensor_algebra()
    a = tensor.algebra_generator("a")
    b = tensor.algebra_generator("b")

    assert tensor.algebra_framing_source() is tensor
    assert tensor.algebra_framing_morphism() is tensor.Mor(tensor).identity()
    assert tensor.algebra_generator("a") == tensor.algebra_framing_morphism()(
        tensor.algebra_framing_source().algebra_generator("a")
    )
    resolution = tensor.selected_algebra_resolution()
    assert resolution.target() is tensor
    assert resolution.generating_set() == tensor.algebra_generating_set()
    assert resolution.generator_morphism().domain() is tensor.algebra_generating_set()
    assert resolution.generator_morphism().codomain() is tensor
    assert resolution.generator_morphism()("a") == tensor.algebra_generator("a")
    assert a * b != b * a
    assert (a * b) * a == a * (b * a)
    assert tensor.one() * a == a
    assert not tensor.is_commutative()


def test_swapping_the_letters_is_an_involution_of_the_tensor_algebra() -> None:
    tensor = QQ.free_module(("a", "b")).tensor_algebra()
    a = tensor.algebra_generator("a")
    b = tensor.algebra_generator("b")
    swap = tensor.Mor(tensor)({"a": b, "b": a})

    assert swap(a * b) == b * a
    assert swap(a * a * b) == b * b * a
    assert (swap * swap)(a * a * b) == a * a * b


def test_abelianizing_the_tensor_algebra_kills_the_commutator() -> None:
    tensor = QQ.free_module(("a", "b")).tensor_algebra()
    a = tensor.algebra_generator("a")
    b = tensor.algebra_generator("b")
    polynomials = QQ["a, b"]
    abelianization = tensor.Mor(polynomials)(
        {"a": polynomials.algebra_generator("a"), "b": polynomials.algebra_generator("b")}
    )

    assert abelianization(a * b - b * a) == polynomials.zero()
    assert abelianization(a * b) == polynomials.algebra_generator("a") * polynomials.algebra_generator("b")
    assert abelianization(a + b) != polynomials.zero()


def test_the_symmetric_algebra_of_the_plane_is_a_polynomial_ring_in_two_variables() -> None:
    symmetric = QQ.free_module(("a", "b")).symmetric_algebra()
    a = symmetric.algebra_generator("a")
    b = symmetric.algebra_generator("b")

    assert symmetric.algebra_framing_source() is symmetric
    assert symmetric.algebra_framing_morphism() is symmetric.Mor(symmetric).identity()
    assert symmetric.algebra_generator("a") == symmetric.algebra_framing_morphism()(
        symmetric.algebra_framing_source().algebra_generator("a")
    )
    resolution = symmetric.selected_algebra_resolution()
    assert resolution.target() is symmetric
    assert resolution.generator_morphism().domain() is symmetric.algebra_generating_set()
    assert resolution.generator_morphism().codomain() is symmetric
    assert resolution.generator_morphism()("b") == symmetric.algebra_generator("b")
    assert symmetric.is_commutative()
    assert a * b == b * a
    assert symmetric.krull_dimension() == 2
