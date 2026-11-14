r"""Pointwise null stabilizers lift split quotient isometries in every rank.

An integral orthogonal block map fixes the null basis. In the glued
U(3) quotient example below, quotient negation lifts setwise by global
negation but cannot fix the null line: b(f,x)=1 would become -1 modulo 3.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("null_rank", (1, 2), ids=("line", "plane"))
def test_split_pointwise_levi_lift_over_an_infinite_quotient(null_rank):
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic
    for _ in range(null_rank):
        ambient = ambient + hyperbolic
    ambient = ambient + Lattices(ZZ)([[2]])
    basis = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    null_basis = basis[:2*null_rank:2]
    u, v, w = basis[-3:]
    known = ambient.Aut()(dict(zip(labels, (*basis[:-3], u, v+w-u, w-2*u), strict=True)))
    reduction = ambient.primitive_isotropic_subobject(*null_basis).isotropic_reduction()
    quotient_map = reduction.levi_action()(known)
    lift = reduction.pointwise_levi_lift(quotient_map)
    assert reduction.levi_action()(lift) == quotient_map
    assert all(lift(point) == point for point in null_basis)
    assert all((~lift)(lift(point)) == point for point in basis)


def test_glued_line_pointwise_image_excludes_quotient_negation():
    ambient = Lattices(ZZ)([[0, 3, 0, 0], [3, 0, 1, 0], [0, 1, 0, 3], [0, 0, 3, 0]])
    e, f, x, y = tuple(ambient.module_generators())
    reduction = ambient.primitive_isotropic_subobject(e).isotropic_reduction()
    minus = reduction.O()({label: -reduction.module_generator(label) for label in reduction.module_generating_set()})
    setwise = reduction.parabolic_subgroup()(ambient.Aut()({label: -ambient.module_generator(label) for label in ambient.module_generating_set()}))
    assert reduction.levi_action()(setwise) == minus
    assert setwise(e) == -e
    assert reduction.pointwise_levi_lift(minus) is None
    assert minus not in reduction.pointwise_levi_image()


def test_zero_null_pointwise_levi_lift_and_joint_kernel():
    ambient = Lattices(ZZ)([[6]])
    reduction = ambient.primitive_isotropic_subobject().isotropic_reduction()
    minus = reduction.O()({label: -reduction.module_generator(label) for label in reduction.module_generating_set()})
    lift = reduction.pointwise_levi_lift(minus)
    assert all(lift(point) == -point for point in ambient.module_generators())
    assert reduction.unipotent_kernel().cardinality() == cardinal(1)
    zero = ambient.primitive_isotropic_subobject()
    assert zero.unipotent_radical().cardinality() == cardinal(1)
    assert tuple(zero.unipotent_group_generators()) == ()
