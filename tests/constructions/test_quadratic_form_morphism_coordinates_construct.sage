r"""Quadratic-form morphisms retain coordinate data through polarization and pullback."""

from sage_extensions.all import *  # noqa: F401,F403


def _binary_quadratic_morphism():
    module = ZZ.free_module(2)
    quadratic = module.equip_quadratic_form(ZZ, [[1, 1], [0, 1]])
    return module, quadratic.form()


def test_quadratic_form_morphism_exposes_selected_lift_coordinates() -> None:
    module, morphism = _binary_quadratic_morphism()
    labels = module.module_generating_set()
    coordinates = morphism.lift_coordinate_values()

    assert coordinates(labels[0], labels[0]) == ZZ.one()
    assert coordinates(labels[0], labels[1]) == ZZ.one()


def test_quadratic_form_polar_coordinate_values_match_polarization() -> None:
    module, morphism = _binary_quadratic_morphism()
    polar = morphism.polar_form()
    coordinates = morphism.polar_coordinate_values()
    labels = polar.domain().module_generating_set()
    pair = labels[0]

    assert coordinates[pair] == polar(
        module.module_generator(pair.component(0)),
        module.module_generator(pair.component(1)),
    )


def test_quadratic_form_pullback_along_identity_preserves_values_and_lift() -> None:
    module, morphism = _binary_quadratic_morphism()
    identity = Modules(ZZ).Mor(module, module).identity()
    pulled = morphism.pullback(identity)
    e0 = module.module_generator(0)
    e1 = module.module_generator(1)

    assert pulled.module() is module
    assert pulled(e0 + e1) == morphism(e0 + e1)
    assert pulled.lift_pairing(e0, e1) == morphism.lift_pairing(e0, e1)
