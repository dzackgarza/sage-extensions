r"""The free product of two infinite finitely presented groups has its injections.

The coproduct in ``Grp`` of ``G_1`` and ``G_2`` is the free product
``G_1 * G_2`` (Mathlib ``Mathlib/GroupTheory/FreeProduct.lean``): the group
of reduced alternating words in the two factors, with factor inclusions
``i_j: G_j -> G_1 * G_2`` and, for every pair of homomorphisms
``f_j: G_j -> H``, the unique ``f`` with ``f i_j = f_j``.  The inclusions are
constituents of the construction, not decoration: a bare group object of the
right shape states no universal property and admits no cocone.

Specimens:

- ``Z * F(a, b)``, two infinite finitely presented groups.  The images
  ``i_1(1) = g_1`` and ``i_2(a) = g_2`` are nonidentity and their commutator
  is not trivial, so the coproduct is the free product and not the product
  of the two factors.
- The retraction ``r_1: Z * F(a,b) -> Z`` that is the identity on ``Z`` and
  trivial on ``F(a,b)`` is the universal map of the cocone
  ``(id_Z, trivial)``; ``r_1 i_1 = id_Z`` and ``r_1 i_2`` is the trivial map,
  and symmetrically for ``r_2``.  A one-sided inverse exhibits each injection
  as an injection.
- The cocone ``(1 |-> (12), a |-> (12), b |-> (123))`` into ``S_3`` factors
  through ``Z * F(a,b)``; the factor reproduces both supplied legs on the
  images of the injections, in particular on a mixed word.
- ``Z * <a, b | a^2 = b^3>``, where the second factor is infinite and not
  free; its finiteness is not decided by the engine, so it is asserted not
  placed finite (its abelianization is ``Z``).  The injections into the
  coproduct are still actual group morphisms with the stated endpoints.

The injection of a finitely presented *free* factor is where the construction
stopped: ``IndexedFreeGroupMor``, the owner of the maps out of a free group,
had no engine crossing while the canonical ``GroupMor`` had one, so building
the inclusion of ``Z`` into ``Z * F(a,b)`` raised ``AttributeError``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _integers_and_rank_two_free_group():
    r"""``Z`` and ``F(a,b)``, with their selected generators."""
    integers = Groups.Free(1)
    rank_two = Groups.Free(2)
    unit = integers.free_generator(next(iter(integers.free_basis())))
    a, b = rank_two.group_generators()[0], rank_two.group_generators()[1]
    return integers, rank_two, unit, a, b


def _free_product_of_integers_and_rank_two():
    r"""The selected coproduct ``Z * F(a,b)`` with its two injections."""
    integers, rank_two, unit, a, b = _integers_and_rank_two_free_group()
    construction = Groups().coproduct_construction((integers, rank_two))
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    return (
        construction,
        construction.object(),
        construction.costructure_morphism(first),
        construction.costructure_morphism(second),
        integers,
        rank_two,
        unit,
        a,
        b,
    )


def test_the_free_product_of_two_infinite_groups_has_its_injections() -> None:
    integers, rank_two, unit, a, b = _integers_and_rank_two_free_group()
    assert integers in Groups().Infinite() and integers in Groups().FinitelyPresentedAsGroup()
    assert rank_two in Groups().Infinite() and rank_two in Groups().FinitelyPresentedAsGroup()

    construction, coproduct, left, right, _, _, unit, a, b = (
        _free_product_of_integers_and_rank_two()
    )
    assert coproduct in Groups() and coproduct in Groups().FinitelyPresentedAsGroup()
    assert left.domain() is integers and left.codomain() is coproduct
    assert right.domain() is rank_two and right.codomain() is coproduct
    assert left(unit) != coproduct.one()
    assert right(a) != coproduct.one() and right(b) != coproduct.one()
    # The free product is not the direct product of the two factors.
    commutator = left(unit) * right(a) * ~left(unit) * ~right(a)
    assert commutator != coproduct.one()
    assert left(unit) * right(b) != right(b) * left(unit)


def test_each_free_product_injection_is_a_section_of_the_selected_retraction() -> None:
    construction, coproduct, left, right, integers, rank_two, unit, a, b = (
        _free_product_of_integers_and_rank_two()
    )
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    identity_integers = integers.Mor(integers).identity()
    identity_rank_two = rank_two.Mor(rank_two).identity()
    trivial_to_integers = rank_two.Mor(integers).elementwise(lambda _element: integers.one())
    trivial_to_rank_two = integers.Mor(rank_two).elementwise(lambda _element: rank_two.one())

    onto_integers = construction.factor(
        construction.diagram().Cocones().cocone(
            integers,
            lambda index: identity_integers if index == first else trivial_to_integers,
        )
    ).apex_map()
    onto_rank_two = construction.factor(
        construction.diagram().Cocones().cocone(
            rank_two,
            lambda index: trivial_to_rank_two if index == first else identity_rank_two,
        )
    ).apex_map()

    assert onto_integers.domain() is coproduct and onto_integers.codomain() is integers
    assert onto_rank_two.domain() is coproduct and onto_rank_two.codomain() is rank_two
    assert onto_integers * left == identity_integers
    assert onto_rank_two * right == identity_rank_two
    assert onto_integers(left(unit)) == unit
    assert onto_rank_two(right(a)) == a and onto_rank_two(right(b)) == b
    assert onto_integers(right(a)) == integers.one()
    assert onto_rank_two(left(unit)) == rank_two.one()


def test_the_free_product_cocone_factors_through_both_injections() -> None:
    construction, coproduct, left, right, _, _, unit, a, b = (
        _free_product_of_integers_and_rank_two()
    )
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    symmetric = Groups.S(3)
    three_cycle, transposition = symmetric.group_generators()[0], symmetric.group_generators()[1]
    source_left, source_right = left.domain(), right.domain()
    leg_left = source_left.Mor(symmetric)({next(iter(source_left.free_basis())): transposition})
    leg_right = source_right.Mor(symmetric)(
        {
            tuple(source_right.free_basis())[0]: transposition,
            tuple(source_right.free_basis())[1]: three_cycle,
        }
    )

    factor = construction.factor(
        construction.diagram().Cocones().cocone(
            symmetric, lambda index: leg_left if index == first else leg_right
        )
    ).apex_map()
    assert factor.domain() is coproduct and factor.codomain() is symmetric
    assert factor * left == leg_left
    assert factor * right == leg_right
    assert factor(coproduct.one()) == symmetric.one()
    assert factor(left(unit)) == transposition
    assert factor(right(a)) == transposition and factor(right(b)) == three_cycle

    mixed_word = left(unit) ** 2 * right(b) * ~left(unit)
    assert factor(mixed_word) == transposition**2 * three_cycle * ~transposition
    assert factor(mixed_word) == factor(left(unit)) ** 2 * factor(right(b)) * ~factor(left(unit))

    # The cocone of the two injections themselves factors as the identity:
    # the factor is characterized by its composites with the injections.
    identity_factor = construction.factor(
        construction.diagram().Cocones().cocone(
            coproduct, lambda index: left if index == first else right
        )
    ).apex_map()
    assert identity_factor * left == left
    assert identity_factor * right == right
    assert identity_factor(mixed_word) == mixed_word


def test_the_free_product_with_a_non_free_infinite_presented_factor_has_its_injections() -> None:
    integers, rank_two, unit, a, b = _integers_and_rank_two_free_group()
    # <a, b | a^2 = b^3>, the trefoil group: infinite, finitely presented, not free.
    presented = rank_two.quotient_by_relators((a**2 * ~(b**3),))
    assert presented in Groups().FinitelyPresentedAsGroup()
    assert presented not in Groups().Finite()
    assert presented not in Groups().Infinite()

    construction = Groups().coproduct_construction((integers, presented))
    coproduct = construction.object()
    shape = construction.diagram().domain()
    first, second = shape(0), shape(1)
    from_integers = construction.costructure_morphism(first)
    from_presented = construction.costructure_morphism(second)

    assert coproduct in Groups()
    assert from_integers.domain() is integers and from_integers.codomain() is coproduct
    assert from_presented.domain() is presented and from_presented.codomain() is coproduct
    assert from_integers(unit) != coproduct.one()
    assert from_presented(a) != coproduct.one()
    assert from_integers(unit) * from_presented(a) != from_presented(a) * from_integers(unit)
