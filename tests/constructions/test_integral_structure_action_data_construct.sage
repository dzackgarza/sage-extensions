r"""An integral-structure action retains exactly its rational group and selected lattice inclusion."""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_hyperbolic_integral_structure_retains_defining_data() -> None:
    plane = Lattices(QQ)("U")
    restriction = Modules(QQ).restriction_of_scalars(
        ZZ.Mor(QQ)(lambda n: QQ(n))
    )
    space = restriction(plane)
    e0, e1 = plane.module_generators()
    inclusion = space.submodule([space(e0), space(e1)])
    action = IntegralStructureAction(plane.O(), inclusion)

    assert action.rational_group() is plane.O()
    assert action.lattice_inclusion() is inclusion
