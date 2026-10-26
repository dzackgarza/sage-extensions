r"""The two linearizations of ``O(1)`` on ``P^1`` under the coordinate swap."""

from sage_extensions.all import *  # noqa: F401,F403


def linearizations():
    r"""``P^1`` with coordinates ``x, y``, ``O(1)``, and its trivial and sign linearizations."""
    line = ProjectiveSpaces(QQ)(1, names=("x", "y"))
    bundle = line.O(1)
    swap = ProjectiveLines(QQ)(line).coordinate_swap_action()
    group = swap.acting_group()
    trivial_character = group.trivial_character()
    sign_character = next(
        chi for chi in group.irreducible_characters() if chi != trivial_character
    )
    trivial = bundle.linearize(swap, trivial_character)
    sign = bundle.linearize(swap, sign_character)
    involution = next(g for g in group if g != group.one())
    return line, bundle, trivial, sign, sign_character, involution


def symmetric_and_alternating(bundle):
    r"""The sections ``x + y`` and ``x - y`` of ``O(1)``."""
    sections = bundle.global_sections()
    ring = sections.homogeneous_coordinate_ring()
    x, y = ring("x"), ring("y")
    return (
        sections.section_from_homogeneous_polynomial(x + y),
        sections.section_from_homogeneous_polynomial(x - y),
    )


def test_two_character_twists_keep_same_bundle_but_swap_section_eigenspaces() -> None:
    r"""The trivial linearization fixes ``x + y`` and negates ``x - y``; the sign twist does the opposite."""
    _line, bundle, trivial, sign, _sign_character, g = linearizations()
    symmetric, alternating = symmetric_and_alternating(bundle)

    assert trivial.section_action_of(g)(symmetric) == symmetric
    assert trivial.section_action_of(g)(alternating) == -alternating
    assert sign.section_action_of(g)(symmetric) == -symmetric
    assert sign.section_action_of(g)(alternating) == alternating


def test_fixed_point_fiber_evaluation_is_equivariant_and_detects_character_twist() -> None:
    r"""At the fixed point ``(1:1)`` the swap acts on the fibre by ``+1`` (trivial) and ``-1`` (sign)."""
    line, _bundle, trivial, sign, _sign_character, g = linearizations()
    point = line.point_morphism((1, 1))
    trivial_fiber = trivial.fixed_point_fiber_evaluation(point).codomain()
    sign_fiber = sign.fixed_point_fiber_evaluation(point).codomain()
    (v,) = trivial_fiber.basis()
    (w,) = sign_fiber.basis()

    assert trivial.point_is_fixed(point)
    assert not trivial.point_is_fixed(line.point_morphism((1, 0)))
    assert trivial_fiber.act(g, v) == v
    assert sign_fiber.act(g, w) == -w


def test_sign_eigensection_has_invariant_zero_divisor() -> None:
    r"""``x - y`` is a sign eigensection of ``O(1)``; its zero divisor ``V(x - y) = {(1:1)}`` is swap-invariant."""
    line, bundle, trivial, _sign, sign_character, _g = linearizations()
    symmetric, alternating = symmetric_and_alternating(bundle)
    ring = bundle.global_sections().homogeneous_coordinate_ring()

    divisor = trivial.eigensection_divisor(alternating, sign_character)

    assert trivial.is_eigensection(alternating, sign_character)
    assert not trivial.is_eigensection(symmetric, sign_character)
    assert trivial.is_eigensection_divisor(divisor)
    assert divisor == line.closed_subscheme(ring("x") - ring("y"))
    assert divisor.contains_point(line.point((1, 1)))
    assert not divisor.contains_point(line.point((1, -1)))


def test_cohomology_of_O_1_on_P1_as_a_representation_of_the_swap() -> None:
    r"""``H^0(P^1, O(1)) = triv + sign`` has rank 2 and invariants of rank 1; ``H^1 = 0``."""
    _line, _bundle, trivial, sign, _sign_character, _g = linearizations()
    h0 = trivial.coherent_cohomology_group_module(0)
    h1 = trivial.coherent_cohomology_group_module(1)

    assert h0.coefficient_module_rank() == 2
    assert h0.invariants().module_rank() == 1
    assert sign.coherent_cohomology_group_module(0).invariants().module_rank() == 1
    assert h1.coefficient_module_rank() == 0


def test_restriction_to_the_fixed_point_is_equivariant_with_kernel_the_alternating_section() -> None:
    r"""``H^0(P^1, O(1)) -> H^0({x = y}, O(1))`` is equivariant onto rank 1, with kernel spanned by ``x - y``."""
    _line, bundle, trivial, _sign, sign_character, _g = linearizations()
    _symmetric, alternating = symmetric_and_alternating(bundle)
    divisor = trivial.eigensection_divisor(alternating, sign_character)

    restriction = trivial.equivariant_section_restriction(divisor)

    assert restriction.codomain().coefficient_module_rank() == 1
    assert restriction.parent().is_equivariant(restriction)
    assert restriction.kernel().coefficient_module_rank() == 1
