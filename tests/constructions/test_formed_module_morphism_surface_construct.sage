r"""A fixed-fibre formed morphism retains its module and value maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _formed_identity():
    form = NamedLattices.U
    module = form.unformed_module()
    values = form.value_module()
    module_identity = Modules(ZZ).Mor(module, module).identity()
    value_identity = values.Mor(values).identity()
    formed = form.formed_mor(module_identity, value_identity)
    return module, values, module_identity, value_identity, formed


def test_formed_identity_retains_module_and_value_maps() -> None:
    _module, _values, module_identity, value_identity, formed = _formed_identity()

    assert formed.module_morphism() is module_identity
    assert formed.value_morphism() is value_identity
    assert formed.preserves_form_exactly()
    assert formed.is_injective()


def test_formed_identity_maps_value_elements_identically() -> None:
    _module, values, _module_identity, _value_identity, formed = _formed_identity()
    value = values.module_generator(0)

    assert formed.map_value(value) == value
