r"""The glue map of an odd lattice, and the even statement it must not weaken.

Peters and Sterk, *Symmetric and Quadratic Forms, with Applications to Coding
Theory, Algebraic Geometry and Topology* (version of June 2024), state the
primitive-extension correspondence for both parities at once, as "symmetric
(respectively quadratic)".  Prop. 15.1.1 reads ``L/(S + R)`` as the graph of an
anti-isometry of the two discriminant forms: bilinear, valued in ``QQ/ZZ``, for
an integral ``L``, and quadratic, valued in ``QQ/2ZZ``, when ``L`` is even.
Prop. 1.7.4 matches integral overlattices with the bilinear-isotropic subgroups
of the discriminant group and even overlattices with the quadratic-isotropic
ones, which is a strictly smaller collection.

The odd specimen here is the classical splitting of the cubic lattice ``I_3``
along its diagonal: ``S = ZZ(e1+e2+e3)`` is ``<3>``, which is odd, its
orthogonal complement is a copy of ``A_2``, which is even, and the two are
glued along a group of order three.  A summand of an odd lattice can therefore
carry a quadratic discriminant form while the extension does not, and this is
why the glue of an odd lattice is read off the bilinear forms.
"""

from sage_extensions.all import *


def _cubic_lattice_split():
    r"""Return ``I_3`` with its diagonal ``<3>`` and the ``A_2`` orthogonal to it."""
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    first, second, third = (lattice.module_generator(label) for label in (0, 1, 2))
    diagonal = lattice.subobject_on((first + second + third,))
    complement = lattice.subobject_on((first - second, second - third))
    return lattice, diagonal, complement


def test_the_glue_of_an_odd_lattice_is_an_anti_isometry_of_bilinear_forms() -> None:
    lattice, diagonal, complement = _cubic_lattice_split()
    values = FractionFieldQuotients(ZZ)(1)

    assert not lattice.is_even()
    assert diagonal.module_rank() + complement.module_rank() == lattice.module_rank()
    assert diagonal.is_primitive()
    assert complement.is_primitive()
    assert diagonal.sum(complement).index() == 3

    glue = lattice.glue_map(diagonal, complement)
    source = glue.domain()
    target = glue.codomain()

    assert not glue.is_quadratic()
    assert source in TorsionBilinearFormModules(ZZ)
    assert source not in TorsionQuadraticFormModules(ZZ)
    assert target in TorsionBilinearFormModules(ZZ)
    assert target not in TorsionQuadraticFormModules(ZZ)
    assert source.cardinality() == 3

    # <3> pairs every nonzero class to 1/3 and A_2 pairs every nonzero class to
    # 2/3, so the two discriminant forms are anti-isometric and not isometric.
    diagonal_form = diagonal.discriminant_module()
    complement_form = complement.discriminant_module()
    assert values(QQ(2) / 3) == -values(QQ(1) / 3)
    assert all(
        diagonal_form.b(element, element) == values(QQ(1) / 3)
        for element in diagonal_form.elements()
        if element != diagonal_form.zero()
    )
    assert all(
        complement_form.b(element, element) == values(QQ(2) / 3)
        for element in complement_form.elements()
        if element != complement_form.zero()
    )

    # The arrow lands in the twist A_R(-1), where the anti-isometry is an
    # isometry: without that twist the image would pair to 2/3.
    generator = source.module_generators()[0]
    assert source.b(generator, generator) == values(QQ(1) / 3)
    assert target.b(glue(generator), glue(generator)) == source.b(generator, generator)


def test_an_even_lattice_glues_through_its_quadratic_discriminant_forms() -> None:
    lattice = Lattices(ZZ)("U")
    first, second = lattice.module_generator(0), lattice.module_generator(1)
    invariant = lattice.subobject_on((first + second,))
    coinvariant = lattice.subobject_on((first - second,))
    values = FractionFieldQuotients(ZZ)(2)

    assert lattice.is_even()
    assert invariant.sum(coinvariant).index() == 2

    glue = lattice.glue_map(invariant, coinvariant)
    source = glue.domain()
    target = glue.codomain()

    assert glue.is_quadratic()
    assert source in TorsionQuadraticFormModules(ZZ)
    assert target in TorsionQuadraticFormModules(ZZ)
    assert source.cardinality() == 2

    generator = source.module_generators()[0]
    assert source.q(generator) == values(QQ(1) / 2)
    assert target.q(glue(generator)) == source.q(generator)

    # q is -1/2 on the coinvariant side, which is 3/2 in QQ/2ZZ, so the glue is
    # an anti-isometry of quadratic forms and the twist is what makes the
    # returned arrow an isometry.
    coinvariant_form = coinvariant.discriminant_module()
    assert all(
        coinvariant_form.q(element) == -values(QQ(1) / 2)
        for element in coinvariant_form.elements()
        if element != coinvariant_form.zero()
    )


def test_a_bilinear_isotropic_class_of_u2_gives_the_odd_overlattice() -> None:
    # Peters--Sterk, Example 1.7.5.1: of the three subgroups of order two in
    # A_{U(2)}, all three are bilinear-isotropic and only two are
    # quadratic-isotropic.  The remaining one is the class of e, and it glues
    # U(2) up to the odd unimodular lattice ZZ e + ZZ f.
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    discriminant = lattice.discriminant_module()
    bilinear = discriminant.associated_bilinear_form()

    # Peters--Sterk, Example 1.7.5.1: including the zero subgroup, the
    # bilinear form admits four isotropic subgroups and its quadratic
    # refinement only three. The two enumeration paths contract different
    # quotient-valued forms on the same underlying finite group.
    assert bilinear.isotropic_subgroups().cardinality() == 4
    assert discriminant.isotropic_subgroups().cardinality() == 3
    e, f = lattice.module_generator(0), lattice.module_generator(1)
    # e + f has divisibility 2 in U(2), so its divided class is the class of (e + f)/2.
    odd_class = (e + f).divided_discriminant_class()

    assert discriminant.cardinality() == 4
    assert discriminant.b(odd_class, odd_class) == FractionFieldQuotients(ZZ)(1).zero()
    assert discriminant.q(odd_class) == FractionFieldQuotients(ZZ)(2)(QQ(1))

    inclusion = lattice.overlattice(odd_class)
    enlarged = inclusion.codomain()

    assert inclusion.index() == 2
    assert not enlarged.is_even()
    assert abs(enlarged.determinant()) == 1


def test_an_odd_orthogonal_sum_glues_up_to_a_unimodular_lattice() -> None:
    # <3> + A_2, the orthogonal sum split off the cubic lattice above.  It is
    # odd, so its discriminant group carries no quadratic form, and the glue
    # class of order three recovers a unimodular odd lattice of index three.
    summands = Lattices(ZZ)([[3, 0, 0], [0, 2, -1], [0, -1, 2]])
    discriminant = summands.discriminant_module()
    # w = e_1 + 2 e_2 + e_3 pairs to (3, 3, 0) with the basis, so it has divisibility 3
    # and its divided class is the class of w/3, of order three.
    e_1, e_2, e_3 = (summands.module_generator(label) for label in (0, 1, 2))
    glue_class = (e_1 + 2 * e_2 + e_3).divided_discriminant_class()

    assert not summands.is_even()
    assert discriminant in TorsionBilinearFormModules(ZZ)
    assert discriminant not in TorsionQuadraticFormModules(ZZ)
    assert discriminant.cardinality() == 9
    assert discriminant.b(glue_class, glue_class) == FractionFieldQuotients(ZZ)(1).zero()

    inclusion = summands.overlattice(glue_class)
    enlarged = inclusion.codomain()

    assert inclusion.index() == 3
    assert not enlarged.is_even()
    assert abs(enlarged.determinant()) == 1
