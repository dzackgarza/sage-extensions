r"""The discriminant reduction sequence, the spinor norm, and the Witt index of a lattice.

The spinor norm follows Gritsenko--Hulek--Sankaran, *Abelianisation of
orthogonal groups* (arXiv:0810.1614), §1: \(\mathrm{sn}_K(s_{v_1}\cdots s_{v_m})
= \prod_i -(v_i,v_i)/2\) in \(K^\times/(K^\times)^2\), \(O^+(L)=O(L)\cap\ker
\mathrm{sn}_{\mathbb R}\) and \(O'(L)=SO(L)\cap\ker\mathrm{sn}_{\mathbb Q}\).  The
Witt index is the number of hyperbolic planes split off the quadratic space
(O'Meara, *Introduction to Quadratic Forms*, §42F).
"""

from sage_extensions.all import *


def u_plus_twisted_a1():
    r"""\(U\oplus A_1(-1)=U\oplus\langle 2\rangle\), of signature \((2,1)\)."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("A1").twist(-1)


def test_square_classes_of_the_rationals_and_the_reals() -> None:
    r"""\([a]=[b]\) exactly when \(ab\) is a square; \(\mathbb R^\times/(\mathbb R^\times)^2=\{[1],[-1]\}\)."""
    rational = QQ.square_class_group()
    assert rational(8) == rational(2)
    assert rational(3) * rational(12) == rational.one()
    assert rational(-1) != rational.one()
    assert rational(2) != rational(3)

    real = RR.square_class_group()
    assert real(2) == real.one()
    assert real(-3) == real(-1)
    assert real(-1) != real.one()

    real_place = CommutativeRings().square_class_group()(QQ.Mor(RR)(lambda rational_number: RR(rational_number)))
    assert real_place(rational(-5)) == real(-1)
    assert real_place(rational(5)) == real.one()


def test_the_discriminant_reduction_sequence_of_a2() -> None:
    r"""\(O(A_2)\cong D_{12}\) maps onto \(O(q_{A_2})=\{\pm1\}\), since \(-1\) acts as \(-1\) on \(\mathbb Z/3\).

    So the cokernel is trivial and the kernel \(\tilde O(A_2)=W(A_2)\cong S_3\) has index 2.
    """
    sequence = Lattices(ZZ)("A2").discriminant_reduction_sequence()
    assert sequence.source().order() == 12
    assert sequence.target().order() == 2
    assert sequence.kernel().order() == 6
    assert sequence.kernel_inclusion().codomain() is sequence.source()
    assert sequence.cokernel().cardinality() == cardinal(1)


def test_the_discriminant_reduction_sequence_of_a1() -> None:
    r"""\(A_{A_1}=\mathbb Z/2\) has only the identity isometry, so the reduction morphism is trivial.

    Hence \(\tilde O(A_1)=O(A_1)=\{\pm1\}\), of index 1, and the cokernel is trivial.
    """
    sequence = Lattices(ZZ)("A1").discriminant_reduction_sequence()
    assert sequence.target().order() == 1
    assert sequence.kernel().order() == 2
    assert sequence.source().order() == 2
    assert sequence.cokernel().cardinality() == cardinal(1)


def test_the_discriminant_reduction_cokernel_can_be_a_nonnormal_coset_space() -> None:
    r"""For $A_2\oplus A_2\oplus E_6$, the image has order $16$ in a target of order $48$ and is not normal."""
    lattice = Lattices(ZZ)("A2") + Lattices(ZZ)("A2") + Lattices(ZZ)("E6")
    sequence = lattice.discriminant_reduction_sequence()
    cokernel = sequence.cokernel()

    assert sequence.target().order() == 48
    assert sequence.image().order() == 16
    assert not sequence.image().inclusion().is_normal()
    assert cokernel in FiniteGSets(sequence.target())
    assert cokernel.cardinality() == cardinal(3)
    assert sequence.cokernel_projection().codomain() is cokernel


def test_the_spinor_norm_is_the_whole_square_class() -> None:
    r"""On \(\langle 6\rangle\), \(-1=s_v\) with \((v,v)=6\), so \(\mathrm{sn}_{\mathbb Q}(-1)=[-3]\), neither \([1]\) nor \([-1]\)."""
    lattice = Lattices(ZZ)([[6]])
    (v,) = lattice.module_generators()
    minus_identity = lattice.Aut()((-v,))
    square_classes = QQ.square_class_group()
    assert lattice.spinor_norm()(minus_identity) == square_classes(-3)
    assert lattice.spinor_norm()(minus_identity) != square_classes(-1)
    assert lattice.spinor_norm(form_multiplier=1)(minus_identity) == square_classes(6)

    sequence = lattice.spinor_norm_sequence()
    image = sequence.image()
    projection = sequence.cokernel_projection()
    assert square_classes(-3) in image
    assert square_classes(-1) not in image
    assert projection(square_classes(-3)).is_one()
    assert not projection(square_classes(-1)).is_one()


def test_spinor_norm_and_witt_index_over_a_quadratic_number_field() -> None:
    r"""The hyperbolic plane over ``O_{QQ(sqrt(5))}`` has Witt index one on its generic fibre, and a reflection has its norm square class."""
    field = QuadraticField(5, "a")
    lattice = Lattices(field.ring_of_integers())("U")
    e, f = lattice.module_generators()
    reflection = lattice.reflection(e + f)

    assert lattice.witt_index() == 1
    assert lattice.spinor_norm(form_multiplier=1)(reflection) == field.square_class_group()(field(2))


def test_the_anisotropic_binary_spinor_image_uses_the_norm_subgroup_and_reflection_coset() -> None:
    r"""For ``<1,1>`` over ``QQ``, ``[2]`` is a rotation norm and ``[-2]`` is a reflection norm, while ``[3]`` is neither."""
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    sequence = lattice.spinor_norm_sequence()
    square_classes = QQ.square_class_group()
    image = sequence.image()
    projection = sequence.cokernel_projection()

    assert square_classes(2) in image
    assert square_classes(-2) in image
    assert square_classes(3) not in image
    assert projection(square_classes(2)).is_one()
    assert projection(square_classes(-2)).is_one()
    assert not projection(square_classes(3)).is_one()


def test_a_minus_two_reflection_in_signature_two_one_lies_in_o_plus() -> None:
    r"""For \((v,v)=-2\), \(\mathrm{sn}_{\mathbb Q}(s_v)=[1]\) and so \(\mathrm{sn}_{\mathbb R}(s_v)=+1\): \(s_v\in O^+(L)\).

    For \((w,w)=2\), \(\mathrm{sn}(s_w)=[-1]\), so \(s_w\) lies in neither kernel.
    """
    lattice = u_plus_twisted_a1()
    e, f, h = lattice.module_generators()
    reflection = lattice.reflection(e - f)
    assert lattice.spinor_norm()(reflection) == QQ.square_class_group().one()
    assert reflection in lattice.spinor_kernel()
    assert reflection in lattice.O_plus()
    assert lattice.reflection(e + f) not in lattice.spinor_kernel()
    assert lattice.reflection(e + f) not in lattice.O_plus()


def test_the_spinorial_kernel_of_u_plus_twisted_a1_lies_in_so() -> None:
    r"""\(s_{e-f}s_{e-2f+h}\) is a rotation of spinor norm \([1][1]=[1]\), so it lies in \(O'(L)\subseteq SO(L)\).

    \(s_{e-f}s_{e+f}=-1_U\oplus 1\) is a rotation of spinor norm \([1][-1]=[-1]\): in \(SO(L)\), not in \(O'(L)\).
    """
    lattice = u_plus_twisted_a1()
    e, f, h = lattice.module_generators()
    rotation = lattice.reflection(e - f) * lattice.reflection(e - 2 * f + h)
    assert rotation in lattice.spinorial_kernel()
    assert rotation in lattice.SO()
    half_turn = lattice.reflection(e - f) * lattice.reflection(e + f)
    assert half_turn in lattice.SO()
    assert half_turn not in lattice.spinorial_kernel()


def test_the_rational_spinor_norm_sequence_of_u_plus_twisted_a1() -> None:
    r"""\(L_{\mathbb Q}\) contains a hyperbolic plane, so \(\mathrm{sn}_{\mathbb Q}\) is onto (O'Meara 55:2a).

    The rational reflection \(s_{e+3f}\), with \((e+3f)^2=6\), is not integral; its spinor norm is \([-3]\).
    """
    lattice = u_plus_twisted_a1()
    sequence = lattice.spinor_norm_sequence()
    assert sequence.cokernel().order() == 1

    space = lattice.vector_space()
    a, b, c = space.module_generators()
    rational_reflection = space.reflection(a + 3 * b)
    assert sequence.morphism()(rational_reflection) == QQ.square_class_group()(-3)
    assert rational_reflection not in sequence.kernel()

    e, f, h = lattice.module_generators()
    extension = lattice.orthogonal_group_base_change(ZZ.fraction_field_map())
    assert extension(lattice.reflection(e - f)) in sequence.kernel()


def test_the_rational_spinor_norm_cokernel_of_e8_depends_on_the_multiplier() -> None:
    r"""\(E_8\) is negative definite of rank 8, so its rotations have exactly the positive classes as spinor norms (O'Meara 101:8).

    With \(c=-\tfrac12\) a reflection has the positive class \([-(v,v)/2]\), the image is the positive classes and the
    cokernel is \(\{\pm1\}\); with \(c=\tfrac12\) a reflection has a negative class and the spinor norm is onto.
    """
    lattice = Lattices(ZZ)("E8")
    assert lattice.spinor_norm_sequence().cokernel().order() == 2
    assert lattice.spinor_norm_sequence(1/2).cokernel().order() == 1


def test_the_witt_index_of_u_plus_u() -> None:
    r"""\(U\oplus U\) is hyperbolic of dimension 4: two hyperbolic planes."""
    assert (Lattices(ZZ)("U") + Lattices(ZZ)("U")).witt_index() == 2


def test_the_witt_index_of_u_plus_twisted_a1() -> None:
    r"""\(U\oplus\langle 2\rangle\) splits one hyperbolic plane off a line, which is anisotropic."""
    assert u_plus_twisted_a1().witt_index() == 1


def test_the_witt_index_of_e8() -> None:
    r"""\(E_8\) is definite, so its quadratic space is anisotropic."""
    assert Lattices(ZZ)("E8").witt_index() == 0


def test_two_u_eichler_model_can_wrap_existing_biproduct_without_rebuilding() -> None:
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    model = lattice.two_u_eichler_model_from_represented_biproduct()
    assert model.first_hyperbolic_plane() is lattice.biproduct_factor(0)
    assert model.second_hyperbolic_plane() is lattice.biproduct_factor(1)
    assert model.orthogonal_complement().module_rank() == ZZ.zero()


def test_two_u_eichler_model_retains_every_remaining_biproduct_factor() -> None:
    first_complement = Lattices(ZZ)("A1")
    second_complement = Lattices(ZZ)("A2")
    lattice = Lattices(ZZ).orthogonal_sum(
        (
            Lattices(ZZ)("U"),
            Lattices(ZZ)("U"),
            first_complement,
            second_complement,
        )
    )
    model = lattice.two_u_eichler_model_from_represented_biproduct()
    complement = model.orthogonal_complement()
    inclusion = model.complement_inclusion()

    assert complement.module_rank() == first_complement.module_rank() + second_complement.module_rank()
    assert inclusion.domain() is complement
    assert inclusion.codomain() is lattice
    assert tuple(inclusion(generator) for generator in complement.module_generators()) == tuple(
        lattice.injection(index)(generator)
        for index in (2, 3)
        for generator in lattice.biproduct_factor(index).module_generators()
    )
