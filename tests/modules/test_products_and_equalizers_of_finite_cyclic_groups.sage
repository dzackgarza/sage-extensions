r"""Products, their universal property, and equalizers of maps of finite cyclic groups.

In $\mathbb Z\text{-Mod}$ the product $\prod_i M_i$ is the Cartesian product of the underlying
sets with componentwise operations, so $\lvert \prod_i M_i \rvert = \prod_i \lvert M_i \rvert$; the
empty product is the terminal module $0$.  A cone $(f_i: X \to M_i)$ factors uniquely through the
product by $x \mapsto (f_i(x))_i$.  The equalizer of $f, g: M \to N$ is
$\{m : f(m) = g(m)\}$ with its inclusion, and the coequalizer is $N / (f - g)(M)$, by the definitions.  On $\mathbb Z/6$,
multiplication by $5$ and the identity agree exactly on $\{x : 4x = 0\} = \{0, 3\}$, and
$\mathbb Z/6 / 4\mathbb Z/6 = \mathbb Z/2$.

An equalizing map has image in $\{0,3\}$, so it factors uniquely through the
inclusion.  A coequalizing map $h$ satisfies $4h(1)=0$ and $6h(1)=0$, hence
$2h(1)=0$, and therefore factors uniquely through the parity quotient.
Multiplication by $3$ is a nonzero example of both kinds of map; its factors
are determined by sending $1$ to the lift of $3$, and the class of $1$ to $3$,
respectively.  Injectivity of the inclusion and surjectivity of the quotient
give uniqueness.
"""

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(order):
    return Modules(ZZ)(ZZ.quotient_ring(ZZ.ideal(order)))


def test_the_order_of_a_product_is_the_product_of_the_orders() -> None:
    r"""$\lvert \mathbb Z/6 \times \mathbb Z/4 \rvert = 24$, $\lvert \mathbb Z/6 \times \mathbb Z/4
    \times \mathbb Z/3 \rvert = 72$, the unary product is $\mathbb Z/6$ and the empty product is $0$."""
    modules = Modules(ZZ)
    six, four, three = cyclic(6), cyclic(4), cyclic(3)

    assert modules.product((six, four)).cardinality() == 24
    assert modules.product((six, four, three)).cardinality() == 72
    assert modules.product((six,)).cardinality() == 6
    assert modules.product(()).cardinality() == 1


def test_empty_module_biproducts_retain_their_base_and_universal_maps() -> None:
    r"""The empty product and coproduct of finitely presented modules over R are the zero module.

    Their cones and cocones admit the unique zero morphisms for every apex,
    and the scalar ring is part of the constructed zero module's data.
    These assertions are banked for the terminal verification phase.
    """
    for ring in (ZZ, QQ):
        category = Modules(ring).FinitelyPresented()
        source = ring.free_module(1)
        product = category.product_construction(())
        coproduct = category.coproduct_construction(())
        terminal = product.object()
        initial = coproduct.object()

        assert terminal in category and initial in category
        assert terminal.base_ring() is ring and initial.base_ring() is ring
        assert terminal.is_zero() is True and initial.is_zero() is True

        cone = product.diagram().Cones().cone(source, lambda _index: None)
        to_terminal = product.factor(cone).apex_map()
        assert to_terminal.domain() is source and to_terminal.codomain() is terminal
        generator = source.module_generator(next(iter(source.module_generating_set())))
        assert to_terminal(generator) == terminal.zero()

        cocone = coproduct.diagram().CoproductCocones().cocone(source, lambda _index: None)
        from_initial = coproduct.factor(cocone).apex_map()
        assert from_initial.domain() is initial and from_initial.codomain() is source
        assert from_initial(initial.zero()) == source.zero()


def test_the_cone_of_the_identity_and_zero_factors_as_x_to_x_comma_0() -> None:
    r"""The cone $(\mathrm{id}: \mathbb Z/6 \to \mathbb Z/6, 0: \mathbb Z/6 \to \mathbb Z/4)$ factors
    through $\mathbb Z/6 \times \mathbb Z/4$ by $u(x) = (x, 0)$, and $p_0 u = \mathrm{id}$, $p_1 u = 0$."""
    modules = Modules(ZZ)
    six, four = cyclic(6), cyclic(4)
    construction = modules.product_construction((six, four))
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    identity = modules.Mor(six, six).identity()
    zero = modules.Mor(six, four)(lambda x: four.zero())
    cone = construction.diagram().Cones().cone(six, lambda index: identity if index == first else zero)
    factor = construction.factor(cone).apex_map()
    generator = six(1)

    assert construction.structure_morphism(first).codomain() is six
    assert construction.structure_morphism(second).codomain() is four
    assert construction.structure_morphism(first)(factor(generator)) == generator
    assert construction.structure_morphism(second)(factor(generator)) == four.zero()
    assert construction.structure_morphism(first)(factor(5 * generator)) == 5 * generator


def test_the_projection_after_the_factorization_is_the_leg() -> None:
    r"""$p_0 \circ u = \mathrm{id}_{\mathbb Z/6}$ as morphisms."""
    modules = Modules(ZZ)
    six, four = cyclic(6), cyclic(4)
    construction = modules.product_construction((six, four))
    shape = construction.diagram().domain()
    identity = modules.Mor(six, six).identity()
    zero = modules.Mor(six, four)(lambda x: four.zero())
    cone = construction.diagram().Cones().cone(six, lambda index: identity if index == shape(0) else zero)
    factor = construction.factor(cone).apex_map()

    assert construction.structure_morphism(shape(0)) * factor == identity


def test_three_lifts_to_the_equalizer_of_five_and_the_identity_on_z6() -> None:
    r"""$5 \cdot 3 = 15 = 3$ in $\mathbb Z/6$, so $3$ lies in the equalizer of $5$ and $\mathrm{id}$ and
    its lift maps back to $3$ under the inclusion."""
    modules = Modules(ZZ)
    six = cyclic(6)
    times_five = modules.Mor(six, six)(ZZ(5))
    assert times_five(six(1)) == six(5)
    assert times_five(six.zero()) == six.zero()
    construction = modules.equalizer_construction(times_five, modules.Mor(six, six).identity())
    inclusion = construction.structure_morphism(construction.diagram().domain().source())
    lifted = modules.equalizer_element(construction, six(3))

    assert inclusion(lifted) == six(3)
    equalizer = construction.object()
    assert inclusion.domain() is equalizer and inclusion.codomain() is six
    assert equalizer.cardinality() == 2
    assert inclusion(equalizer.zero()) == six.zero()
    assert times_five(inclusion(lifted)) == inclusion(lifted)

    times_three = modules.Mor(six, six)(ZZ(3))
    shape = construction.diagram().domain()
    cone = construction.diagram().Cones().cone(
        six,
        lambda index: times_three if index is shape.source() else times_five * times_three,
    )
    factor = construction.factor(cone).apex_map()
    specified_factor = modules.Mor(six, equalizer)({six(1): lifted})
    assert inclusion * factor == times_three
    assert inclusion * specified_factor == times_three
    assert factor == specified_factor
    assert factor(six(1)) == lifted


def test_the_equalizer_of_five_and_the_identity_on_z6_has_two_elements() -> None:
    r"""$\{x \in \mathbb Z/6 : 5x = x\} = \{0, 3\}$."""
    modules = Modules(ZZ)
    six = cyclic(6)
    times_five = modules.Mor(six, six)(ZZ(5))
    assert times_five(six(1)) == six(5)
    assert times_five(six.zero()) == six.zero()

    assert modules.equalizer(times_five, modules.Mor(six, six).identity()).cardinality() == 2


def test_the_coequalizer_of_five_and_the_identity_on_z6_is_z2() -> None:
    r"""$\mathbb Z/6 / (5 - 1)\mathbb Z/6 = \mathbb Z/6 / \{0, 2, 4\} \cong \mathbb Z/2$."""
    modules = Modules(ZZ)
    six = cyclic(6)
    times_five = modules.Mor(six, six)(ZZ(5))
    assert times_five(six(1)) == six(5)
    assert times_five(six.zero()) == six.zero()

    assert modules.coequalizer(times_five, modules.Mor(six, six).identity()).cardinality() == 2

    construction = modules.coequalizer_construction(times_five, modules.Mor(six, six).identity())
    quotient = construction.object()
    shape = construction.diagram().domain()
    projection = construction.costructure_morphism(shape.target())
    assert projection.domain() is six and projection.codomain() is quotient
    assert projection(six.zero()) == quotient.zero()
    assert projection(six(1)) != quotient.zero()
    assert projection(six(2)) == quotient.zero()
    assert projection(six(3)) == projection(six(1))
    assert projection(six(4)) == quotient.zero()
    assert projection(six(5)) == projection(six(1))
    assert projection * times_five == projection * modules.Mor(six, six).identity()

    times_three = modules.Mor(six, six)(ZZ(3))
    cocone = construction.diagram().Cocones().cocone(
        six,
        lambda index: times_three * times_five if index is shape.source() else times_three,
    )
    factor = construction.factor(cocone).apex_map()
    specified_factor = modules.Mor(quotient, six)({projection(six(1)): six(3)})
    assert factor * projection == times_three
    assert specified_factor * projection == times_three
    assert factor == specified_factor
    assert factor(projection(six(1))) == six(3)
