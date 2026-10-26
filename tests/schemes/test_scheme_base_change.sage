r"""Base change of schemes along a ring map, and the slice adjunction along a base morphism."""

from sage_extensions.all import *


def _extension():
    field = QuadraticField(2, "s")
    return field, QQ.Mor(field)(lambda element: field(element))


def test_base_change_of_the_cuspidal_cubic_is_the_cubic_over_the_extension() -> None:
    field, ring_map = _extension()
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    algebra = plane.coordinate_ring()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    cusp = plane.closed_subscheme(y**2 - x**3)
    change = Schemes(ring_map.domain()).base_change_functor(ring_map)

    ordinary_changed_plane = AffineSpaces(field)(2, names=("x", "y"))
    changed_plane = change(plane)
    changed_cusp = change(cusp)
    # The session spelling names the object, not the functor.
    assert plane.base_change(ring_map) is changed_plane
    assert cusp.base_change(ring_map) is changed_cusp
    assert changed_plane is not ordinary_changed_plane
    assert ordinary_changed_plane not in FiberProductSchemes(field)
    assert changed_plane in AffineSpaces(field)
    assert changed_cusp in AffineSchemes(field)
    assert changed_cusp in FiberProductSchemes(field)
    assert changed_cusp.relative_dimension() == 1
    assert changed_cusp.fiber_product_base() is (QQ).affine_spectrum()
    assert changed_cusp.left_projection().codomain() is cusp
    assert changed_cusp.right_projection().codomain() is (field).affine_spectrum()
    changed_algebra = changed_cusp.coordinate_algebra()
    x_changed = changed_algebra.algebra_generator("x")
    y_changed = changed_algebra.algebra_generator("y")
    assert changed_algebra.base_ring() is field
    assert y_changed**2 == x_changed**3
    projection = changed_cusp.left_projection().coordinate_algebra_morphism()
    assert projection(cusp.coordinate_algebra().algebra_generator("y")) == y_changed

    # The base-change square commutes: X' -> X -> Spec Q equals X' -> Spec K -> Spec Q.
    left_square = cusp.structure_morphism() * changed_cusp.left_projection()
    right_square = change.base_morphism() * changed_cusp.right_projection()
    assert left_square == right_square

    # A morphism over Q base-changes to a morphism over K with commuting squares.
    inclusion = cusp.inclusion()
    changed_inclusion = change(inclusion)
    assert changed_inclusion.domain() is changed_cusp
    assert changed_inclusion.codomain() is changed_plane
    assert changed_plane.left_projection() * changed_inclusion == inclusion * changed_cusp.left_projection()
    assert changed_inclusion.is_closed_immersion()


def test_base_change_carries_the_swap_to_an_involution_fixing_the_diagonal() -> None:
    r"""The swap `(x, y) \mapsto (y, x)` of `\mathbb{A}^2_{\mathbb{Q}}` base-changes to an
    involution of `\mathbb{A}^2_{\mathbb{Q}(\sqrt 2)}` over the base, still fixing exactly
    the diagonal line; base change along the identity of `\mathbb{Q}` or of
    `\mathbb{Q}(\sqrt 2)` changes nothing up to isomorphism."""
    field, ring_map = _extension()
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    algebra = plane.coordinate_ring()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    swap = plane.Mor(plane)(algebra.Mor(algebra)({"x": y, "y": x}))

    changed_plane = plane.base_change(ring_map)
    changed_swap = swap.base_change(ring_map)
    identity = changed_plane.Mor(changed_plane).identity()

    assert changed_swap * changed_swap == identity
    assert changed_swap != identity
    assert changed_plane.structure_morphism() * changed_swap == changed_plane.structure_morphism()
    assert changed_swap.fixed_locus().relative_dimension() == 1
    assert plane.base_change(QQ.Mor(QQ).identity()).is_isomorphic(plane)
    assert changed_plane.base_change(field.Mor(field).identity()).is_isomorphic(changed_plane)


def test_the_special_fibre_of_xy_equals_t_is_the_node_xy_equals_zero() -> None:
    r"""Pulling the family `xy = t` over the `t`-line back along `t = 0` gives the
    reducible fibre `xy = 0`, two lines meeting in a node, while the fibre over
    `t = 1` is the integral smooth hyperbola; the pullback is right adjoint to
    composition along `g`, and the counit after `\Sigma_g` of the unit is the identity."""
    parameter = QQ.polynomial_ring("t")
    t = parameter.algebra_generator("t")
    presentation = parameter.polynomial_ring(("x", "y"))
    x = presentation.algebra_generator("x")
    y = presentation.algebra_generator("y")
    family = presentation.quotient_by_relations((x * y - t,)).affine_spectrum()
    line = parameter.affine_spectrum()

    def point(value):
        return QQ.affine_spectrum().Mor(line)(parameter.Mor(QQ)({"t": QQ(value)}))

    special = Schemes(parameter).fiber_product(family.structure_morphism(), point(0))
    general = Schemes(parameter).fiber_product(family.structure_morphism(), point(1))
    fibre_ring = special.coordinate_ring()

    assert fibre_ring.algebra_generator(("left", "x")) * fibre_ring.algebra_generator(("left", "y")) == 0
    assert special.irreducible_components().cardinality() == 2
    assert special.singular_locus().relative_dimension() == 0
    assert general.is_integral()
    assert general.is_smooth()

    adjunction = point(0).slice_base_change_adjunction()
    over_line = adjunction.right_adjoint().domain()
    family_object = over_line(family.structure_morphism())
    fibre_object = adjunction.right_adjoint()(family_object)
    composite = adjunction.counit(family_object) * adjunction.left_adjoint()(adjunction.unit(fibre_object))
    assert composite == over_line.Mor(composite.domain(), composite.codomain()).identity()


def test_base_change_of_the_rational_projective_line_is_the_projective_line_over_the_extension() -> None:
    field, ring_map = _extension()
    changed = ProjectiveSpaces(QQ)(1).base_change(ring_map)

    assert changed.is_isomorphic(ProjectiveSpaces(field)(1))
    assert changed.relative_dimension() == 1
    assert changed.genus() == 0


def test_base_change_of_a_cubic_surface_retains_its_projective_surface_owner() -> None:
    field, ring_map = _extension()
    space = ProjectiveSpaces(QQ)(3, names=("x0", "x1", "x2", "x3"))
    x0, x1, x2, x3 = space.homogeneous_coordinate_generators()
    cubic = space.closed_subscheme(x0**3 + x1**3 + x2**3 + x3**3)

    changed = cubic.base_change(ring_map)

    assert changed in ProjectiveCompleteIntersections(field)
    assert changed in Surfaces(field).Proper()
    assert changed in Surfaces(field).Projective()
    assert changed.is_del_pezzo()
    assert Surfaces(changed.scheme_base_ring()).DelPezzo()(changed).del_pezzo_degree() == 3
