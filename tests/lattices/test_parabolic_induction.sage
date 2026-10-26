r"""Parabolic subgroups of primitive isotropic subobjects, and Eichler transvections.

The specimen is the even unimodular Lorentzian lattice ``E10 = U + E8``, for
which ``e^perp/e`` is ``E8`` (Conway--Sloane, *Sphere Packings, Lattices and
Groups*, ch. 26: ``II_{1,9} = U + E8``), so the cusp of the isotropic line
``Z e`` has ``E8`` as its reduction lattice.
"""

from sage_extensions.all import *


def _lorentzian_line():
    lattice = NamedLattices.E10
    return lattice, lattice.primitive_isotropic_subobject(lattice.module_generators()[0])


def _acts_as_identity(restriction, module) -> bool:
    return all(
        restriction(generator) == generator for generator in module.module_generators()
    )


def test_primitive_isotropic_refinement_selects_the_line_eichler_operation() -> None:
    lattice, line = _lorentzian_line()
    module_generators = tuple(lattice.module_generators())
    isotropic = module_generators[0]
    root = module_generators[2]

    transvection = line.eichler_transvection(root)
    family = line.unipotent_group_generators()

    assert transvection(isotropic) == isotropic
    assert tuple(family.index_set()) == tuple(
        line.isotropic_perpendicular().module_generating_set()
    )


def test_the_isotropic_line_of_E10_reduces_to_E8() -> None:
    lattice, line = _lorentzian_line()

    assert line.is_totally_isotropic()
    assert line.is_primitive()
    assert line.module_rank() == 1
    assert line.ambient_lattice() is lattice

    assert line.isotropic_perpendicular().module_rank() == 9
    assert line.isotropic_quotient().module_rank() == 8
    reduction = line.isotropic_reduction()
    assert reduction.module_rank() == 8
    assert reduction.is_isometric(NamedLattices.E8)


def test_eichler_transvections_lie_in_the_unipotent_radical() -> None:
    lattice, line = _lorentzian_line()
    module_generators = tuple(lattice.module_generators())
    isotropic, hyperbolic_partner = module_generators[:2]
    root = module_generators[2]
    assert lattice.b(isotropic, root) == 0
    assert root.q() == -2

    transvection = line.eichler_transvection(root)
    assert transvection.parent() is lattice.Aut()
    assert transvection != lattice.Aut().identity()
    assert transvection(isotropic) == isotropic
    assert transvection(hyperbolic_partner) == hyperbolic_partner + isotropic - root
    assert transvection(hyperbolic_partner).q() == hyperbolic_partner.q()

    assert line.stabilizes(transvection)
    assert transvection in line.parabolic_subgroup()
    assert transvection in line.unipotent_radical()
    assert line.acts_trivially_on_isotropic_reduction(transvection)
    assert _acts_as_identity(line.levi_restriction(transvection), line)


def test_the_eichler_transvections_of_a_line_form_an_abelian_group() -> None:
    lattice, line = _lorentzian_line()
    module_generators = tuple(lattice.module_generators())
    isotropic = module_generators[0]
    first, second = module_generators[2:4]

    left = line.eichler_transvection(first)
    right = line.eichler_transvection(second)
    assert left * right == line.eichler_transvection(first + second)
    assert left * right == right * left
    assert ~left == line.eichler_transvection(-first)
    assert line.eichler_transvection(isotropic) == lattice.Aut().identity()
    assert line.eichler_transvection(lattice.zero()) == lattice.Aut().identity()

    family = line.unipotent_group_generators()
    assert family.index_set() is line.isotropic_perpendicular().module_generating_set()
    assert all(transvection in line.unipotent_radical() for transvection in family)


def test_the_two_isotropic_lines_of_two_hyperbolic_planes_are_one_orbit() -> None:
    lattice = NamedLattices.U + NamedLattices.U
    first = lattice.primitive_isotropic_subobject(lattice.module_generators()[0])
    second = lattice.primitive_isotropic_subobject(lattice.module_generators()[2])

    assert first.isotropic_reduction().is_isometric(NamedLattices.U)
    assert second.isotropic_reduction().is_isometric(NamedLattices.U)

    witness = first.transporter_witness_to(second)
    assert second.inclusion().is_in_image(witness(lattice.module_generators()[0]))
    assert first.is_equivalent_to(second)


def test_the_saturation_of_the_line_through_twice_e_is_the_line_through_e() -> None:
    r"""In \(U\), \(U/\mathbb Z(2e)\cong\mathbb Z/2\oplus\mathbb Z\) has torsion, so
    \(\mathbb Z(2e)\) is not primitive; its saturation \((\mathbb Z(2e)\otimes\mathbb Q)\cap U\)
    is \(\mathbb Ze\), which is primitive and contains \(e\).
    """
    lattice = NamedLattices.U
    vector = lattice.module_generators()[0]

    doubled = lattice.subobject_on((2 * vector,))
    assert not doubled.is_primitive()

    saturated = doubled.saturation()
    assert saturated.module_rank() == 1
    assert saturated.is_primitive()
    assert saturated.inclusion().is_in_image(vector)
