r"""The structure sheaf is a represented sheaf object on its ringed space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_structure_sheaf_is_a_sheaf_object() -> None:
    line = AffineSpaces(QQ)(1)
    structure = line.structure_sheaf()

    assert structure in SheafObjects(line)
    assert SheafObjects(line).an_object() is structure
