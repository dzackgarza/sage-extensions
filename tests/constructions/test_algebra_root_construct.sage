r"""The algebra root retains multiplication, scalar structure, ideals and derivations.

Polynomial algebras provide the commutative unital specimen; the coordinate
axes ``QQ[x,y]/(xy)`` provide a nontrivial generated ideal quotient; and the
family ``xy=t`` records the relative affine-family construction.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane():
    return QQ["x,y"]


def test_polynomial_algebra_retains_scalar_multiplication_and_structure_maps() -> None:
    algebra = _plane()
    x, y = algebra.algebra_generator("x"), algebra.algebra_generator("y")
    multiplication = algebra.multiplication()
    classifier = algebra.multiplication_morphism()
    underlying = algebra.underlying_module()
    tensor_square = underlying.tensor_product(underlying)

    assert algebra in Algebras(QQ)
    assert algebra.algebra_base_ring() is QQ
    assert algebra.algebra_structure_morphism()(QQ.one()) == algebra.one()
    assert algebra.product(x, y) == x * y
    assert multiplication(x, y) == x * y
    assert classifier(tensor_square.pure_tensor(x, y)) == x * y
    assert underlying in Modules(QQ)
    assert algebra.unformed_module() in Modules(QQ)
    assert isinstance(x, algebra.ElementType)


def test_polynomial_algebra_decisions_center_and_derivations_have_the_standard_values() -> None:
    algebra = _plane()
    x = algebra.algebra_generator("x")
    center = algebra.center()
    inclusion = algebra.center_inclusion()

    assert algebra.is_algebra()
    assert algebra.is_commutative()
    assert algebra.is_framed_algebra()
    assert algebra.associativity_decision() is True
    assert algebra.commutativity_decision() is True
    assert algebra.unit_laws_decision() is True
    assert algebra.alternation_decision() is False
    assert algebra.jacobi_decision() is False
    assert inclusion.domain() is center
    assert inclusion.codomain() is algebra
    assert inclusion.is_in_image(x)
    assert algebra.derivations(algebra.regular_module()).module_rank() == 2
    assert algebra.vector_fields().module_rank() == 2


def test_coordinate_axes_are_the_quotient_by_the_generated_algebra_ideal() -> None:
    algebra = _plane()
    x, y = algebra.algebra_generator("x"), algebra.algebra_generator("y")
    ideal = algebra.ideal(x * y)
    generated = algebra.algebra_ideal_generated_by(ideal)
    quotient = algebra.quotient_by_algebra_ideal(generated)
    by_generated = algebra.quotient_by_generated_algebra_ideal(ideal)
    projection = quotient.algebra_quotient_projection()

    assert generated == ideal
    assert quotient.algebra_quotient_ideal() == ideal
    assert projection.domain() is algebra
    assert projection.codomain() is quotient
    assert projection(x * y) == quotient.zero()
    assert by_generated.algebra_generator("x") * by_generated.algebra_generator("y") == by_generated.zero()


def test_scalar_restriction_changes_only_the_algebra_base_ring() -> None:
    algebra = QQ["x"]
    inclusion = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    restricted = algebra.restrict_scalars(inclusion)

    assert restricted in Algebras(ZZ)
    assert restricted.algebra_base_ring() is ZZ
    assert restricted.algebra_generator("x") in restricted


def test_parameter_algebra_builds_the_xy_equals_t_affine_family() -> None:
    parameter = QQ["t"]
    t = parameter.algebra_generator("t")
    family = parameter.affine_equation_family(
        ("x", "y"),
        lambda presentation: (
            presentation.algebra_generator("x") * presentation.algebra_generator("y") - presentation(t),
        ),
    )

    assert family.structure_morphism().codomain() is family.base_scheme()
    assert family.is_flat()


def test_algebra_morphisms_have_identity() -> None:
    algebra = _plane()
    identity = algebra.Mor(algebra).identity()

    assert identity(algebra.algebra_generator("x")) == algebra.algebra_generator("x")
    assert identity * identity == identity
