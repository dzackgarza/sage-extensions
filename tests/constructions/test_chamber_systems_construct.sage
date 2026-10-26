r"""Finite chamber systems as sets with typed equivalence relations.

A chamber system over a type set ``I`` has one equivalence relation on its
chambers for every ``i in I``.  Morphisms preserve the type set and every one
of those relations.  The three-chamber specimen below has ``s``-classes
``{0,1},{2}`` and ``t``-classes ``{0},{1,2}``, so the two adjacencies are
genuinely different rather than a duplicated universal relation.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _three_chambers():
    return ChamberSystems().from_adjacencies(
        (0, 1, 2),
        ("s", "t"),
        {
            "s": ((0, 0), (1, 1), (2, 2), (0, 1), (1, 0)),
            "t": ((0, 0), (1, 1), (2, 2), (1, 2), (2, 1)),
        },
    )


def _one_chamber():
    return ChamberSystems().from_adjacencies(
        ("*",),
        ("s", "t"),
        {"s": (("*", "*"),), "t": (("*", "*"),)},
    )


def test_chamber_system_retains_chambers_types_and_each_typed_adjacency() -> None:
    system = _three_chambers()

    assert system in ChamberSystems()
    assert system in Sets()
    assert system.cardinality() == cardinal(3)
    assert system.chambers().cardinality() == cardinal(3)
    assert system.type_set().cardinality() == cardinal(2)
    assert system.is_adjacent(system(0), "s", system(1))
    assert not system.is_adjacent(system(0), "s", system(2))
    assert system.is_adjacent(system(1), "t", system(2))
    assert not system.is_adjacent(system(0), "t", system(1))


def test_chamber_system_inherits_the_set_constructions_on_its_chamber_set() -> None:
    system = _three_chambers()
    two = Sets.Δ[1]
    point = Sets.Δ[0]

    assert system.counting_well_order().cardinality() == cardinal(3)
    assert system.condition_set(lambda chamber: chamber != system(2)).cardinality() == cardinal(2)
    assert system.power_set().cardinality() == cardinal(8)
    assert system.exponential(point).cardinality() == cardinal(3)
    assert system.product_with(two).cardinality() == cardinal(6)
    assert system.coproduct_with(two).cardinality() == cardinal(5)
    assert system.subsets_of_size(2).cardinality() == cardinal(3)
    assert system.finite_subsets().cardinality() == cardinal(8)
    assert system.finite_words().cardinality() == aleph0
    assert system.finite_multisets().cardinality() == aleph0


def test_chamber_system_image_set_is_the_image_of_an_explicit_underlying_set_map() -> None:
    source = _three_chambers()
    target = _one_chamber()
    underlying = source.Mor(target, category=Sets())(lambda _chamber: target("*"))
    image = source.image_set(underlying)

    assert underlying in Sets().Mor(source, target)
    assert image.cardinality() == cardinal(1)
    assert target("*") in image


def test_chamber_system_endpoint_mor_preserves_structure_unless_sets_are_requested() -> None:
    source = _three_chambers()
    target = _one_chamber()
    structured_mor = source.Mor(target)
    coarse_mor = source.Mor(target, category=Sets())
    collapse = structured_mor(lambda _chamber: target("*"))

    assert structured_mor is ChamberSystems().Mor(source, target)
    assert coarse_mor is Sets().Mor(source, target)
    assert collapse.underlying_set_morphism().domain() is source
    assert collapse.underlying_set_morphism().codomain() is target
    assert collapse(source(2)) == target("*")


def test_chamber_system_morphisms_have_identity_and_composition() -> None:
    source = _three_chambers()
    target = _one_chamber()
    collapse = source.Mor(target)(lambda _chamber: target("*"))
    source_identity = source.Mor(source).identity()
    target_identity = target.Mor(target).identity()

    assert source_identity(source(1)) == source(1)
    assert target_identity * collapse == collapse
    assert collapse * source_identity == collapse
