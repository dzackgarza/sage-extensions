r"""The cokernel of multiplication by two on $\mathbb{Z}$ is $\mathbb{Z}/2$.

The cokernel of $f : \mathbb{Z} \to \mathbb{Z}$, $n \mapsto 2n$ -- written on the
free group on one generator $g$ as $g \mapsto g^2$ -- is the closure specimen of
the issue: an actual quotient group of two elements, its quotient map out of
$\mathbb{Z}$, the kernel $2\mathbb{Z}$, and the universal factorization of every
map out of $\mathbb{Z}$ that kills $2\mathbb{Z}$.  The quotient of the codomain
by the normal closure of the image is the presented group $\langle g \mid g^2
\rangle$, which is placed abelian because the free group of rank one is, and its
presentation is the $\mathbb{Z}$-module presentation $\mathbb{Z} \to
\mathbb{Z}$, $1 \mapsto 2$; that module's Smith normal form is the single
invariant factor $2$, so the cokernel is finite of order $2$ and the map is onto.
"""

from sage_extensions.all import *


def multiplication_by_two() -> tuple:
    r"""$f : \mathbb{Z} \to \mathbb{Z}$, $g \mapsto g^2$, with $\mathbb{Z}$ the free group on one generator."""
    integers = Groups.Free(1)
    label = next(iter(integers.free_basis()))
    generator = integers.free_generator(label)
    return integers, label, generator, integers.Mor(integers)({label: generator**2})


def test_the_cokernel_of_multiplication_by_two_is_a_group() -> None:
    r"""$\operatorname{coker} f$ is a group, and one object however often it is asked for."""
    _integers, _label, _generator, squaring = multiplication_by_two()
    cokernel = squaring.cokernel()

    assert cokernel in Groups()
    assert cokernel is squaring.cokernel()


def test_the_quotient_map_has_domain_the_integers_and_codomain_the_cokernel() -> None:
    r"""The quotient map is an arrow $\mathbb{Z} \to \operatorname{coker} f$, not a bare group."""
    integers, _label, _generator, squaring = multiplication_by_two()
    projection = squaring.cokernel_projection()

    assert projection.domain() is integers
    assert projection.codomain() is squaring.cokernel()


def test_the_kernel_of_the_quotient_map_is_the_subgroup_of_even_powers() -> None:
    r"""$\ker(\mathbb{Z} \to \mathbb{Z}/2) = 2\mathbb{Z}$: an integer power of $g$ dies exactly when it is even."""
    _integers, _label, generator, squaring = multiplication_by_two()
    projection = squaring.cokernel_projection()
    cokernel = squaring.cokernel()
    kernel = projection.kernel()

    assert projection(generator**2) == cokernel.one()
    assert generator**2 in kernel
    assert generator**4 in kernel
    assert generator not in kernel
    assert generator**3 not in kernel
    assert all(
        (projection(generator**exponent) == cokernel.one()) == (exponent % 2 == 0)
        for exponent in (-4, -3, -1, 0, 1, 2, 3, 4)
    )


def test_the_cokernel_of_multiplication_by_two_has_two_elements() -> None:
    r"""$\lvert \mathbb{Z}/2 \rvert = 2$, decided from the invariant factor of the presentation.

    The presentation $\langle g \mid g^2 \rangle$ of the quotient is the
    $\mathbb{Z}$-module presentation $\mathbb{Z} \to \mathbb{Z}$, $1 \mapsto 2$,
    whose Smith normal form is the single invariant factor $2$: the quotient is
    the cyclic group of that order, not merely a group whose order happens to be
    counted some other way.
    """
    _integers, _label, _generator, squaring = multiplication_by_two()
    cokernel = squaring.cokernel()

    assert cokernel.is_finite() is True
    assert cokernel.cardinality() == 2
    assert cokernel.order() == 2
    assert tuple(cokernel.abelian_presentation_module().invariant_factors()) == (2,)


def test_every_element_of_the_cokernel_is_hit() -> None:
    r"""The quotient map is onto: the two classes are the image of $g$ and the identity."""
    _integers, _label, generator, squaring = multiplication_by_two()
    cokernel = squaring.cokernel()
    projection = squaring.cokernel_projection()

    assert projection.is_surjective() is True
    assert projection(generator) != projection(generator**2)
    assert projection(generator**2) == cokernel.one()


def test_the_universal_map_out_of_the_cokernel_is_unique_on_generators() -> None:
    r"""A map out of $\mathbb{Z}$ killing $2\mathbb{Z}$ descends uniquely to $\mathbb{Z}/2$.

    $g \mapsto h$ for $h$ of order two kills $g^2$, so it factors through the
    projection; a homomorphism out of the quotient is determined by the image of
    the quotient's chosen generator, and the descended map is exactly that
    homomorphism.
    """
    integers, label, generator, squaring = multiplication_by_two()
    cokernel = squaring.cokernel()
    projection = squaring.cokernel_projection()
    target = Groups.C(2)
    involution = next(iter(target.group_generators()))
    reduction = integers.Mor(target)({label: involution})
    descent = cokernel.descend_homomorphism(reduction, through=projection)
    (quotient_generator,) = cokernel.group_generators()

    assert projection(generator) == quotient_generator
    assert descent(quotient_generator) == involution
    assert all(
        descent(projection(generator**exponent)) == reduction(generator**exponent)
        for exponent in (0, 1, 2, 3, -1, -2)
    )
    assert cokernel.Mor(target)({quotient_generator: involution}) == descent
