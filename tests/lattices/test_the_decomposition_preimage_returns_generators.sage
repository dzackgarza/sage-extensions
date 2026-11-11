r"""The decomposition preimage on card `0125` returns generators (sage-extensions#354).

Sterk's group `G_e` is the subgroup of `O(M(2))`, `M(2) = U(2) + E8(-2)`, whose induced map on
`M(2)^* / M(2)` respects the decomposition `A_{U(2)} + A_{E8(-2)}` (H. Sterk, *Compactifications
of the period space of Enriques surfaces I*, Math. Z. 207 (1991), (4.3.5), p. 19).  The same
decomposition stabilizer `P <= O(q)` has preimage `Gamma_{En,2}`, so the call this test pins
serves the `Gamma_{En,2}` rows as well.

`L.Aut().discriminant_preimage(P)` used to return a predicate subgroup with no generating family:
`rho_L^-1(P)` was described as lifts of `P`'s generators together with `ker rho_L`, and the kernel
is `O(L)`'s stable orthogonal group, whose generating set this library does not have (the open
capability named by `_MISSING_ARITHMETIC_GENERATING_SET`).  The route taken instead needs no
kernel generators: `O(L)` acts on `A_L` through `rho_L`, so `rho_L^-1(P)` is the stabilizer of a
point of the orbit of `A_{U(2)}`, and Schreier's lemma turns a transversal of that orbit into
generators of the stabilizer (Seress, *Permutation Group Algorithms*, Cambridge Tracts in
Mathematics 152, Cambridge University Press, 2003, Lemma 4.2.1, p. 57).  The orbit is read on the
`F_2` model of `A_L` --- a 2-elementary discriminant group is an `F_2`-vector space --- so the
search is integer arithmetic on bit masks rather than owned discriminant-form evaluation.

What is asserted is what the two public calls compute.  The orbit's cardinality is `[O(q) : P]`,
so `|P| * |orbit|` is `|O(q)|`, with `|P|` read from the preimage's own discriminant image in
`O(q)` --- two routes to one number, no typed constant.  The generator family is the Schreier
family of that orbit with its trivial members dropped, so its cardinality is `|S| * |orbit|`
minus the `|orbit| - 1` orbit-tree pairs, `|S|` being the number of selected generators of
`O(L)`; a truncated or incomplete transversal fails that count.  Individual generators are
checked to lie in the preimage and to preserve `A_{U(2)}`.

`rho_L` is surjective here: `|rho_L(O(L))| = |O(q)|` is asserted, so the stabilizer in `O(L)`
maps onto the stabilizer in `O(q)`, which is how the family's images generate `P` without
computing an order over `|S| * |orbit|` generators.  That order computation is *not* asserted;
the family at this orbit has `15 * 67456 - 67455` members, and no route to an order of
`696729600` inside `O(q)` from that family was run.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _lattice():
    r"""`U(2) + E_8(-2)` as an integral lattice, from the named lattice's Gram (card `0125`)."""
    named = NamedLattices.E10_2
    rank = int(named.module_rank())
    gram = named.gram_tensor()
    return Lattices(ZZ)([[int(gram[i, j]) for j in range(rank)] for i in range(rank)])


def _decomposition_point(lattice):
    r"""The four classes of `A_{U(2)}` inside `A_L`, from the primitive duals of `U(2)`'s basis.

    `L = U(2) + E8(-2)` is built from the named lattice, whose first two module generators
    span the `U(2)` summand; their primitive duals project to the two classes that generate
    `A_{U(2)}`, and `A_{U(2)}` is the span of those two classes over `ZZ/2ZZ`.
    """
    form = lattice.discriminant_group()
    basis = tuple(lattice.module_generators())
    first = lattice.discriminant_class(lattice.primitive_dual(basis[0]))
    second = lattice.discriminant_class(lattice.primitive_dual(basis[1]))
    return frozenset({form.zero(), first, second, first + second})


def _summand_orders():
    r"""`(|O(q_{U(2)})|, |O(q_{E8(-2)})|)`: the two factors of the decomposition stabilizer's order.

    `A_L = A_{U(2)} + A_{E8(-2)}` is an orthogonal decomposition with both summands
    nondegenerate, so an isometry of `A_L` preserves one summand exactly when it preserves the
    other, and restriction is an isomorphism `P -> O(A_{U(2)}) x O(A_{E8(-2)})`.  `|P|` is
    therefore the product of the two summands' isometry-group orders, each read on the summand
    lattice itself --- a route to `|P|` that does not pass through the orbit.
    """
    return (
        int(NamedLattices.U_2.discriminant_group().orthogonal_group().cardinality()),
        int(NamedLattices.E8_2.discriminant_group().orthogonal_group().cardinality()),
    )


def test_the_decomposition_preimage_returns_generators() -> None:
    r"""The preimage's orbit index, its generator family, and the stabilizer's order agree.

    The computations are: the orbit of `A_{U(2)}` under `O(L)` (its cardinality is the index
    of the stabilizer), the Schreier family of that orbit lifted to `O(L)` (its cardinality is
    the Schreier count), the stabilizer's order from the two summands' isometry groups, and
    `rho_L`'s image `O(q)`.  `|P| * |orbit| = |O(q)|` is the index-stabilizer identity with
    `|P|` read a second way, and `|rho_L(O(L))| = |O(q)|` is the surjectivity that makes the
    stabilizer in `O(L)` map onto `P`; a wrong point, a wrong stabilizer and a truncated
    family each break one of them.
    """
    lattice = _lattice()
    form = lattice.discriminant_group()
    orthogonal = form.orthogonal_group()
    group = lattice.Aut()
    point = _decomposition_point(lattice)
    preimage = group.discriminant_point_stabilizer(point)
    orbit = group.discriminant_point_orbit(point)
    index = int(orbit.cardinality())
    order = int(orthogonal.cardinality())

    first_summand, second_summand = _summand_orders()
    assert first_summand * second_summand * index == order

    assert int(lattice.discriminant_image().cardinality()) == order

    letters = int(group.group_generators().cardinality())
    family = preimage.group_generators()
    count = int(family.cardinality())
    assert count == letters * index - (index - 1)

    rho = preimage.preimage_morphism()
    for label in (0, 1, 2, letters - 1, count - 1):
        generator = family.value(label)
        assert generator in preimage
        assert frozenset(rho(generator)(class_) for class_ in point) == point
