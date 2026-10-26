r"""Even bilinear forms have even self-pairing on every vector."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_lies_in_the_even_bilinear_refinement() -> None:
    form = NamedLattices.U
    category = BilinearFormModules(ZZ).Even()

    assert form in category
    assert form.is_even()
    assert form.b(form.module_generator(0), form.module_generator(0)) == 0
