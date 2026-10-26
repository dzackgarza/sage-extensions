r"""The unimodular hyperbolic plane has one discriminant class covering root square."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_root_square_has_only_zero_covering_class() -> None:
    lattice = NamedLattices.U
    classes = lattice.covering_discriminant_classes(-2)

    assert classes.cardinality() == cardinal(1)
    assert lattice.discriminant_group().zero() in classes


def test_zero_lattice_uses_unformed_smith_workspace_for_covering_class() -> None:
    lattice = Lattices(ZZ)(ZZ.free_module(0))
    discriminant = lattice.discriminant_group()
    classes = lattice.covering_discriminant_classes(ZZ.zero())
    zero_subgroup = discriminant.subgroup_on(())
    subgroups = discriminant.subgroups()

    assert classes.cardinality() == cardinal(1)
    assert tuple(classes) == (discriminant.zero(),)
    assert zero_subgroup.cardinality() == cardinal(1)
    assert tuple(zero_subgroup.embedded_elements()) == (discriminant.zero(),)
    assert subgroups.cardinality() == cardinal(1)
    assert tuple(subgroups)[0].cardinality() == cardinal(1)


def test_covering_classes_match_the_defining_discriminant_predicate() -> None:
    lattice = Lattices(ZZ)("A3").twist(ZZ(2))
    discriminant = lattice.discriminant_group()
    values = discriminant.quadratic_value_module()
    field = lattice.base_ring().fraction_field()

    for square in (ZZ.zero(), ZZ(2)):
        target = field(square)
        expected = tuple(
            element
            for element in discriminant.elements()
            if discriminant.q(element)
            == values(target / field(element.additive_order()) ** 2)
        )

        assert tuple(lattice.covering_discriminant_classes(square)) == expected
