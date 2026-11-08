r"""The options and second route of the pinned edgewalk driver.

U+<2n> are in Nikulin's rank-three classification: U+<46> is non-reflective.
In U+<4> the vector x of norm 4 pairs evenly with L, so it is a root in the
"all" walk, but the norm-two walk K3 cannot have a norm-four wall.
"""

import pytest

from sage_extensions.all import *


def _hyperbolic_plus(square):
    summand = Lattices(ZZ)("A1").twist(-square // 2)
    return HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + summand)


def test_k3_mode_excludes_the_norm_four_wall():
    lattice = _hyperbolic_plus(4)
    x = tuple(lattice.module_generators())[2]
    assert lattice.q(x) == 4
    all_walls = tuple(lattice.allcock_edgewalk().simple_roots())
    k3_walls = tuple(lattice.allcock_edgewalk(option_norms="K3").simple_roots())
    assert x in all_walls or -x in all_walls
    assert x not in k3_walls and -x not in k3_walls
    assert all(lattice.q(root) == 2 for root in k3_walls)


def test_prescribed_vertex_returns_the_same_polyhedron_class():
    lattice = _hyperbolic_plus(2)
    report = lattice.allcock_edgewalk()
    vertex = next(iter(report.vertices()))
    ray = next(iter(vertex.primitive_rays()))
    restarted = lattice.allcock_edgewalk(initial_vertex=ray)
    assert restarted.is_reflective() is True
    assert restarted.vertices().cardinality() == report.vertices().cardinality()


def test_isomorphism_route_returns_a_witness_for_a_basis_change():
    lattice = _hyperbolic_plus(2)
    e, f, x = tuple(lattice.module_generators())
    changed = HyperbolicLattices(ZZ)(lattice.subobject_on((e + f + x, f, x + f)).inclusion().domain())
    witness = lattice.edgewalk_isometry(changed)
    assert witness is not None and witness.domain() is lattice and witness.codomain() is changed
    assert all(changed.b(witness(p), witness(q)) == lattice.b(p, q) for p in (e, f, x) for q in (e, f, x))


def test_non_reflective_reason_and_full_walk():
    lattice = _hyperbolic_plus(46)
    early = lattice.allcock_edgewalk()
    assert early.is_reflective() is False
    assert early.reason_non_reflective() == "Not reflective by the finiteness test"
    full = lattice.allcock_edgewalk(early_termination=False)
    assert full.is_reflective() is False
    assert full.reason_non_reflective() is None
    assert full.vertices().cardinality() >= early.vertices().cardinality()
