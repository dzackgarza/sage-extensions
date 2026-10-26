r"""Set and cardinal constructions a mathematician expects.

Finite and infinite sets, their products, coproducts, power sets, function
sets and subsets, the Hom sets between them, and the cardinal arithmetic
those constructions realize.
"""


from sage_extensions.all import *  # noqa: F401,F403


def _three():
    return Set((1, 2, 3))


def _two():
    return Sets.Δ[1]


def test_a_finite_set_and_its_constructions() -> None:
    three = _three()
    two = _two()

    assert three in Sets()
    assert three in FiniteSets()
    assert three in CountableSets()
    assert three.cardinality() == cardinal(3)
    assert two.cardinality() == cardinal(2)
    assert 2 in three
    assert 4 not in three
    assert three.power_set().cardinality() == cardinal(8)
    assert three.product_with(two).cardinality() == cardinal(6)
    assert Sets().product((three, two, three)).cardinality() == cardinal(18)
    assert Sets().coproduct((three, two)).cardinality() == cardinal(5)
    assert three.subsets_of_size(2).cardinality() == cardinal(3)
    assert three.finite_subsets().cardinality() == cardinal(8)


def test_function_sets_between_finite_sets() -> None:
    three = _three()
    two = _two()
    functions = Sets().Mor(two, three)
    assert three.exponential(two) is functions
    assert functions in Sets()
    assert functions in Sets().Mors()
    assert functions in FunctionSets()
    assert functions in FinitelySupportedFunctionSets()
    assert functions.base() is three
    assert functions.exponent() is two
    assert functions.mor() is functions
    assert functions.cardinality() == cardinal(9)
    assert Sets().Mor(three, two).cardinality() == cardinal(8)
    assert Sets().Mono(two, three).cardinality() == cardinal(6)
    assert Sets().Mono(three, two).cardinality() == cardinal(0)
    assert Sets().Iso(three, three).cardinality() == cardinal(6)
    assert Sets().Mor(three, Sets.Δ[0]).cardinality() == cardinal(1)


def test_subsets_by_condition_and_by_image() -> None:
    three = _three()
    large = three.condition_set(lambda n: n > 1)
    squares = three.image_set(lambda n: n * n)

    assert large.cardinality() == cardinal(2)
    assert 3 in large
    assert 1 not in large
    assert squares.cardinality() == cardinal(3)
    assert 4 in squares
    assert 2 not in squares
    assert large.inclusion().codomain() is three


def test_infinite_sets_and_their_constructions() -> None:
    assert NN.cardinality() == aleph0
    assert NN in CountablyInfiniteSets()
    assert NN in CountableSets()
    assert NN not in FiniteSets()
    assert ZZ.cardinality() == aleph0
    assert ZZ in CountablyInfiniteSets()
    assert QQ.cardinality() == aleph0
    assert RR.cardinality() == continuum
    assert RR in UncountableSets()
    assert NN.power_set().cardinality() == continuum
    assert NN.finite_subsets().cardinality() == aleph0
    assert Sets().product((NN, NN)).cardinality() == aleph0
    assert Sets().coproduct((NN, _three())).cardinality() == aleph0
    assert NN.subsets_of_size(2).cardinality() == aleph0
    assert NN.exponential(_two()).cardinality() == aleph0
    binary_sequences = _two().exponential(NN)
    assert binary_sequences is Sets().Mor(NN, _two())
    assert binary_sequences in FunctionSets()
    assert binary_sequences not in FinitelySupportedFunctionSets()
    assert binary_sequences.cardinality() == continuum
    assert Sets().Mor(NN, NN).cardinality() == continuum
    assert NN.condition_set(lambda n: n % 2 == 0).cardinality() == aleph0
    assert Sets.Δ[aleph0] is NN


def test_cardinal_arithmetic() -> None:
    cardinals = Cardinalities()
    assert cardinal(3) + cardinal(4) == cardinal(7)
    assert cardinal(3) * cardinal(4) == cardinal(12)
    assert cardinal(2) ** cardinal(3) == cardinal(8)
    assert cardinal(2) ** aleph0 == continuum
    assert cardinals.le(cardinal(3), aleph0)
    assert cardinal(5).is_finite()
    assert cardinal(5).finite_value() == 5
    assert cardinals.sum(cardinal(1), cardinal(2), cardinal(3)) == cardinal(6)
    assert cardinals.product(cardinal(2), cardinal(3), aleph0) == aleph0
    assert aleph0 + cardinal(1) == aleph0
    assert aleph0 * aleph0 == aleph0
    assert aleph0 ** 2 == aleph0
    assert 2 ** aleph0 == continuum
    assert continuum * continuum == continuum
    assert continuum ** aleph0 == continuum
    assert cardinals.lt(aleph0, continuum)
    assert not cardinals.le(continuum, aleph0)
    assert aleph0.is_countable()
    assert continuum.is_uncountable()
    assert aleph(1).is_uncountable()


def test_ordinal_arithmetic_is_not_commutative() -> None:
    first = omega(0)
    assert ordinal(1).ordinal_sum(first) == first
    assert first.ordinal_sum(1) != first
    assert Ordinals()(2).ordinal_sum(Ordinals()(3)) == Ordinals()(5)
    assert first.cardinality() == aleph0
    assert omega(1).cardinality() == aleph(1)


def test_finite_ordinals_are_totally_ordered() -> None:
    four = Sets.Δ[3]
    assert four.cardinality() == cardinal(4)
    assert four in TotallyOrderedSets()
    assert four[0] == four(0)
    assert four.ranking_map()(four(2)) == NN(2)
    assert four.le(four(1), four(3))
    assert not four.le(four(3), four(1))


def test_sets_of_sets() -> None:
    three = _three()
    power = three.power_set()
    element = power(Set((1, 2)))
    assert element in power
    assert element.cardinality() == cardinal(2)
    assert element.complement().cardinality() == cardinal(1)
    assert element.union(element.complement()).cardinality() == cardinal(3)
    assert element.intersection(element.complement()).cardinality() == cardinal(0)
    assert power(three).cardinality() == cardinal(3)
    assert power.top().cardinality() == cardinal(3)
    assert power.bottom().cardinality() == cardinal(0)


def test_a_set_of_rings_and_a_set_of_lattices_are_sets() -> None:
    rings = Set((ZZ, QQ, GF(5)))
    lattices = Set((Lattices(ZZ)("U"), Lattices(ZZ)("A2")))
    assert rings.cardinality() == cardinal(3)
    assert QQ in rings
    assert lattices.cardinality() == cardinal(2)
    assert Lattices(ZZ)("U") in lattices
    assert rings.product_with(lattices).cardinality() == cardinal(6)
