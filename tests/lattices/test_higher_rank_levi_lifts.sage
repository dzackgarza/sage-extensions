r"""A split null-plane parabolic in 3U + <2> lifts O(U + <2>).

Fixing the first two hyperbolic planes and applying an integral isometry
of the last U + <2> is an integral ambient lift. The quotient transvection
(u,v,w) -> (u,v+w-u,w-2u) has infinite order and preserves the form.
"""

from sage_extensions.all import *


def test_null_plane_levi_section_lifts_a_quotient_transvection():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    e, f, a, b, u, v, w = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    isotropic = ambient.primitive_isotropic_subobject(e, a)
    reduction = isotropic.isotropic_reduction()
    levi = reduction.levi_action()
    known = ambient.Aut()(dict(zip(labels, (e, f, a, b, u, v+w-u, w-2*u), strict=True)))
    quotient_map = levi(known)
    assert quotient_map != levi.codomain().one()
    assert known(e) == e and known(a) == a
    lift = levi.lift(quotient_map)
    assert levi(lift) == quotient_map
    assert lift in isotropic.parabolic_subgroup()
    for source in (e, a):
        assert isotropic.inclusion().is_in_image(lift(source))
        assert isotropic.inclusion().is_in_image((~lift)(source))
    assert all((~lift)(lift(point)) == point for point in ambient.module_generators())
    assert all(ambient.b(lift(x), lift(y)) == ambient.b(x, y) for x in ambient.module_generators() for y in ambient.module_generators())


def _glued_plane_reduction():
    glued = Lattices(ZZ)([[0, 3, 0, 0], [3, 0, 1, 0], [0, 1, 0, 3], [0, 0, 3, 0]])
    ambient = glued + Lattices(ZZ)("U") + Lattices(ZZ)([[2]])
    e, f, x, y, u, v, w = tuple(ambient.module_generators())
    isotropic = ambient.primitive_isotropic_subobject(e, u)
    return ambient, isotropic, (e, f, x, y, u, v, w)


def test_glued_null_plane_levi_lift_can_move_the_null_basis():
    r"""Global negation lifts -1 on K, but no lift fixes I pointwise.

    If g fixes e,u, preservation of their pairings forces the f and v
    coefficients of g(f) to be 1 and 0. Since g(x)=-x modulo I,
    b(g(f),g(x))=-1 modulo 3, whereas b(f,x)=1.
    """
    ambient, isotropic, basis = _glued_plane_reduction()
    reduction = isotropic.isotropic_reduction()
    levi = reduction.levi_action()
    minus = reduction.O()({label: -reduction.module_generator(label) for label in reduction.module_generating_set()})
    lift = levi.lift(minus)
    assert levi(lift) == minus
    assert lift in isotropic.parabolic_subgroup()
    assert lift(basis[0]) != basis[0] or lift(basis[4]) != basis[4]
    assert all((~lift)(lift(point)) == point for point in basis)
    assert all(ambient.b(lift(x), lift(y)) == ambient.b(x, y) for x in basis for y in basis)


def test_glued_null_plane_quotient_exchange_has_no_levi_lift():
    r"""The exchange x <-> y on K fails the retained gluing condition.

    Divisibilities force g(e)=a*e+3*b*u and g(u)=c*e+d*u, with a,d
    units modulo 3. Pairing with g(u) forces the v coefficient of g(f)
    to vanish modulo 3. Then g(x)=y modulo I gives b(g(f),g(x))=0
    modulo 3, contrary to b(f,x)=1.
    """
    ambient, isotropic, basis = _glued_plane_reduction()
    reduction = isotropic.isotropic_reduction()
    perpendicular = reduction.orthogonal_complement().inclusion()
    projection = reduction.projection()
    x, y, w = (projection(perpendicular.lift(basis[position])) for position in (2, 3, 6))
    labels = tuple(reduction.module_generating_set())
    general_linear = reduction.general_linear_group()
    chart = general_linear(dict(zip(labels, (x, y, w), strict=True)))
    swapped = general_linear(dict(zip(labels, (y, x, w), strict=True)))
    permutation = swapped * ~chart
    exchange = reduction.O()({label: permutation(reduction.module_generator(label)) for label in labels})
    image_locus = reduction.levi_action().selected_section().domain()
    assert exchange not in image_locus


def test_zero_null_levi_section_lifts_negation_of_the_whole_lattice():
    ambient = Lattices(ZZ)([[6]])
    isotropic = ambient.primitive_isotropic_subobject()
    reduction = isotropic.isotropic_reduction()
    levi = reduction.levi_action()
    minus = reduction.O()({label: -reduction.module_generator(label) for label in reduction.module_generating_set()})
    lift = levi.lift(minus)
    assert levi(lift) == minus
    assert all(lift(point) == -point for point in ambient.module_generators())


def test_null_plane_public_levi_lift_uses_the_exact_image_section():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    e, f, a, b, u, v, w = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    reduction = ambient.primitive_isotropic_subobject(e, a).isotropic_reduction()
    known = ambient.Aut()(dict(zip(labels, (e, f, a, b, u, v+w-u, w-2*u), strict=True)))
    quotient_map = reduction.levi_action()(known)
    lift = reduction.levi_lift(quotient_map)
    assert reduction.levi_action()(lift) == quotient_map
    assert all((~lift)(lift(point)) == point for point in ambient.module_generators())


def test_null_plane_levi_image_generators_realize_both_signs_on_a_line():
    r"""In 2U + <2>, negating the last summand lifts the nontrivial O(<2>) element."""
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    basis = tuple(ambient.module_generators())
    reduction = ambient.primitive_isotropic_subobject(basis[0], basis[2]).isotropic_reduction()
    image = reduction.levi_image()
    family = tuple(reduction.levi_image_generators())
    assert all(generator in image for generator in family)
    assert reduction.O().subgroup(family).cardinality() == cardinal(2)


def test_null_plane_levi_image_is_proper_in_a_split_binary_quotient():
    r"""The U(2) quotient has four isometries; only its two scalar maps lift.

    The coordinate pairing of f with x is odd. Divisibilities of e and u
    force the v coefficient of g(f) to be even. Exchanging x,y modulo I
    would make b(g(f),g(x)) even, so the exchange cannot lift.
    """
    glued = Lattices(ZZ)([[0, 2, 0, 0], [2, 0, 1, 0], [0, 1, 0, 2], [0, 0, 2, 0]])
    ambient = glued + Lattices(ZZ)("U")
    e, f, x, y, u, v = tuple(ambient.module_generators())
    reduction = ambient.primitive_isotropic_subobject(e, u).isotropic_reduction()
    perpendicular = reduction.orthogonal_complement().inclusion()
    projection = reduction.projection()
    first, second = (projection(perpendicular.lift(point)) for point in (x, y))
    labels = tuple(reduction.module_generating_set())
    general_linear = reduction.general_linear_group()
    chart = general_linear(dict(zip(labels, (first, second), strict=True)))
    swapped = general_linear(dict(zip(labels, (second, first), strict=True)))
    permutation = swapped * ~chart
    exchange = reduction.O()({label: permutation(reduction.module_generator(label)) for label in labels})
    minus = reduction.O()({label: -reduction.module_generator(label) for label in labels})
    image = reduction.levi_image()
    assert minus in image
    assert exchange not in image
