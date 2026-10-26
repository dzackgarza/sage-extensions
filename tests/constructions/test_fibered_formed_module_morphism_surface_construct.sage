r"""A fibrewise formed morphism retains its scalar, module, and value maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _fibered_formed_identity():
    form = NamedLattices.U
    module = form.unformed_module()
    values = form.value_module()
    ring_identity = ZZ.Mor(ZZ).identity()
    module_identity = Modules(ZZ).Mor(module, module).identity()
    value_identity = values.Mor(values).identity()
    fibered = form.fibered_formed_mor(
        form,
        ring_identity,
        module_identity,
        value_identity,
    )
    return form, module, values, ring_identity, module_identity, value_identity, fibered


def test_fibered_formed_identity_retains_ring_module_and_value_maps() -> None:
    form, _module, _values, ring_identity, module_identity, value_identity, fibered = (
        _fibered_formed_identity()
    )

    assert fibered.ring_map() is ring_identity
    assert fibered.base_changed_domain() is form
    assert fibered.module_morphism() is module_identity
    assert fibered.value_morphism() is value_identity


def test_fibered_formed_identity_forgets_to_the_identity_semilinear_map_and_value_action() -> None:
    _form, module, values, _ring_identity, _module_identity, _value_identity, fibered = (
        _fibered_formed_identity()
    )
    generator = module.module_generator(0)
    value_generator = values.module_generator(0)
    underlying = fibered.underlying_semilinear_morphism()

    assert underlying(generator) == generator
    assert fibered.map_value(value_generator) == value_generator
