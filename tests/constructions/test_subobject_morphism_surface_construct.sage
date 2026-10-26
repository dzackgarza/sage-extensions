r"""A morphism of subobjects is the unique factor making the inclusions commute."""

from sage_extensions.all import *  # noqa: F401,F403


def _coordinate_line_in_plane():
    module = ZZ.free_module(2)
    e0, e1 = module.module_generator(0), module.module_generator(1)
    line = module.subobject_on((e0,))
    plane = module.subobject_on((e0, e1))
    category = Modules(ZZ).Subobjects(module)
    arrow = category.Mor(line, plane).canonical_morphism()
    return line, plane, arrow


def test_subobject_morphism_retains_its_factor_map() -> None:
    line, plane, arrow = _coordinate_line_in_plane()
    generator = line.module_generator(0)
    factor = arrow.factor_morphism()

    assert factor.domain() is line
    assert factor.codomain() is plane
    assert arrow(generator) == factor(generator)


def test_subobject_morphism_makes_the_inclusion_triangle_commute() -> None:
    line, plane, arrow = _coordinate_line_in_plane()
    generator = line.module_generator(0)

    assert plane.inclusion()(arrow(generator)) == line.inclusion()(generator)
    assert arrow.parent().has_morphism()


def test_subobject_morphism_composition_composes_factor_maps() -> None:
    line, _plane, arrow = _coordinate_line_in_plane()
    identity = line.Mor(line).identity()
    composite = arrow * identity

    assert composite.factor_morphism() == (
        arrow.factor_morphism() * identity.factor_morphism()
    )
