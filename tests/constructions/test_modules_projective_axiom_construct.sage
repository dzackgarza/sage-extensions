r"""The projective module refinement consists of direct summands of free modules."""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_integer_plane_lies_in_the_projective_refinement() -> None:
    module = ZZ.free_module(2)
    category = Modules(ZZ).Projective()

    assert module in category
    assert module.is_projective()
    assert module.Mor(module).identity()(module.module_generator(0)) == module.module_generator(0)
