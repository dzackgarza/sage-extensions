r"""Morphisms of commutative algebras given by generators and relations.

A morphism out of the polynomial algebra ``R[x_1, ..., x_n]`` is the same as a
choice of images of the variables, and a morphism out of ``R[x]/I`` is such a
choice that kills ``I`` (the universal properties of the polynomial ring and of
the quotient).  So the assignment ``x -> x + 1, y -> y``
on ``Q[x, y]/(xy)`` is not a morphism, since ``(x + 1) y = y`` is not zero there,
while ``x -> 0, y -> y`` from ``Q[x, y]/(xy)`` to ``Q[x, y]/(x)`` is one.

The coproduct of commutative algebras is the tensor product, so the coproduct of
``Q[x]`` and ``Q[y]`` is a polynomial ring in two variables whose two injections
commute, and a pair of maps out of the factors induces the unique map out of the
coproduct restricting to them.  The kernel of evaluation ``Q[x] -> Q`` at ``2`` is
the ideal ``(x - 2)``.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_a_morphism_out_of_a_polynomial_ring_is_a_choice_of_images() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations([x * y])
    projection = plane.Mor(axes)({"x": axes.algebra_generator("x"), "y": axes.algebra_generator("y")})

    assert projection(x * y) == axes.zero()
    assert projection(x + y) == axes.algebra_generator("x") + axes.algebra_generator("y")
    assert projection(x**2 * y + x**3) == projection(x) ** 3
    assert projection(x**2 * y + x**3) != axes.zero()


def test_swapping_the_variables_is_an_involution() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    swap = plane.Mor(plane)({"x": y, "y": x})

    assert swap(x**2 * y) == y**2 * x
    assert swap(x + 2 * y) == y + 2 * x
    assert (swap * swap)(x) == x
    assert swap * swap == plane.Mor(plane).identity()
    assert swap != plane.Mor(plane).identity()


def test_a_map_out_of_a_quotient_must_kill_the_relations() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    axes = plane.quotient_by_relations([x * y])
    line = plane.quotient_by_relations([x])
    restriction = axes.Mor(line)({"x": line.zero(), "y": line.algebra_generator("y")})

    assert restriction(axes.algebra_generator("x") * axes.algebra_generator("y")) == line.zero()
    assert restriction(axes.algebra_generator("x") + axes.algebra_generator("y")) == line.algebra_generator("y")
    with pytest.raises(ValueError):
        axes.Mor(axes)({"x": axes.algebra_generator("x") + axes.one(), "y": axes.algebra_generator("y")})


def test_reduction_of_integer_polynomials_modulo_six_at_t_equals_two() -> None:
    polynomials = ZZ["t"]
    t = polynomials.algebra_generator("t")
    residues = ZZ.ideal(ZZ(6)).quotient_ring()
    evaluation = polynomials.Mor(residues)({"t": residues(2)})

    assert evaluation(t**2) == residues(4)
    assert evaluation(t**3) == residues(2)
    assert evaluation(t**2 + t + 1) == residues(1)


def test_the_coproduct_of_two_polynomial_rings_is_the_polynomial_ring_in_both_variables() -> None:
    left = QQ["x"]
    right = QQ["y"]
    coproduct = Algebras(QQ).Associative().Unital().Commutative().coproduct((left, right))
    first = coproduct.coproduct_injection(0)
    second = coproduct.coproduct_injection(1)
    try:
        coproduct.coproduct_injection(QQ(1) / 2)
    except IndexError:
        pass
    else:
        assert False, "a nonintegral index was truncated into the left coproduct injection"
    x = left.algebra_generator("x")
    y = right.algebra_generator("y")

    assert first.domain() is left
    assert second.domain() is right
    assert first(x) * second(y) == second(y) * first(x)
    assert first(x) != second(y)
    assert first(x**2) == first(x) ** 2
    assert coproduct.krull_dimension() == 2


def test_a_pair_of_maps_induces_the_map_out_of_the_coproduct() -> None:
    left = QQ["x"]
    right = QQ["y"]
    coproduct = Algebras(QQ).Associative().Unital().Commutative().coproduct((left, right))
    target = QQ["t"]
    t = target.algebra_generator("t")
    to_square = left.Mor(target)({"x": t**2})
    to_cube = right.Mor(target)({"y": t**3})
    induced = coproduct.from_cocone(to_square, to_cube)

    assert induced * coproduct.coproduct_injection(0) == to_square
    assert induced * coproduct.coproduct_injection(1) == to_cube
    assert induced(coproduct.coproduct_injection(0)(left.algebra_generator("x")) * coproduct.coproduct_injection(1)(right.algebra_generator("y"))) == t**5


def test_the_kernel_of_evaluation_at_two_is_generated_by_x_minus_two() -> None:
    line = QQ["x"]
    x = line.algebra_generator("x")
    evaluation = line.Mor(QQ)({"x": QQ(2)})

    assert evaluation(x**3) == 8
    assert evaluation.kernel() == line.ideal(x - 2)
