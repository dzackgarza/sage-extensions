r"""Every affine scheme is a sheafed space with its selected structure sheaf."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_is_a_sheafed_space() -> None:
    line = AffineSpaces(QQ)(1, names=("x",))

    assert line in SheafedSpaces()
    assert line.structure_sheaf().global_sections() is line.coordinate_ring()
