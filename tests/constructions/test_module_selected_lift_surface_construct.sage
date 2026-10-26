r"""A represented module subobject inclusion retains its exact selected lift."""

from sage_extensions.all import *  # noqa: F401,F403


def test_coordinate_line_inclusion_has_constructor_exact_selected_lift() -> None:
    plane = ZZ.free_module(2)
    e0 = plane.module_generator(0)
    line = plane.subobject_on((e0,))
    inclusion = line.inclusion()

    assert inclusion.has_selected_lift()
    assert inclusion.selected_lift_exactness_decision() is True
    assert inclusion.lift(e0) == line.module_generator(0)
