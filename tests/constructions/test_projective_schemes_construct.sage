r"""Projective space lies in the projective-scheme refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_is_projective_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    plane = ProjectiveSpaces(ring)(2)

    assert plane in ProjectiveSchemes(ring)
    assert plane in Schemes(ring).FiniteType()
    assert plane in Schemes(ring).Separated()
    assert plane.is_projective()
