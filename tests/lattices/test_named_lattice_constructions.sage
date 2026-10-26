r"""The catalogue constructors of unimodular lattices, root lattices and K3 complements.

- \(I_{p,q} = \langle1\rangle^{p}\oplus\langle-1\rangle^{q}\) is odd and unimodular with
  determinant \((-1)^q\).
- The signature of an even unimodular lattice is divisible by 8 (Milnor--Husemoller,
  *Symmetric Bilinear Forms*, Ch. II, Theorem 5.1), so there is no \(II_{1,2}\); in the
  negative definite convention of this repository \(II_{1,9} = U \oplus E_8\), of
  determinant \(-1\).
- \(\langle -2d\rangle \oplus U^2 \oplus E_8^2\) has signature
  \((0,1)+(2,2)+(0,16) = (2,19)\) and determinant \(-2d\cdot(-1)^2\cdot1^2\).
- The determinant of a tensor product of forms of ranks \(m,n\) is
  \(\det(A)^n\det(B)^m\); its signature pairs the signs of the eigenvalue products.
- The highest root \(\theta\) is the maximal root: \(\theta+\alpha\) has square below \(-2\) for every
  simple root \(\alpha\), so it is not a root of square \(-2\).  A simply laced root lattice of rank \(n\) and Coxeter number
  \(h\) has \(nh\) roots (Conway--Sloane, SPLAG, Ch. 4, section 2), so \(h(D_4) = 24/4 = 6\)
  and \(h(E_8) = 240/8 = 30\).
"""

import pytest

from sage_extensions.all import *


def test_the_odd_unimodular_lattice_i_2_1() -> None:
    lattice = Lattices.IPQ(2, 1)

    assert lattice.signature_pair() == signature_pair(2, 1)
    assert lattice.determinant() == -1
    assert lattice.is_unimodular()
    assert not lattice.is_even()


def test_the_even_unimodular_lattices_ii_1_9_and_ii_9_1() -> None:
    negative = Lattices.IIPQ(1, 9)
    positive = Lattices.IIPQ(9, 1)

    assert negative.signature_pair() == signature_pair(1, 9)
    assert negative.determinant() == -1
    assert negative.is_even()
    assert negative.is_unimodular()
    assert positive.signature_pair() == signature_pair(9, 1)
    assert positive.is_even()
    assert positive.determinant() == -1


def test_there_is_no_even_unimodular_lattice_of_signature_1_2() -> None:
    with pytest.raises(ValueError):
        Lattices.IIPQ(1, 2)


def test_the_dolgachev_pinkham_dual_lattice_retains_its_metric_form() -> None:
    r"""The metric dual of U + U(2) + E8^2 has Gram matrix G^{-1} over QQ.

    The dual remains a lattice over the original owned integer ring; only its
    pairing takes values in the fraction field.
    """
    from sage.matrix.constructor import matrix
    from sage.rings.rational_field import QQ as SageQQ

    from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
    from sage_extensions.categories.modules.pure.modules import Modules
    from sage_extensions.categories.rings.ring_foundation import _engine_element

    lattice = NamedLattices.TdP
    dual = lattice.dual_lattice()
    gram = matrix(
        SageQQ,
        [
            [SageQQ(_engine_element(ZZ, entry)) for entry in row]
            for row in lattice.gram_tensor()._component_array()
        ],
    )
    labels = tuple(lattice.module_generating_set())
    dual_gram = matrix(
        SageQQ,
        [
            [
                SageQQ(_engine_element(QQ, dual.gram_tensor()[i, j]))
                for j in range(20)
            ]
            for i in range(20)
        ],
    )

    assert dual in FormModules(ZZ)
    assert dual.base_ring() is lattice.base_ring() is ZZ
    assert dual.module_rank() == lattice.module_rank() == 20
    assert dual.unformed_module() is lattice.dual_module()
    assert dual.module_generating_set() is lattice.module_generating_set()
    assert dual.form().codomain() is dual.value_module()
    assert dual.value_module() is Modules(QQ).restriction_of_scalars(
        ZZ.fraction_field_map()
    )(QQ.regular_module())
    assert dual_gram == gram.inverse()
    assert dual.signature_pair() == lattice.signature_pair() == signature_pair(2, 18)
    assert lattice.determinant() * dual.determinant() == QQ.one()


def test_a_restricted_rank_two_value_module_is_not_scalarized_for_determinants() -> None:
    from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
    from sage_extensions.categories.modules.pure.modules import Modules
    from sage_extensions.tensors.tensor import Tensor

    module = Modules(ZZ).free_module(1)
    values = Modules(QQ).restriction_of_scalars(ZZ.fraction_field_map())(QQ**2)
    form = module.bilinear_hom_space(values)._from_bilinear_evaluation(
        lambda left, right: values.zero()
    )
    formed = FormModules(ZZ)(form)

    try:
        formed.determinant()
    except AssertionError as error:
        assert "needs numerical scalar data" in str(error)
    else:
        raise AssertionError("a QQ^2-valued form was incorrectly assigned a scalar determinant")
    assert not isinstance(form._as_numerical_tensor(), Tensor)


def test_the_k3_complement_of_a_degree_two_polarization() -> None:
    lattice = Lattices.LK3_2d(1)

    assert lattice.signature_pair() == signature_pair(2, 19)
    assert lattice.determinant() == -2
    assert lattice.is_even()


def test_rank_one_negative_lattices_and_the_root_lattice_constructor() -> None:
    assert Lattices.rank_one_negative(3).determinant() == -6
    assert Lattices.rank_one_negative(3).is_negative_definite()
    assert Lattices.root_lattice("D", 4).determinant() == 4
    assert Lattices.root_lattice("D", 4).is_negative_definite()


def test_the_tensor_product_of_a2_with_u_and_with_itself() -> None:
    root_lattice = Lattices(ZZ)("A2")
    plane = Lattices(ZZ)("U")

    assert (root_lattice @ plane).determinant() == 9
    assert (root_lattice @ plane).signature_pair() == signature_pair(2, 2)
    assert (root_lattice @ root_lattice).determinant() == 81
    assert (root_lattice @ root_lattice).is_positive_definite()


def test_the_zeroth_orthogonal_power_is_the_unit_of_the_orthogonal_sum() -> None:
    root_lattice = Lattices(ZZ)("A2")

    assert (root_lattice ** 0).determinant() == 1
    assert (root_lattice ** 0 + root_lattice).determinant() == 3


def test_an_orthogonal_sum_splits_into_its_indecomposable_summands() -> None:
    root_lattice = Lattices(ZZ)("A2")
    lattice = root_lattice + Lattices(ZZ)("U") + root_lattice
    summands = lattice.indecomposable_summands()

    assert lattice.is_decomposable()
    assert summands[0].determinant() == 3
    assert summands[1].is_unimodular()
    assert summands[1].signature_pair() == signature_pair(1, 1)
    assert summands[2].is_negative_definite()


def test_the_highest_roots_of_d4_and_e8() -> None:
    for name, coxeter_number in (("D4", 6), ("E8", 30)):
        lattice = Lattices(ZZ)(name)
        highest = lattice.highest_root()

        assert highest.is_root()
        for simple_root in lattice.simple_roots():
            assert (highest + simple_root).q() < -2
        assert lattice.coxeter_number() == coxeter_number


def test_products_of_vectors_are_the_bilinear_form_and_divisibility_scales() -> None:
    r"""In \(A_2\) with Gram \(\begin{pmatrix}-2&1\\1&-2\end{pmatrix}\), \(e_0e_1 = 1\) and
    \(e_0, e_0+e_1\) are roots.  In the unimodular \(U\) a basis
    vector has divisibility 1 and its double divisibility 2."""
    root_lattice = Lattices(ZZ)("A2")
    first, second = root_lattice.module_generators()
    plane = Lattices(ZZ)("U")
    isotropic, _other = plane.module_generators()

    assert first * second == 1
    assert first * first == -2
    assert first.is_root()
    assert (first + second).is_root()
    assert plane.div(isotropic) == 1
    assert (2 * isotropic).div() == 2
