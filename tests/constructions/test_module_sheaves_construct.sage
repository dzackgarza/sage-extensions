r"""The structure sheaf is canonically a sheaf of modules over itself."""

from sage_extensions.all import *  # noqa: F401,F403


def test_structure_sheaf_is_a_module_sheaf() -> None:
    line = AffineSpaces(QQ)(1)
    structure = line.structure_sheaf()

    assert structure in ModuleSheaves(line)
    assert ModuleSheaves(line).an_object() is structure
