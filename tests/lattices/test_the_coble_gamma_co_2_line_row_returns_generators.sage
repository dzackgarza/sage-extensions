r"""The `Gamma_{Co,2}` line row on `T_Co` reaches its stabilizer's image (sage-extensions#358).

`T_Co = <2> + U(2) + E8(-2)` is the Coble period lattice: D. Dolgachev and S. Kondo, *Enriques
surfaces and Borel--Weil--Bott type duality*, Izv. Math. 77:3 (2013), Section 3, equation (3.6),
printed p. 513, with `E8` negative definite as the source's signature `(2, 9)` forces.  Its
discriminant group `A_{T_Co}` has exponent two, and over `F_2` it splits into three pairwise
orthogonal summands,

.. MATH::

    A_{T_\mathrm{Co}} = A_{U(2)} \perp A_{E8(-2)} \perp \langle [h/2] \rangle,

the first two being `[h/2]^\perp` (order `4 * 256 = 1024`, the index of a hyperplane) and the
third the class of the `U(2)`-transversal `h/2` of `\langle 2 \rangle`'s generator, whose
`q`-value `1/2` puts it outside its own orthogonal complement.

`Gamma_{Co,2} = R_{Gamma_{En,2}}` is the preimage in `O(T_Co)` of `P`, the stabilizer in `O(q)`
of that decomposition (research `prop:gamma-co-images`, `38fa09935a`), and the call this test
pins is `discriminant_point_stabilizer` at the point `A_{U(2)}`
(`tests/lattices/test_the_decomposition_preimage_returns_generators.sage` pins the same call on
card `0125`).  `A_{U(2)}` is nondegenerate with nondegenerate orthogonal complement, so an
isometry preserves it exactly when it preserves the decomposition, and restriction is an
isomorphism `P -> O(A_{U(2)}) x O(A_{U(2)}^\perp)`;
`A_{U(2)}^\perp = A_{E8(-2)} \perp \langle [h/2] \rangle` is the discriminant form of
`E8(-2) + <2>`.  Hence

.. MATH::

    |P| = |O(q_{U(2)})| \cdot |O(q_{E8(-2) + <2>})|,

computed on the two summand lattices' own discriminant orthogonal groups.  The second,
independent route is the index--stabilizer identity `|P| * [O(T_Co) : Gamma_{Co,2}] = |O(q)|`,
with the index read from the character quotient of the preimage and `|O(q)|` from `O(A_{T_Co})`.

The call used to hand `P` over as a bare predicate.  `O(A_{T_Co})` is a finite group, and this
library's canonical free cover of a finite group is the one on *all* of its elements, so a
generator request on a predicate subgroup of it filters an enumeration of the whole group: the
preimage's joint discriminant image entered that enumeration and was killed at 4282 MiB without
returning in 2400 s (`orthogonal_quotients.py:706`, `_joint_discriminant_image_gap`, reached from
`isotropic_orbit_representatives` through `splitting_isometries`).  `P` is now also generated, by
the engine's own setwise stabilizer of the point (GAP's `Stabilizer`; Holt--Eick--O'Brien,
*Handbook of Computational Group Theory*, Chapman & Hall/CRC, 2005, Section 4.1, p. 79), and it is
that family whose images the assertions below measure.

Which claim about generators this test makes, and why not the Schreier family: on card `0125` the
Schreier family of the same point has `15 * 67456 - 67455` members and
`discriminant_point_stabilizer_image_generators` selects nine of them.  On `T_Co` the ambient
family has ~330 letters at the same `67456`-point orbit, so the Schreier family has ~22 000 000
members and its realization is killed at 5484 MiB against the runtime's 6144 MiB guard
(`results/issue358-the-gamma-co-2-line-row.md` records both runs; what is missing is the cheap
walk representation that sage-extensions#296 names).  The lifting route is refused by the same
wall: `discriminant_lift` of one generator of `P` alone is killed at 6254 MiB, because it searches
the ambient family's products for a word with that discriminant image.  So the order asserted here
is `rho(Gamma_{Co,2})`'s, read as the owned subgroup `discriminant_image()` of `O(q)` and,
independently, from the character quotient's joint discriminant image --- the same two-order
argument `stabilizer_discriminant_image_orders` uses for the parabolic's image
(`isotropic_parabolics.py:2366`), and the claim the issue's acceptance states: the stabilizer's
image in `O(q)` has order `|P|`, computed in `O(q)`.

What is asserted is what the public calls compute: the decomposition by construction, `|P|` three
ways (the summands' isometry-group orders, the engine's setwise stabilizer of the point, and
`|O(q)|` divided by the index), the index `[O(T_Co) : Gamma_{Co,2}]`, `rho(Gamma_{Co,2})`'s order
as an owned subgroup of `O(q)` and from the character quotient's joint discriminant image, and
that every generator of the stabilizer fixes the point.  No count is typed: `|P| * index = |O(q)|`
is the index--stabilizer identity with `|P|` read a second way, and a wrong point, a wrong
stabilizer or a wrong image each break one of the assertions.  The row itself
(`isotropic_orbit_representatives(1)` on `Gamma_{Co,2}`) is measured in
`results/issue358-the-gamma-co-2-line-row.md`, not here: it is minutes of computation and pins no
value this test does not.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _span(form, family):
    r"""The span of a finite family of classes of `A_L` over `ZZ/2ZZ`, as a set of classes."""
    closure = {form.zero()}
    for generator in family:
        closure |= {element + generator for element in closure}
    return frozenset(closure)


def _classes(lattice):
    r"""One class of `A_L` per named module generator: the primitive dual's class."""
    return {
        label: lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator(label)))
        for label in lattice.module_generating_set()
    }


def _decomposition(lattice):
    r"""`(A_{U(2)}, A_{E8(-2)}, [h/2])`, the three summands of `A_{T_Co}` by construction."""
    form = lattice.discriminant_group()
    classes = _classes(lattice)
    return (
        _span(form, (classes["ep"], classes["fp"])),
        _span(form, tuple(classes[f"a{index}"] for index in range(1, 9))),
        frozenset({form.zero(), classes["h"]}),
    )


def _same_class_set(left, right):
    r"""Whether two finite class sets have the same members, compared class by class.

    The comparison is by `==` member by member, never through Python's set operators: in a `.sage`
    test a set literal is an owned finite set (`{x}` is not a `set`), so `{x} == frozenset({x})` is
    a comparison across two kinds and answers `False` however the classes compare, and a
    `frozenset - {x}` raises.  This helper states the class-level question in the one form that
    does not depend on either kind.
    """
    return all(
        any(member == other for other in right) for member in left
    ) and all(any(member == other for member in left) for other in right)


def _summand_orders():
    r"""`(|O(q_{U(2)})|, |O(q_{E8(-2) + <2>})|)`: the two factors of `|P|`, computed in O(q).

    The decomposition's complement is the discriminant form of the lattice
    `E8(-2) + <2>`, whose orthogonal group is read on that lattice's own discriminant group.
    """
    return (
        int(NamedLattices.U_2.discriminant_group().orthogonal_group().cardinality()),
        int(
            (NamedLattices.E8_2 + NamedLattices.Z_2)
            .discriminant_group()
            .orthogonal_group()
            .cardinality()
        ),
    )


def test_the_coble_gamma_co_2_line_row_returns_its_stabilizer_image() -> None:
    r"""The decomposition, `|P|`, the index, and `Gamma_{Co,2}`'s image in `O(q)`.

    The computations are: the three summands of `A_{T_Co}` from the lattice's own Gram data, the
    summand lattices' isometry-group orders, `O(q)`'s own order, the preimage's character
    quotient (its index, its character image, its joint discriminant image), and the owned
    subgroup `rho(Gamma_{Co,2})` with its generators.  Nothing is typed: every number asserted on
    the right is computed, and the two routes to `|P|` are independent -- one from the two
    summands' orthogonal groups, one from `|O(q)|` and the index.
    """
    lattice = NamedLattices.Tco
    form = lattice.discriminant_group()
    orthogonal = form.orthogonal_group()
    order = int(orthogonal.cardinality())
    zero = form.zero()
    zero_q = form.b(zero, zero)

    A_U2, A_E8, half = _decomposition(lattice)
    point = A_U2

    # The decomposition is by construction, not by a described list: three pairwise orthogonal
    # summands that generate the whole of A_{T_Co}, and [h/2]^perp is exactly the first two.
    # Sumsets are compared by membership and by count: a set literal in a `.sage` test is an owned
    # finite set, so a Python set comparison across the two kinds answers False however the
    # classes compare.
    sums = {left + middle + right for left in A_U2 for middle in A_E8 for right in half}
    assert all(sum_ in form for sum_ in sums)
    assert cardinal(sum(1 for _ in sums)) == form.cardinality()
    # A direct sum: the three orders multiply to |A|, so the sums above being all of A makes the
    # sum map from the product injective and the three summands pairwise trivially intersecting.
    assert (
        cardinal(sum(1 for _ in A_U2))
        * cardinal(sum(1 for _ in A_E8))
        * cardinal(sum(1 for _ in half))
        == form.cardinality()
    )
    assert all(form.b(left, right) == zero_q for left in A_U2 for right in A_E8)
    assert all(form.b(left, right) == zero_q for left in A_U2 for right in half)
    assert all(form.b(left, right) == zero_q for left in A_E8 for right in half)
    half_class = next(class_ for class_ in half if class_ != zero)
    in_perpendicular = {left + middle for left in A_U2 for middle in A_E8}
    assert all(form.b(sum_, half_class) == zero_q for sum_ in in_perpendicular)
    perpendicular = {
        class_ for class_ in form.elements() if form.b(class_, half_class) == zero_q
    }
    assert cardinal(sum(1 for _ in in_perpendicular)) == cardinal(
        sum(1 for _ in perpendicular)
    )

    # |P|, first route: the two summand lattices' own orthogonal groups.
    first_summand, second_summand = _summand_orders()
    product = first_summand * second_summand

    # |P|, second route: the engine's own setwise stabilizer of the point in O(q), which is the
    # subgroup the preimage below is taken of, with its generators.
    stabilizer = orthogonal.stabilizer_of_classes(point)
    assert int(stabilizer.cardinality()) == product
    stabilizer_generators = tuple(stabilizer.group_generators())
    for generator in stabilizer_generators:
        assert _same_class_set(
            frozenset(generator(class_) for class_ in point), point
        )

    group = lattice.Aut()
    preimage = group.discriminant_point_stabilizer(point)
    quotient = preimage.finite_character_quotient()
    index = quotient.index()

    # |P|, third route: the index-stabilizer identity, with |O(q)| computed above.
    assert index * product == order
    # rho_L is onto here, which is what makes a preimage's discriminant image P itself.
    assert int(lattice.discriminant_image().cardinality()) == order
    assert quotient.image_order() == order
    # rho(Gamma_{Co,2}) is P, read as a subgroup of O(q): its order is |P| in O(q), two ways --
    # the owned subgroup itself, and the character quotient's joint discriminant image.
    assert int(preimage.discriminant_image().cardinality()) == product
    assert quotient.subgroup_image_order() == product
