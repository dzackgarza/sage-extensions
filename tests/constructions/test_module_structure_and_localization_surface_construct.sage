r"""Modules expose their selected framing status, scalar action, generic fibre, and prime localization."""

from sage_extensions.all import *  # noqa: F401,F403


def test_framed_free_integer_module_reports_module_structure_and_scalar_action() -> None:
    module = ZZ.free_module(2)
    e0 = module.module_generator(0)
    action = module.scalar_action()

    assert module.is_module()
    assert module.is_framed_module()
    assert action(ZZ(3))(e0) == 3 * e0


def test_free_integer_line_generic_fibre_map_is_injective_into_a_rational_line() -> None:
    module = ZZ.free_module(1)
    generic = ModulesOverIntegralDomains(ZZ)(module).generic_fibre_map()

    assert generic.domain() is module
    assert generic.codomain().base_ring() is QQ
    assert generic.is_injective()


def test_polynomial_line_localization_at_origin_has_local_base_ring() -> None:
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    prime = ring.ideal(x)
    module = ring.free_module(1)
    localized = module.localization_at_prime(prime)

    assert localized.base_ring() == ring.localization_at_prime(prime)
    assert localized.base_ring().is_local()
