r"""A single distinguished open D(1) is the canonical affine cover specimen."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_distinguished_affine_cover() -> None:
    line = AffineSpaces(QQ)(1)
    covers = DistinguishedAffineCovers(line)
    cover = covers.an_object()

    assert cover in covers
    assert cover.ambient_scheme() is line
    assert cover.defining_elements().cardinality() == cardinal(1)
    assert cover.open(0) == line.distinguished_open(line.coordinate_algebra().one())
