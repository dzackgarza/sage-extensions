r"""A single ambient primitive isotropic line orbit in odd rank.

For the two forms below, divide the pairing by two. The resulting
unimodular lattice is odd, with odd rank and both signature indices at
least two. By Peters--Sterk, Theorem 2.3.1, it is I_{p,q}. A characteristic
vector has odd coordinates in a diagonal unimodular basis and thus odd
square; no isotropic vector is characteristic. For every primitive
isotropic v choose w with (v,w)=1. If w has odd square, add an odd vector
in v^perp (otherwise v would be characteristic). Subtract (w^2/2)v from
the even-square partner to split U. The complement is odd indefinite
unimodular and has signature (p-1,q-1), hence is unique by the same
theorem. Matching the hyperbolic bases and their complements sends any
primitive isotropic vector to any other. Scaling preserves the action.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_ambient_coble_line_orbit():
    lattice = Lattices(ZZ)([[2]]) + (NamedLattices.U + NamedLattices.E8).twist(2)
    assert lattice.determinant() == -2048
    representatives = lattice.Aut().isotropic_orbit_representatives(1)
    assert representatives.cardinality() == 1
    line = representatives[0]
    label = tuple(line.module_generating_set())[0]
    vector = line.inclusion()(line.module_generator(label))
    assert vector.is_primitive() is True
    assert vector.q() == 0
    assert lattice.div(vector) == 2


def test_the_scaled_diagonal_form_has_the_same_ambient_transitivity():
    lattice = Lattices(ZZ)([[2,0,0,0,0],[0,2,0,0,0],[0,0,-2,0,0],[0,0,0,-2,0],[0,0,0,0,-2]])
    representatives = lattice.Aut().isotropic_orbit_representatives(1)
    assert representatives.cardinality() == 1
    line = representatives[0]
    label = tuple(line.module_generating_set())[0]
    vector = line.inclusion()(line.module_generator(label))
    assert vector.is_primitive() is True
    assert vector.q() == 0
    assert lattice.div(vector) == 2
