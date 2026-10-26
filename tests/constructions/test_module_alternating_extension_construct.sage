r"""The generator inclusion into an exterior algebra extends through its universal property."""

from sage_extensions.all import *  # noqa: F401,F403


def test_generator_inclusion_extends_to_identity_on_exterior_algebra() -> None:
    module = QQ.free_module(2)
    exterior = module.exterior_algebra()
    inclusion = module.Mor(exterior)(
        {label: exterior.algebra_generator(label) for label in module.module_generating_set()}
    )
    extension = inclusion.alternating_extension()

    assert extension.domain() is exterior
    assert extension.codomain() is exterior
    for label in module.module_generating_set():
        generator = exterior.algebra_generator(label)
        assert extension(generator) == generator
