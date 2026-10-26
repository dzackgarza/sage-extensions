r"""An algebraic geometer's session: affine and projective space, curves, products, points.

One long session per base ring, typed as into a notebook.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


BASES = {
    "QQ": lambda: QQ,
    "GF(5)": lambda: GF(5),
    "GF(4)": lambda: GF(4),
    "ZZ": lambda: ZZ,
}
EXTENSIONS = {
    "QQ": lambda: QuadraticField(2, "s"),
    "GF(5)": lambda: GF(25),
    "GF(4)": lambda: GF(16),
    "ZZ": lambda: GF(7),
}


@pytest.mark.parametrize("name", sorted(BASES))
def test_an_algebraic_geometry_session(name) -> None:
    base = BASES[name]()
    rendered(base)
    is_field = base in Fields()

    # The base scheme, affine plane and projective line.
    point = (base).affine_spectrum()
    rendered(point)
    assert point in AffineSchemes(base)
    assert point.relative_dimension() == 0
    plane = AffineSpaces(base)(2, names=("x", "y"))
    line = ProjectiveSpaces(base)(1)
    rendered(plane)
    rendered(line)
    assert plane in AffineSchemes(base)
    assert plane in SmoothSchemes(base)
    assert plane in IntegralSchemes(base)
    assert plane in NormalSchemes(base)
    assert plane.relative_dimension() == cardinal(2)
    assert line in ProjectiveSchemes(base)
    assert line in SmoothSchemes(base)
    assert line.relative_dimension() == 1
    assert plane.structure_morphism().codomain() == point
    if is_field:
        assert plane in Varieties(base)
        assert plane in Surfaces(base)
        assert line in Curves(base)
        assert plane.dimension() == 2

    # A smooth cubic and a nodal cubic in the plane.
    ring = plane.coordinate_ring()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    smooth = plane.closed_subscheme(y**2 - x**3 - x)
    node = plane.closed_subscheme(y**2 - x**3 - x**2)
    two_points = plane.closed_subscheme(x * (x - ring.one()), y)
    for curve in (smooth, node, two_points):
        rendered(curve)
        assert curve in ClosedSubschemes(base)
        assert curve in Schemes(base)
        assert curve.ambient_scheme() is plane
        assert curve.inclusion().codomain() is plane
    assert smooth.codimension() == 1
    assert smooth.relative_dimension() == 1
    assert node.relative_dimension() == 1
    assert two_points.relative_dimension() == 0
    assert smooth in IntegralSchemes(base)
    assert node in IntegralSchemes(base)
    assert two_points not in IntegralSchemes(base)
    if is_field and base.characteristic() != 2:
        assert smooth in SmoothSchemes(base)
        assert smooth in Curves(base)
        assert node not in SmoothSchemes(base)
        assert node not in NormalSchemes(base)
        assert node in Curves(base)
    assert smooth.coordinate_ring().krull_dimension() == base.krull_dimension() + 1

    # Points over finite fields.
    if is_field and base.cardinality().is_finite():
        q = int(base.cardinality().finite_value())
        assert plane.point_count() == q**2
        assert line.point_count() == q + 1
        assert line.point_count(2) == q**2 + 1
        assert two_points.point_count() == 2
        assert smooth.point_count() >= 1
        assert smooth.point_count() <= 2 * q + 1
        rendered(line.zeta_function())
        assert ProjectiveSpaces(base)(2).point_count() == q**2 + q + 1

    # Products and fiber products.
    quadric = Schemes(base).product((line, line))
    rendered(quadric)
    assert quadric in ProductSchemes(base)
    assert quadric in ProjectiveSchemes(base)
    assert quadric in SmoothSchemes(base)
    assert quadric.relative_dimension() == 2
    assert quadric.projection(0).codomain() is line
    assert quadric.projection(1).codomain() is line
    if is_field:
        assert quadric in Surfaces(base)
        if base.cardinality().is_finite():
            q = int(base.cardinality().finite_value())
            assert quadric.point_count() == (q + 1) ** 2
    mixed = plane.product(line)
    rendered(mixed)
    assert mixed.relative_dimension() == 3
    square = Schemes(base).fiber_product(smooth.structure_morphism(), smooth.structure_morphism())
    rendered(square)
    assert square.relative_dimension() == 2
    assert square.fiber_product_base() == point

    # The prime spectrum of the coordinate ring, and stalks.
    spectrum = plane.underlying_space()
    rendered(spectrum)
    origin = spectrum(ring.ideal(x, y))
    generic = spectrum.generic_point()
    assert generic.specializes_to(origin)
    stalk = plane.stalk(origin)
    rendered(stalk)
    assert stalk in LocalRings()
    assert stalk.krull_dimension() == base.krull_dimension() + 2
    assert stalk.residue_field() in Fields()
    assert plane.structure_sheaf().global_sections() is ring
    assert origin in spectrum.closed_set(ring.ideal(x))
    assert generic not in spectrum.closed_set(ring.ideal(x))

    # Spec is a contravariant functor: a ring map gives a scheme map the other way.
    spec = Algebras(base).Associative().Unital().Commutative().spectrum()
    affine_line = base.polynomial_ring("t")
    t = affine_line.algebra_generator("t")
    parametrization = ring.Mor(affine_line)({"x": t**2, "y": t**3})
    cusp_map = spec(parametrization)
    rendered(cusp_map)
    assert cusp_map.domain() is (affine_line).affine_spectrum()
    assert cusp_map.codomain() is (ring).affine_spectrum()
    assert spec(affine_line).relative_dimension() == 1
    assert spec(ring) == plane
    assert spec(ring.Mor(ring).identity()) == (ring).affine_spectrum().Mor((ring).affine_spectrum()).identity()

    # Base change of the plane to an extension field, or to a residue field of ZZ.
    extension = EXTENSIONS[name]()
    rendered(extension)
    changed = plane.base_change(base.Mor(extension)(lambda element: extension(element)))
    rendered(changed)
    assert changed in AffineSchemes(extension)
    assert changed.relative_dimension() == cardinal(2)
    assert changed.coordinate_ring().krull_dimension() == 2
