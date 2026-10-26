r"""Discriminant modules retain the quotient ``L^# / L`` and its maps.

For the ``A2`` lattice the discriminant module is cyclic of order three.  Its
only primary component is the 3-primary part and its only subgroups are the
trivial subgroup and the whole cyclic group.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a2_discriminant_module():
    lattice = Lattices(ZZ)("A2")
    return lattice, lattice.discriminant_group()


def test_discriminant_module_retains_lattice_dual_correlation_and_projection() -> None:
    lattice, discriminant = _a2_discriminant_module()
    dual = discriminant.dual_lattice()
    correlation = discriminant.correlation()
    projection = discriminant.projection()

    assert discriminant in DiscriminantModules(ZZ)
    assert discriminant.source_lattice() is lattice
    assert discriminant.cover() is dual
    assert correlation.domain() is lattice
    assert correlation.codomain() is dual
    assert projection.domain() is dual
    assert projection.codomain() is discriminant
    assert discriminant.cardinality() == cardinal(3)
    assert discriminant not in ModuleSubobjects(ZZ)


def test_discriminant_classes_lift_back_to_the_selected_dual_lattice() -> None:
    _lattice, discriminant = _a2_discriminant_module()
    generator = discriminant.module_generator(0)
    lift = discriminant.dual_lattice_lift(generator)

    assert discriminant.discriminant_class(lift) == generator
    assert discriminant.projection()(lift) == generator
    assert isinstance(generator, discriminant.ElementType)


def test_a2_discriminant_primary_parts_and_subgroups_are_the_cyclic_order_three_ones() -> None:
    _lattice, discriminant = _a2_discriminant_module()
    generator = discriminant.module_generator(0)
    components = discriminant.primary_components()
    generated = discriminant.subgroup_on((generator,))

    assert components.cardinality() == cardinal(1)
    assert discriminant.primary_part(3).cardinality() == cardinal(3)
    assert discriminant.primary_part(2).cardinality() == cardinal(1)
    assert generated.cardinality() == cardinal(3)
    assert generated in ModuleSubobjects(ZZ)
    assert discriminant.subgroups().cardinality() == cardinal(2)


def test_unimodular_discriminant_module_is_the_zero_quotient_not_a_subobject() -> None:
    discriminant = Lattices(ZZ)("E8").discriminant_module()

    assert discriminant in DiscriminantModules(ZZ)
    assert discriminant not in ModuleSubobjects(ZZ)
    assert discriminant.is_zero()
    assert discriminant.cardinality() == cardinal(1)


def test_rank_28_unimodular_discriminant_retains_the_full_selected_cokernel() -> None:
    lattices = Lattices(ZZ)
    hyperbolic = lattices("U")
    negative_e8 = lattices("E8").twist(-1)
    lattice = hyperbolic + hyperbolic + negative_e8 + negative_e8 + negative_e8
    discriminant = lattice.discriminant_module()

    assert lattice.module_rank() == cardinal(28)
    assert discriminant.source_lattice() is lattice
    assert discriminant.module_generating_set().cardinality() == cardinal(28)
    assert discriminant.is_zero()
    assert tuple(discriminant.invariant_factors()) == ()
    assert discriminant.form().domain().module_generating_set().cardinality() == cardinal(0)
    assert discriminant.q(discriminant.module_generator(0)) == discriminant.value_module().zero()
    assert lattice.is_p_elementary(2)


def test_discriminant_module_morphisms_have_identity() -> None:
    _lattice, discriminant = _a2_discriminant_module()
    identity = discriminant.Mor(discriminant).identity()

    assert identity(discriminant.zero()) == discriminant.zero()
    assert identity * identity == identity
