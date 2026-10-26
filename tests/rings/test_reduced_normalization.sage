r"""Reduced normalization, total quotients, finite local lengths and conductors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_reducible_node_normalizes_componentwise_and_retains_the_map() -> None:
    polynomial = QQ.polynomial_ring(("x", "y"))
    x, y = tuple(polynomial.algebra_generators())
    node = polynomial.quotient_ring(polynomial.ideal(x * y))

    assert node.is_reduced()
    assert node.minimal_primes().cardinality() == 2
    assert node.irreducible_components().cardinality() == 2
    component_locus = node.irreducible_component_locus()
    assert component_locus.cardinality() == 2
    assert all(closed.universe() is node.prime_ideal_locus() for closed in component_locus)
    for quotient in node.irreducible_components():
        # Components are quotients of the actual node, not merely abstractly
        # isomorphic quotients of its polynomial presentation. The chosen
        # enumeration of components need not order the minimal primes alike.
        assert quotient.quotient_source() is node
        assert quotient.quotient_map().domain() is node
        assert quotient.defining_ideal().ring() is node
        assert any(quotient.defining_ideal() == prime for prime in node.minimal_primes())
    components = node.normalization_components()
    assert components.cardinality() == 2
    for minimal_prime, component, component_map in components:
        assert minimal_prime.ring() is node
        assert component_map.domain() is node
        assert component_map.codomain() is component
    normalization = node.normalization()
    normalization_map = node.normalization_map()
    assert normalization_map.domain() is node
    assert normalization_map.codomain() is normalization
    assert node.conductor_ideal().ring() is node
    assert node.delta_invariant() == 1


def test_total_quotient_ring_of_reduced_node_is_product_of_component_fields() -> None:
    polynomial = QQ.polynomial_ring(("x", "y"))
    x, y = tuple(polynomial.algebra_generators())
    node = polynomial.quotient_ring(polynomial.ideal(x * y))

    total = node.total_quotient_ring()
    total_map = node.total_quotient_map()
    assert total_map.domain() is node
    assert total_map.codomain() is total
    for component in node.irreducible_components():
        # The total-quotient map is assembled from actual maps A -> A/p,
        # not from arbitrary lifts to its polynomial presentation.
        projection = component.quotient_map()
        assert projection.domain() is node
        assert projection(node(x * y)) == component.zero()
        assert projection(node.one()) == component.one()
    assert total_map(node(x + y)).is_unit()
    assert not total_map(node(x)).is_unit()


def test_local_length_divides_out_nonrational_residue_degree() -> None:
    polynomial = QQ.polynomial_ring("x")
    x = polynomial.algebra_generator("x")
    prime = polynomial.ideal(x**2 + 1)
    point = polynomial.spectrum()(prime)

    assert point.residue_degree() == 2
    assert point.local_length(prime) == 1
    assert point.local_length(prime.power(2)) == 2


def test_the_conductor_of_the_cusp_is_its_maximal_ideal_at_the_origin() -> None:
    r"""``QQ[x, y]/(y^2 - x^3) = QQ[t^2, t^3]`` with normalization ``QQ[t]``; the
    conductor ``{f : f QQ[t] in QQ[t^2, t^3]}`` is ``(t^2, t^3) = (x, y)``, and
    ``delta = dim QQ[t]/QQ[t^2, t^3] = 1`` (Hartshorne, IV Ex. 1.8; Serre,
    *Algebraic Groups and Class Fields*, IV §1)."""
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_by_relations([y**2 - x**3])
    xbar = cusp.algebra_generator("x")
    ybar = cusp.algebra_generator("y")
    conductor = cusp.conductor_ideal()

    assert conductor == cusp.ideal(xbar, ybar)
    assert not conductor.contains_ambient_element(cusp.one())
    assert cusp.delta_invariant() == 1
    assert cusp.normalization().krull_dimension() == 1
