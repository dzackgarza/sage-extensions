r"""The structure sheaf is canonically a sheaf of O_X-algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_structure_sheaf_is_an_algebra_sheaf() -> None:
    line = AffineSpaces(QQ)(1)
    structure = line.structure_sheaf()

    assert structure in AlgebraSheaves(line)
    assert AlgebraSheaves(line).an_object() is structure
