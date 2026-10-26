r"""The hyperbolic plane is glued from two orthogonal primitive lines by a discriminant anti-isometry."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_primitive_complement_glue_map_has_order_two_source_and_target() -> None:
    ambient = NamedLattices.U
    first_generator, second_generator = ambient.module_generators()
    first = ambient.subobject_on((first_generator + second_generator,))
    second = ambient.subobject_on((first_generator - second_generator,))
    glue = ambient.glue_map(first, second)

    assert first.is_primitive()
    assert second.is_primitive()
    assert first.sum(second).index() == 2
    assert glue.domain().cardinality() == cardinal(2)
    assert glue.codomain().cardinality() == cardinal(2)
