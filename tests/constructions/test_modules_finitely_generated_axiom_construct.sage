r"""The finitely-generated module refinement is a membership assertion.

The standard integer plane has two generators and therefore lies in the
finitely-generated refinement of ``ZZ``-modules.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_plane_lies_in_the_finitely_generated_refinement() -> None:
    module = ZZ.free_module(2)
    category = Modules(ZZ).FinitelyGenerated()

    assert module in category
    assert module.module_generators().cardinality() == cardinal(2)
    assert module.Mor(module).identity()(module.module_generator(0)) == module.module_generator(0)
