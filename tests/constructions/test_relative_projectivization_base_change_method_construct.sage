r"""Relative projectivization carries its scalar-change comparison itself."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_line_relative_projectivization_base_changes_to_projective_line() -> None:
    field = QuadraticField(2, "s")
    point = QQ.affine_spectrum()
    source = point.associated_module_sheaf(QQ.free_module(("u", "v")))
    total = source.projectivization().domain()
    comparison = total.projectivization_base_change(
        QQ.Mor(field)(lambda element: field(element))
    )

    assert comparison.changed_projectivization().domain().is_isomorphic(
        ProjectiveSpaces(field)(1)
    )
