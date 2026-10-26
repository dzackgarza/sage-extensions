r"""The isotropic reduction \(K_I=I^\perp/I\) and its parabolic data.

For a totally isotropic \(\iota:I\hookrightarrow L\) the form of \(L\)
descends to \(I^\perp/I\), and the descended form is nondegenerate of
signature \((p-k,q-k)\) when \(L\) has signature \((p,q)\) and
\(\operatorname{rk}I=k\).  Witt's decomposition of a hyperbolic plane off an
isotropic line is the smallest specimen of that statement:
\(U\oplus X\) reduces along a generator of the first plane to \(X\).
"""

import pytest

from sage_extensions.all import *


def test_reducing_a_hyperbolic_plane_off_an_isotropic_line_returns_the_complement() -> None:
    plane = Lattices(ZZ)("U")
    lattice = plane + plane
    isotropic = lattice.basis_vector(0)

    reduction = isotropic.isotropic_reduction()

    assert reduction.module_rank() == 2
    assert reduction.signature_pair() == signature_pair(1, 1)
    assert reduction.determinant() == -1
    assert reduction.is_even()
    assert reduction.is_isometric(plane)


def test_the_reduction_drops_one_from_each_side_of_the_signature() -> None:
    root_lattice = Lattices(ZZ)("A2")
    lattice = Lattices(ZZ)("U") + root_lattice
    assert lattice.signature_pair() == signature_pair(1, 3)

    reduction = lattice.basis_vector(0).isotropic_reduction()

    assert reduction.signature_pair() == signature_pair(0, 2)
    assert reduction.determinant() == 3
    assert reduction.is_isometric(root_lattice)


def test_nonprimitive_isotropic_vectors_keep_their_torsion_in_the_formed_quotient() -> None:
    plane = Lattices(ZZ)("U")
    isotropic = plane.module_generators()[0]
    nonprimitive = 2 * isotropic

    with pytest.raises(NotPrimitiveError):
        nonprimitive.isotropic_reduction()

    quotient = nonprimitive.isotropic_quotient()

    assert quotient in FormModules(ZZ)
    assert not quotient.is_free()
    assert tuple(quotient.invariant_factors()) == (ZZ(2),)


def test_coordinate_frame_is_excluded_from_isotropic_reduction_equality() -> None:
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    isotropic = lattice.module_generators()[0]
    reduction = isotropic.isotropic_reduction()
    labels = tuple(reduction.module_generating_set())
    frame = reduction.coordinate_frame()
    line = reduction.isotropic_sublattice()
    isotropic_in_perpendicular = reduction.isotropic_inclusion()(
        line.module_generators()[0]
    )
    shifted = {
        label: frame[label] + isotropic_in_perpendicular
        if label == labels[0]
        else frame[label]
        for label in labels
    }

    reframed = reduction.with_coordinate_frame(shifted)

    assert reframed is not reduction
    assert reframed == reduction
    assert hash(reframed) == hash(reduction)
    assert reframed.coordinate_frame()[labels[0]] != frame[labels[0]]
    for label in labels:
        assert reduction.projection()(frame[label]) == reduction.module_generator(label)
        assert (
            reframed.projection()(reframed.coordinate_frame()[label])
            == reframed.module_generator(label)
        )








def test_an_eichler_transvection_lies_in_the_unipotent_radical_of_its_parabolic() -> None:
    r"""\(t(e,a)\) fixes \(e\) and acts trivially on \(e^\perp/e\).

    That is the defining property of the unipotent radical of the parabolic
    subgroup stabilizing the isotropic line \(\mathbb Ze\), so the
    transvection must land there and its Levi image must be the identity.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    isotropic, hyperbolic_partner, root, _second_root = lattice.module_generators()
    transvection = lattice.eichler_transvection(isotropic, root)

    assert transvection(isotropic) == isotropic
    assert transvection(hyperbolic_partner) == hyperbolic_partner + root + isotropic

    reduction = isotropic.isotropic_reduction()
    assert transvection in reduction.parabolic_subgroup()
    assert reduction.levi_action()(transvection) == reduction.Aut().one()
    assert transvection in reduction.unipotent_kernel()


def test_the_reflection_in_a_root_is_parabolic_but_not_unipotent() -> None:
    r"""\(s_r\) for \(r\perp e\) stabilizes \(\mathbb Ze\) and acts as \(s_r\) on \(e^\perp/e\).

    Its Levi image is therefore a nonidentity involution, which separates the
    parabolic subgroup from its unipotent radical.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    isotropic, _partner, root, _second_root = lattice.module_generators()
    reflection = lattice.reflection(root)

    reduction = isotropic.isotropic_reduction()
    levi_image = reduction.levi_action()(reflection)

    assert reflection in reduction.parabolic_subgroup()
    assert levi_image != reduction.Aut().one()
    assert levi_image * levi_image == reduction.Aut().one()
    assert reflection not in reduction.unipotent_kernel()


def test_lifting_minus_one_splits_the_lattice_along_the_chosen_lifts() -> None:
    r"""\(-\mathrm{id}_{K_I}\) lifts to \(\mathrm{id}_M\perp(-\mathrm{id}_{K'})\).

    For \(L=U\oplus A_2\) and \(I=\mathbb Ze\) the chosen lifts span a copy
    \(K'\) of \(A_2\) whose orthogonal complement \(M\) is unimodular, so the
    Levi quotient lifts.  The lift fixes \(M\) pointwise and negates \(K'\),
    which a lift that merely happened to be parabolic would not do.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    isotropic = lattice.basis_vector(0)
    reduction = isotropic.isotropic_reduction()
    negation = reduction.Aut()(
        lambda label: -reduction.module_generator(label)
    )

    lifted = reduction.lift_isometry(negation)

    assert lifted(isotropic) == isotropic
    assert lifted != lattice.Aut().one()
    assert lifted * lifted == lattice.Aut().one()

    complement_inclusion = reduction.orthogonal_complement().inclusion()
    lifts = reduction.reduction_lifts()
    for label in reduction.module_generating_set():
        embedded_lift = complement_inclusion(lifts(label))
        assert lifted(embedded_lift) == -embedded_lift
