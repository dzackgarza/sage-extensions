r"""Local dimension and embedding dimension determine regularity."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_origin_has_dimension_and_embedding_dimension_two() -> None:
    ring = QQ.polynomial_ring(("x", "y"))
    x, y = (ring.algebra_generator(name) for name in ("x", "y"))
    origin = ring.spectrum()(ring.ideal(x, y))

    assert origin.height() == 2
    assert origin.embedding_dimension() == 2
    assert origin.is_regular()
    assert origin.is_locally_factorial()


def test_cusp_origin_has_local_dimension_one_and_embedding_dimension_two() -> None:
    r"""At the origin of ``y^2 = x^3`` the local ring has dimension 1 and
    ``m/m^2`` is spanned by ``x, y`` (the relation lies in ``m^2``), so it is not
    regular.  It is not a UFD either: ``t = y/x`` satisfies ``t^2 = x`` and is not
    in the ring, so the ring is not normal, and a UFD is normal
    (Atiyah--Macdonald, Ch. 11; Matsumura, *Commutative Ring Theory*, Thm. 20.4)."""
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_by_relations([y**2 - x**3])
    origin = cusp.spectrum()(cusp.ideal(cusp.algebra_generator("x"), cusp.algebra_generator("y")))

    assert origin.height() == 1
    assert origin.embedding_dimension() == 2
    assert not origin.is_regular()
    assert not origin.is_locally_factorial()
