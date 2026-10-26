r"""Exact finite-form groups and labelled vector-family transport.

Counting ordered hyperbolic bases gives
|O^+(2m,2)| = (2^m-1)(2^(m-1)+1) 2^(2m-2) |O^+(2m-2,2)|.
The discriminant quadratic form of U(2)^m realizes this split form.
"""

import pytest
import sage.all

from sage_extensions.catalogue import NamedLattices
from sage_extensions.categories.sets.set_categories import Sets


@pytest.mark.parametrize("planes, expected", [(1, 2), (2, 72), (5, 46998591897600)])
def test_split_elementary_two_discriminant_orthogonal_group(planes, expected):
    form = (NamedLattices.U.twist(2) ** planes).discriminant_group()
    group = form.orthogonal_group()
    assert group.cardinality() == expected
    basis = tuple(form.module_generators())
    for generator in group.group_generators():
        for i, left in enumerate(basis):
            assert form.q(generator(left)) == form.q(left)
            for right in basis[i + 1:]:
                assert form.q(generator(left + right)) == form.q(left + right)


def test_hyperbolic_discriminant_form_of_exponent_four():
    form = NamedLattices.U.twist(4).discriminant_group()
    group = form.orthogonal_group()
    assert group.cardinality() == 4
    for generator in group.group_generators():
        assert all(form.q(generator(point)) == form.q(point) for point in form.elements())


def test_bilinear_hyperbolic_plane_has_full_linear_group():
    form = NamedLattices.U.twist(2).discriminant_bilinear_form()
    assert form.orthogonal_group().cardinality() == 6


def test_reindexed_a2_simple_roots_have_an_integral_transporter():
    lattice = NamedLattices.A2
    indices = Sets.Δ[1]
    family = Sets().Mor(indices, lattice)(lambda i: lattice.module_generator(int(i)))
    reindexed = Sets().Mor(indices, lattice)(lambda i: lattice.module_generator(1 - int(i)))
    witness = lattice.O().transporter(family, reindexed)
    assert witness is not None
    assert {witness(family(i)) for i in indices} == {reindexed(i) for i in indices}


@pytest.mark.parametrize("multiple", [1, 2])
def test_a2_bases_with_different_pairings_have_no_orthogonal_transporter(multiple):
    r"""b(a,b)=-1 differs from b(a,m*a+b)=2m-1 for m=1,2."""
    lattice = NamedLattices.A2
    first, second = tuple(lattice.module_generators())
    source = Sets().Mor(Sets.Δ[1], lattice)(lambda i: (first, second)[int(i)])
    target = Sets().Mor(Sets.Δ[1], lattice)(
        lambda i: (first, multiple * first + second)[int(i)]
    )
    assert lattice.O().transporter(source, target) is None


def test_hyperbolic_plane_is_even_unimodular_and_two_elementary():
    lattice = NamedLattices.U
    assert lattice.is_even()
    assert lattice.is_unimodular()
    assert lattice.two_elementary_invariants() == (2, 0, 0)
