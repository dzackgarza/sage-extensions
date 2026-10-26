r"""An open absolute-Galois subgroup retains the finite extension it fixes."""

from sage_extensions.all import *  # noqa: F401,F403


def test_gaussian_open_subgroup_fixed_extension_has_degree_two_and_expected_field() -> None:
    ambient = AbsoluteGaloisGroup(QQ)
    gaussian = QuadraticField(-1, "i")
    subgroup = ambient.open_subgroup(gaussian)
    extension = subgroup.fixed_extension()

    assert extension.field() is gaussian
    assert extension.degree() == 2
    assert extension.embedding() == subgroup.embedding()
