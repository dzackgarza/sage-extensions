r"""The discriminant action of a preimage generator is ``rho_L`` of it (#367).

On card `0125`, `L = U(2) + E8(-2)`, the family is the one
`L.Aut().discriminant_point_stabilizer(point)` returns: the Schreier family of
the orbit of the decomposition point `A_{U(2)}` inside `A_L`, whose images in
`O(A_L)` are the decomposition stabilizer `P` (sage-extensions#354).

What is asserted is `member.discriminant_morphism() == rho_L(member)` for members
sampled across the family, `rho_L` being the morphism the preimage call retains,
together with the three consequences of that law which a wrong image would break:
`Disc(g) * Disc(g^-1)` is the identity, `Disc(g^-1)` is `Disc(g)^-1`,
`Disc(g h) = Disc(g) Disc(h)`, and `Disc(g)` carries the decomposition point to
itself.  On this tree `rho_L` is *defined* as the accessor
(`lattice_morphisms.py`, `discriminant_representation` sends an isometry to
`isometry.discriminant_morphism()`), and the family's members are elements of
`O(L)`; the record `results/issue367-preimage-generator-discriminant-action.md`
states the measurement that the two are one object, and these four laws are the
part of the contract that can fail.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _lattice():
    r"""`U(2) + E_8(-2)` as an integral lattice, from the named lattice's Gram (card `0125`)."""
    named = NamedLattices.E10_2
    rank = int(named.module_rank())
    gram = named.gram_tensor()
    return Lattices(ZZ)([[int(gram[i, j]) for j in range(rank)] for i in range(rank)])


def _decomposition_point(lattice):
    r"""The four classes of `A_{U(2)}` inside `A_L`, from the primitive duals of `U(2)`'s basis."""
    form = lattice.discriminant_group()
    basis = tuple(lattice.module_generators())
    first = lattice.discriminant_class(lattice.primitive_dual(basis[0]))
    second = lattice.discriminant_class(lattice.primitive_dual(basis[1]))
    return frozenset({form.zero(), first, second, first + second})


def test_each_sampled_family_member_induces_the_map_rho_l_gives() -> None:
    r"""`discriminant_morphism()` of a family member is `rho_L` of it, with its consequences.

    The members sampled are the family's first, the last, and labels spread over
    its 944 385 positions; one product of two of them is checked as well.  The
    family, the point and `rho_L` all come from the public call.
    """
    lattice = _lattice()
    group = lattice.Aut()
    form = lattice.discriminant_group()
    orthogonal = form.orthogonal_group()
    point = _decomposition_point(lattice)

    preimage = group.discriminant_point_stabilizer(point)
    family = preimage.group_generators()
    count = int(family.cardinality())
    rho = preimage.preimage_morphism()
    letters = int(group.group_generators().cardinality())

    samples = (0, 1, 2, letters - 1, letters * 100, letters * 10_000, count - 1)
    identity_of_form = orthogonal.one()
    for label in samples:
        member = family.value(label)
        discriminant = member.discriminant_morphism()
        assert discriminant == rho(member)
        assert frozenset(discriminant(class_) for class_ in point) == point
        assert discriminant * (~member).discriminant_morphism() == identity_of_form
        assert (~member).discriminant_morphism() == ~discriminant

    first = family.value(0)
    last = family.value(count - 1)
    assert (first * last).discriminant_morphism() == (
        first.discriminant_morphism() * last.discriminant_morphism()
    )
