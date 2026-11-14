r"""The radical quotient of a rational lattice, and its lattice presentation.

For a symmetric bilinear space ``(V, b)`` over ``QQ`` with radical ``R``, the
quotient ``V/R`` has dimension ``dim V - dim R``, the projection
``p: V -> V/R`` has kernel ``R``, and the descended form ``b̄`` satisfies
``b = b̄ ∘ (p ⊗ p)``.  The lattice presentation of the quotient is the same
formed module, so it has the same rank and the same form.
"""

from sage_extensions.all import *


def test_the_coordinate_radical_quotient_is_a_hyperbolic_plane() -> None:
    lattice = Lattices(QQ)([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
    quotient = lattice.radical_quotient()
    projection = lattice.radical_quotient_projection()

    assert lattice.radical().module_rank() == 1
    assert quotient.module_rank() == 2
    assert projection.domain() is lattice
    assert projection.codomain() is quotient
    assert projection.module_morphism().kernel().module_rank() == 1
    radical = lattice.radical()
    for label in radical.module_generating_set():
        assert projection(radical.inclusion()(radical.module_generator(label))) == quotient.zero()
    for left in lattice.module_generators():
        for right in lattice.module_generators():
            assert quotient.b(projection(left), projection(right)) == lattice.b(left, right)

    presented = Lattices(QQ)(quotient)
    assert presented.module_rank() == 2
    assert presented.determinant() == -1
    assert presented.is_isometric_to(Lattices(QQ)([[0, 1], [1, 0]]))


def test_a_non_coordinate_radical_descends_to_the_diagonal_form_two_three() -> None:
    r"""``B = [[2,2,0],[2,2,0],[0,0,3]]`` has radical ``QQ(1,-1,0)``; ``p(x,y,z) = (x+y, z)`` and ``b̄ = diag(2,3)``."""
    lattice = Lattices(QQ)([[2, 2, 0], [2, 2, 0], [0, 0, 3]])
    first, second, third = lattice.module_generators()
    quotient = lattice.radical_quotient()
    projection = lattice.radical_quotient_projection()

    assert lattice.radical().module_rank() == 1
    assert quotient.module_rank() == 2
    assert projection(first) == projection(second)
    assert projection(first) != quotient.zero()
    assert quotient.b(projection(first), projection(first)) == 2
    assert quotient.b(projection(third), projection(third)) == 3
    assert quotient.b(projection(first), projection(third)) == 0
    for left in lattice.module_generators():
        for right in lattice.module_generators():
            assert quotient.b(projection(left), projection(right)) == lattice.b(left, right)

    presented = Lattices(QQ)(quotient)
    assert presented.module_rank() == 2
    assert presented.determinant() == 6
    assert presented.is_isometric_to(Lattices(QQ)([[2, 0], [0, 3]]))
