r"""Projectivization of a quasi-coherent sheaf commutes with scalar extension."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_sheaf_projectivization_after_quadratic_base_change() -> None:
    field = QuadraticField(2, "s")
    point = QQ.affine_spectrum()
    sheaf = point.associated_module_sheaf(QQ.free_module(("u", "v")))
    comparison = sheaf.projectivization_base_change(
        QQ.Mor(field)(lambda element: field(element))
    )

    assert comparison.changed_projectivization().domain().is_isomorphic(
        ProjectiveSpaces(field)(1)
    )
