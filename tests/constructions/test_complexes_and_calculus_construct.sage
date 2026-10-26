r"""Cochain complexes, connections and Cartan calculus a mathematician expects.

The Koszul complex of $(x, y)$ over every field, cycles, boundaries and
cohomology as functors, connections on a free module and their curvature,
vector fields, interior products, Lie derivatives and the Cartan formula,
derivations, and de Rham cohomology of the punctured line.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _koszul_complex(ring):
    r"""$0 \to A \xrightarrow{(x,y)} A^2 \xrightarrow{(-y, x)} A \to 0$ for $A = R[x, y]$."""
    plane = ring.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    first = plane.free_module(1)
    middle = plane.free_module(2)
    last = plane.free_module(1)
    d0 = first.Mor(middle)({0: x * middle.module_generator(0) + y * middle.module_generator(1)})
    d1 = middle.Mor(last)({0: -y * last.module_generator(0), 1: x * last.module_generator(0)})
    return plane, CochainComplexes(plane)({0: first, 1: middle, 2: last}, {0: d0, 1: d1})


def test_the_koszul_complex_of_a_regular_sequence(field) -> None:
    plane, koszul = _koszul_complex(field)
    assert koszul in CochainComplexes(plane)
    assert koszul in GradedModules(plane)
    assert koszul.differential().degree_shift() == 1
    assert koszul.cohomology(0).cardinality() == cardinal(1)
    assert koszul.cohomology(1).cardinality() == cardinal(1)
    assert koszul.cohomology(2).cardinality() == field.cardinality()
    assert koszul.cycles(1).module_rank() == cardinal(1)
    assert koszul.boundaries(1).module_rank() == cardinal(1)
    assert koszul.cycles(1) == koszul.boundaries(1)
    assert CochainComplexes(plane).cohomology(2)(koszul) == koszul.cohomology(2)
    assert CochainComplexes(plane).underlying_graded_module()(koszul) in GradedModules(plane)


def test_the_koszul_complex_over_the_integers() -> None:
    plane, koszul = _koszul_complex(ZZ)
    assert koszul.cohomology(1).cardinality() == cardinal(1)
    assert koszul.cohomology(2).module_rank() == cardinal(1)
    assert koszul.cohomology(2).annihilator() == plane.ideal(plane.algebra_generator("x"), plane.algebra_generator("y"))


def test_cochain_morphisms_and_the_identity() -> None:
    _, koszul = _koszul_complex(QQ)
    homset = koszul.Mor(koszul)
    identity = homset.identity()
    assert identity * identity == identity
    assert identity.domain() is koszul
    assert koszul.Mor(koszul).identity() == identity


def test_a_complex_with_nonzero_d_squared_is_refused() -> None:
    line = ZZ.free_module(1)
    doubling = line.Mor(line)({0: 2 * line.module_generator(0)})
    with pytest.raises((ValueError, AssertionError)):
        CochainComplexes(ZZ)({0: line, 1: line, 2: line}, {0: doubling, 1: doubling})


def test_a_cochain_complex_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    line = ring.free_module(1)
    doubling = line.Mor(line)({0: 2 * line.module_generator(0)})
    complex_ = CochainComplexes(ring)({0: line, 1: line}, {0: doubling})
    assert complex_ in CochainComplexes(ring)
    assert complex_.cohomology(1).cardinality() == ring.quotient_ring(ring.ideal(ring(2))).cardinality()
    assert complex_.cohomology(0).module_rank() == cardinal(1 if ring(2) == ring.zero() else 0)


# ---------------------------------------------------------------------------
# Connections.
# ---------------------------------------------------------------------------


def test_connections_on_a_free_module_over_the_affine_line(field) -> None:
    line = field.polynomial_ring("x")
    module = line.free_module(1)
    connections = module.connections()
    omega = line.kahler_differentials()
    target = connections.target_module()
    dx = omega.differential_generator("x")
    e = module.module_generator(0)

    trivial = connections(lambda label: target.zero())
    twisted = connections(lambda label: target.pure_tensor(e, dx))
    assert trivial.is_flat()
    assert twisted.is_flat()
    assert trivial.module() is module
    assert trivial.algebra() is line
    with_connection = ModulesWithConnection(line)(twisted)
    assert with_connection in ModulesWithConnection(line)
    assert with_connection in ModulesWithFlatConnection(line)
    assert with_connection.connection() is twisted
    assert with_connection.is_flat_connection()


def test_curvature_of_a_connection_on_the_plane(field) -> None:
    r"""$\nabla = d + x\,dy$ on the trivial line bundle has curvature $dx \wedge dy \ne 0$."""
    plane = field.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    module = plane.free_module(1)
    connections = module.connections()
    omega = plane.kahler_differentials()
    target = connections.target_module()
    dy = omega.differential_generator("y")
    e = module.module_generator(0)

    curved = connections(lambda label: target.pure_tensor(e, omega.scalar_multiple(x, dy)))
    flat = connections(lambda label: target.pure_tensor(e, dy))
    assert not curved.is_flat()
    assert flat.is_flat()
    assert curved.curvature_on_generator(0) != curved.curvature_target().zero()
    assert flat.curvature_on_generator(0) == flat.curvature_target().zero()
    curved_module = ModulesWithConnection(plane)(curved)
    assert curved_module in ModulesWithConnection(plane)
    assert curved_module not in ModulesWithFlatConnection(plane)


# ---------------------------------------------------------------------------
# Cartan calculus.
# ---------------------------------------------------------------------------


def _plane_calculus(field):
    plane = field.polynomial_ring(("x", "y"))
    values = plane.regular_module()
    fields_ = plane.vector_fields()
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")

    def field_of(a, b):
        return fields_({"x": values.scalar_multiple(a, values.module_generator(0)), "y": values.scalar_multiple(b, values.module_generator(0))})

    return plane, x, y, field_of


def test_vector_fields_and_lie_brackets(field) -> None:
    plane, x, y, field_of = _plane_calculus(field)
    d_dx = field_of(plane.one(), plane.zero())
    d_dy = field_of(plane.zero(), plane.one())
    x_d_dy = field_of(plane.zero(), x)
    y_d_dx = field_of(y, plane.zero())

    assert d_dx(x) == plane.one()
    assert d_dx(y) == plane.zero()
    assert d_dx(x * y) == y
    assert d_dx.lie_bracket(d_dy)(x * y) == plane.zero()
    assert d_dx.lie_bracket(x_d_dy)(y) == plane.one()
    assert d_dx.lie_bracket(x_d_dy)(x) == plane.zero()
    euler = y_d_dx.lie_bracket(x_d_dy)
    assert euler(x) == -x
    assert euler(y) == y
    assert plane.derivations(plane.regular_module()).module_rank() == cardinal(2)
    assert d_dx in plane.derivations(plane.regular_module())


def test_interior_products_lie_derivatives_and_the_cartan_formula(field) -> None:
    plane, x, y, field_of = _plane_calculus(field)
    de_rham = plane.de_rham_algebra()
    d = de_rham.differential()
    dx = de_rham(plane.kahler_differentials().differential_generator("x"))
    dy = de_rham(plane.kahler_differentials().differential_generator("y"))
    d_dx = field_of(plane.one(), plane.zero())
    x_d_dy = field_of(plane.zero(), x)

    assert d_dx.interior_product()(dx) == de_rham.one()
    assert d_dx.interior_product()(dy) == de_rham.zero()
    assert d_dx.interior_product()(dx * dy) == dy
    assert x_d_dy.interior_product()(dy) == de_rham(x)
    assert d_dx.lie_derivative()(de_rham(x)) == de_rham.one()
    assert d_dx.lie_derivative()(dx) == de_rham.zero()
    assert x_d_dy.lie_derivative()(dy) == dx
    form = de_rham(y) * dx
    assert d_dx.lie_derivative()(form) == d(d_dx.interior_product()(form)) + d_dx.interior_product()(d(form))
    assert x_d_dy.lie_derivative()(form) == d(x_d_dy.interior_product()(form)) + x_d_dy.interior_product()(d(form))
    assert d(d(form)) == de_rham.zero()
    assert dx * dy == -(dy * dx)


def test_de_rham_cohomology_of_the_punctured_line(field) -> None:
    r"""$H^1_{dR}(\mathbb G_m) $ is spanned by $dx/x$ in characteristic zero."""
    laurent = field.laurent_polynomial_ring("x")
    de_rham = laurent.de_rham_algebra()
    cohomology = de_rham.cohomology_algebra()
    assert cohomology in CohomologyAlgebras(field)
    assert de_rham.cohomology(0).module_rank() == cardinal(1)
    if field.characteristic() == 0:
        assert de_rham.cohomology(1).module_rank() == cardinal(1)
        assert de_rham.cohomology(2).cardinality() == cardinal(1)
    else:
        assert de_rham.cohomology(1).module_rank() >= cardinal(1)


def test_the_regular_dg_module_of_a_dga(field) -> None:
    de_rham = field.polynomial_ring("x").de_rham_algebra()
    regular = de_rham.regular_dg_module()
    assert regular in DifferentialGradedModules(de_rham)
    assert regular.dga() is de_rham
    assert regular.is_differential_graded_module()
