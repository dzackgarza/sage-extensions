r"""Primitive totally isotropic subobjects and the cusp data they determine.

For the hyperbolic plane ``U`` with isotropic basis vector ``e``, the primitive
line ``I = Ze`` satisfies ``I^perp = I`` and hence ``I^perp / I = 0``.  This is
the smallest specimen on which the parabolic, Levi and unipotent constructions
have their defining meanings without auxiliary choices.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _isotropic_line_in_u():
    lattice = NamedLattices.U
    isotropic_vector = lattice.module_generator(0)
    return lattice.primitive_isotropic_subobject(isotropic_vector)


def test_primitive_isotropic_line_has_the_expected_perpendicular_and_reduction() -> None:
    isotropic = _isotropic_line_in_u()
    lattice = NamedLattices.U
    perpendicular = isotropic.isotropic_perpendicular()
    quotient = isotropic.isotropic_quotient()
    into_perpendicular = isotropic.into_perpendicular()
    projection = isotropic.isotropic_quotient_projection()

    assert isotropic in PrimitiveIsotropicSubobjects(ZZ)
    assert isotropic in ModuleSubobjects(ZZ)
    assert isotropic.ambient_lattice() is lattice
    assert isotropic.module_rank() == 1
    assert isotropic.is_totally_isotropic()
    assert isinstance(isotropic.module_generator(0), isotropic.ElementType)
    assert perpendicular.module_rank() == 1
    assert quotient.module_rank() == 0
    assert into_perpendicular.domain() is isotropic
    assert into_perpendicular.codomain() is perpendicular
    assert projection.domain() is perpendicular
    assert projection.codomain() is quotient
    generator = isotropic.module_generator(0)
    assert perpendicular.inclusion()(into_perpendicular(generator)) == isotropic.inclusion()(generator)


def test_identity_isometry_has_trivial_levi_actions_on_the_isotropic_line() -> None:
    isotropic = _isotropic_line_in_u()
    lattice = isotropic.ambient_lattice()
    identity = lattice.O().identity()
    quotient = isotropic.isotropic_quotient()
    restricted = isotropic.levi_restriction(identity)
    quotient_action = isotropic.levi_quotient_action(identity)

    assert isotropic.stabilizes(identity)
    assert isotropic.acts_trivially_on_isotropic_reduction(identity)
    assert restricted(isotropic.module_generator(0)) == isotropic.module_generator(0)
    assert quotient_action == quotient.Mor(quotient).identity()
    assert identity in isotropic.parabolic_subgroup()


def test_rank_one_cusp_of_u_has_trivial_unipotent_radical() -> None:
    isotropic = _isotropic_line_in_u()
    lattice = isotropic.ambient_lattice()
    identity = lattice.O().identity()
    isotropic_vector = lattice.module_generator(0)
    transvection = isotropic.eichler_transvection(isotropic_vector)
    generators = tuple(isotropic.unipotent_group_generators())
    radical = isotropic.unipotent_radical()

    assert transvection == identity
    assert generators == ()
    assert radical.order() == 1
    assert identity in radical


def test_primitive_isotropic_line_is_equivalent_to_itself_with_a_transporter() -> None:
    isotropic = _isotropic_line_in_u()
    transporter = isotropic.transporter_witness_to(isotropic)

    assert isotropic.is_equivalent_to(isotropic)
    assert transporter is not None
    assert transporter in isotropic.ambient_lattice().O()
    assert isotropic.stabilizes(transporter)


def test_primitive_isotropic_subobject_morphisms_have_identity() -> None:
    isotropic = _isotropic_line_in_u()
    identity = isotropic.Mor(isotropic).identity()

    assert identity(isotropic.module_generator(0)) == isotropic.module_generator(0)
    assert identity * identity == identity
