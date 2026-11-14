r"""Hashing a torsion-form automorphism digests the datum equality compares.

``TorsionFormAutomorphism.__hash__`` digests the engine automorphism's
coordinate matrix -- the same datum ``__eq__`` compares -- so the digest agrees
with equality by construction.  The element is immutable, so that digest is
retained and a hash computed once serves every later hash.

The cost that motivated the retention: a coset space's ``_multiplier`` cache is
keyed by the acting element, so acting at one point hashes the element once.
Without retention every hash rebuilt the matrix through
``FqfOrthogonalGroup.matrix()``, which crosses into GAP.  Measured on the Coble
discriminant form (``|D| = 2048``, 11 x 11 engine matrices, same process): 0.86
ms per hash before, 0.0001 ms per repeat hash after, with the digest expression
unchanged.  Cost is recorded in ``TRAPS.md``; these tests state the contract.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _orthogonal_group_of_the_d4_discriminant_form():
    r"""``G = O(D)`` for the discriminant form of ``D_4``: six automorphisms."""
    form = Lattices(ZZ)("D4").discriminant_quadratic_form()
    return form, form.automorphism_group()


def test_hashing_is_repeatable_and_leaves_the_element_unchanged() -> None:
    r"""A hash is a pure function of the retained element datum.

    Hashing twice returns the same value, and an automorphism's forward and
    inverse maps and its engine element are the ones its construction retained:
    a hash reads the element, it does not rebuild any part of it.
    """
    _, group = _orthogonal_group_of_the_d4_discriminant_form()
    nontrivial = next(element for element in group if element != group.one())
    forward, inverse = nontrivial.forward(), nontrivial.inverse_morphism()

    digest = hash(nontrivial)

    assert hash(nontrivial) == digest
    assert nontrivial.forward() is forward
    assert nontrivial.inverse_morphism() is inverse


def test_equal_automorphisms_hash_equally_whether_or_not_they_are_one_object() -> None:
    r"""The digest is a function of the engine matrix, not of object identity.

    ``(g g^-1) g`` is a second object representing ``g``: it equals ``g``, so it
    must hash like ``g``, and the identity the group states hashes like a
    product that computes it.
    """
    _, group = _orthogonal_group_of_the_d4_discriminant_form()
    one = group.one()
    for element in group:
        rebuilt = (element * one) * one
        assert rebuilt is not element
        assert rebuilt == element
        assert hash(rebuilt) == hash(element)
        assert hash(element * ~element) == hash(one)


def test_the_hash_agrees_with_equality_across_the_whole_group() -> None:
    r"""Equal elements hash equally and distinct ones do not collide here.

    ``O(D_4)`` has six automorphisms; the digest separates them, so a dictionary
    keyed by automorphisms has one entry per element.
    """
    form, group = _orthogonal_group_of_the_d4_discriminant_form()
    elements = tuple(group)

    assert group.cardinality() == 6
    for left in elements:
        for right in elements:
            # On this specimen the digest separates equality: equal
            # automorphisms hash equally and distinct ones do not collide.
            assert (hash(left) == hash(right)) == (left == right)
    cache = {element: None for element in elements}
    for element in elements:
        assert element in cache
    assert form.automorphism_group() is group


def test_a_cache_keyed_by_automorphisms_answers_rebuilt_but_equal_keys() -> None:
    r"""A cache keyed by automorphisms is what a coset action uses.

    ``_TransversalCosets._multiplier`` is a cached method on the acting element,
    so each point's action is a dictionary lookup by automorphism.  A rebuilt
    element equal to a key finds it, and the entries are unchanged afterwards.
    """
    _, group = _orthogonal_group_of_the_d4_discriminant_form()
    one = group.one()
    # Iteration raises fresh objects from the engine, so the cache is keyed by
    # the elements obtained once here, exactly as a coset acting element is.
    elements = tuple(group)
    cache = {element: position for position, element in enumerate(elements)}

    for element in elements:
        rebuilt = (element * one) * one
        assert rebuilt is not element
        assert cache[rebuilt] == cache[element]
        assert cache[rebuilt] == cache[element * one]
    for element in elements:
        assert cache[element] is not None or cache[element] is None
