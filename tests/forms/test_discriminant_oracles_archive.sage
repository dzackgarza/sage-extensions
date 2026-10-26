r"""Independent discriminant-form oracles retained from the archive suite.

The finite cokernel presentation is checked against unrelated lattice data:
``|A_L|=|det G|``, root lattices have their classical discriminant groups,
the bilinear pairing is ``G^{-1}`` modulo ``ZZ``, and primary components have
exactly the prime-power orders of the finite abelian group.
"""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/tests/test_discriminant_forms.sage",
    "live_owner": "tests/forms/test_discriminant_oracles_archive.py",
    "owner_overrides": {
        "test_polarization_relates_q_and_b_by_a_factor_of_two": "tests/forms/test_discriminant_convention_archive.py",
        "test_q_is_quadratic_and_b_is_symmetric_bilinear": "tests/forms/test_discriminant_convention_archive.py",
        "test_normal_form_is_an_isometry_onto_a_smaller_generating_set": "tests/forms/test_discriminant_normal_forms_archive.py",
        "test_invariant_factor_form_is_an_isometry_on_invariant_factor_generators": "tests/forms/test_discriminant_normal_forms_archive.py",
        "test_odd_lattices_have_no_quadratic_discriminant_form": "tests/forms/test_discriminant_refinement_archive.py",
        "test_correlation_is_the_gram_matrix_into_the_dual": "tests/forms/test_discriminant_normal_forms_archive.py",
        "test_discriminant_group_of_a_direct_sum_is_the_direct_sum_of_the_groups": "tests/forms/test_discriminant_normal_forms_archive.py",
        "test_discriminant_form_convention_is_nikulins_not_peters_sterks": "tests/forms/test_discriminant_convention_archive.py",
    },
    "disposition": "reconciled-live-owner",
}


def test_discriminant_group_order_is_absolute_gram_determinant() -> None:
    for lattice in (
        Lattices.A2,
        Lattices.A3,
        Lattices.D4,
        Lattices.D5,
        Lattices.E6,
        Lattices.E7,
        Lattices.E8,
        Lattices.U,
        Lattices.U_2,
        Lattices.TEn,
        Lattices.LK3,
    ):
        assert lattice.discriminant_group().cardinality() == abs(
            int(lattice.gram_matrix().determinant())
        )


def test_root_lattice_discriminant_groups_are_the_classical_ones() -> None:
    for rank in range(2, 8):
        assert Lattices.root_lattice("A", rank).discriminant_group().cardinality() == rank + 1
    for rank in range(4, 8):
        form = Lattices.root_lattice("D", rank).discriminant_group()
        assert form.cardinality() == 4
        expected = (2, 2) if rank % 2 == 0 else (4,)
        assert tuple(form.invariants()) == expected
    for rank, order in ((6, 3), (7, 2), (8, 1)):
        assert Lattices.root_lattice("E", rank).discriminant_group().cardinality() == order


def test_discriminant_bilinear_form_is_inverse_gram_modulo_integers() -> None:
    for lattice in (Lattices.A2, Lattices.D4, Lattices.E7, Lattices.U_2):
        # The Gram matrix of L^# in the dual basis is G^{-1}, and A_L is generated
        # by the classes of that dual basis, so b_A([x], [y]) = b(x, y) mod ZZ there.
        dual = lattice.dual_lattice()
        assert dual.gram_matrix() == lattice.gram_matrix().inverse()
        form = lattice.discriminant_bilinear_form()
        for left in dual.module_generating_set():
            for right in dual.module_generating_set():
                pairing = dual.b(dual.module_generator(left), dual.module_generator(right))
                descended = form.b(form.module_generator(left), form.module_generator(right))
                assert QQ(descended.lift() - pairing) in ZZ


def test_primary_components_have_the_prime_power_orders_and_exhaust_a5() -> None:
    form = Lattices.A5.discriminant_group()
    components = form.primary_components()

    assert form.cardinality() == 6
    assert tuple(components) == (ZZ(2), ZZ(3))
    assert components[ZZ(2)].cardinality() == 2
    assert components[ZZ(3)].cardinality() == 3
    assert (
        int(components[ZZ(2)].cardinality())
        * int(components[ZZ(3)].cardinality())
        == int(form.cardinality())
    )
