r"""The structure sheaf supplies module descent data on a distinguished affine cover."""

from sage_extensions.all import *  # noqa: F401,F403


def test_structure_sheaf_descent_on_identity_affine_cover() -> None:
    line = AffineSpaces(QQ)(1)
    cover = DistinguishedAffineCovers(line).an_object()
    datum = line.structure_sheaf().module_descent_datum(cover)
    descent_category = DescentDataOnCover(cover.coverage(), cover)

    assert datum in descent_category
    assert descent_category.coverage() is cover.coverage()
    assert descent_category.covering_family() is cover
