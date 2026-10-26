r"""Ideals, units and kernels under localization of a polynomial ring and of the node."""

from sage_extensions.all import *  # noqa: F401,F403


def test_generated_localization_extension_and_contraction_are_the_same_ideal() -> None:
    ring = QQ.polynomial_ring(("x", "y"))
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    ideal = ring.ideal(y)
    localization = ring.localization(x)

    extended = ideal.extension_to_localization(localization)
    contracted = extended.contraction_from_localization()

    assert extended.ring() is localization
    assert contracted.ring() is ring
    assert contracted == ideal


def test_prime_local_units_and_residue_map_use_the_selected_local_ring() -> None:
    ring = QQ.polynomial_ring(("x",))
    x = ring.algebra_generator("x")
    point = ring.spectrum()(ring.ideal(x))
    local = point.local_ring()
    include = local.localization_map()

    assert not include(x).is_unit()
    assert include(ring.one() + x).is_unit()
    assert point.residue_map()(x) == point.residue_field().zero()
    assert local.residue_map()(include(x)) == point.residue_field().zero()
    assert local.source_residue_map()(x) == point.residue_map()(x)


def test_multiplication_by_x_on_the_local_ring_of_the_node_has_kernel_generated_by_y() -> None:
    r"""On ``A = QQ[x, y]/(xy)`` the annihilator of ``x`` is ``yA``, and ``y/1`` is
    nonzero in ``A_m`` at ``m = (x, y)`` because ``Ann(y) = (x)`` lies in ``m``.
    Localization is exact, so the kernel of ``x`` on ``A_m`` is the localization
    of the kernel of ``x`` on ``A`` (Atiyah--Macdonald, Prop. 3.3)."""
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    node = plane.quotient_by_relations([x * y])
    a = node.algebra_generator("x")
    b = node.algebra_generator("y")
    point = node.spectrum()(node.ideal(a, b))
    to_local = point.local_ring().localization_map()

    module = Modules(node).free_module(("g",))
    g = module.module_generator("g")
    times_x = module.Mor(module)({"g": a * g})
    local = module.localize_at_prime(point)
    local_times_x = local.localization_functor()(times_x)
    kernel = local_times_x.kernel()
    local_g = local.module_generator("g")

    assert to_local(b) != point.local_ring().zero()
    assert kernel.inclusion().is_in_image(to_local(b) * local_g)
    assert not kernel.inclusion().is_in_image(local_g)
    assert not kernel.inclusion().is_in_image(to_local(a) * local_g)
    assert kernel == times_x.kernel().localize_at_prime(point)
