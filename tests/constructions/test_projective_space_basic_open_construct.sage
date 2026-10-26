r"""The basic open D_+(x_i) is the i-th standard affine chart of projective space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_line_coordinate_basic_open_is_standard_chart() -> None:
    line = ProjectiveSpaces(QQ)(1, names=("x", "y"))
    x = line.homogeneous_coordinate_generators()[0]

    assert line.basic_open(x).is_isomorphic(line.standard_affine_chart(0))
