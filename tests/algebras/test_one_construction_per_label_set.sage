r"""One datum, one object: the label set a free construction records.

A free module's framing records the *actual* label set it was constructed on,
and the free constructions over it are interned by that module's identity.  So
the identity of the whole tower rests on the identity of the label set, and two
separately built sets of the same ordered labels used to give two modules and
two algebras out of one datum:

    QQ.polynomial_ring(("x", "y"))  ==  Modules(QQ).free_module(("x", "y")).symmetric_algebra()
    False                                  (both sides printing identically)

`R[S]` is stated to be ``Sym_R(F_R(S))``, one object for ``(R, S)``, on every
route.  The owner of that identity is the set constructor: the polynomial route
already interned its variables by their ordered names, the free-module route
did not, so the two reached different label sets and `_owned_free_module_on`,
which keys on the identities of the ring and the set, built two modules.

These tests pin the identity, and pin where it stops: a family of unhashable
points keeps its own identity, and an ordinal card is not the explicit tuple of
its points, because those are different presented data and the selected basis
is the set object itself.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_polynomial_ring_is_the_symmetric_algebra_of_its_free_module() -> None:
    r"""``QQ[x, y]`` and ``Sym(QQ^2)`` are one object, not two.

    Every statement about the polynomial ring applies to the symmetric algebra
    and back, which is what ``R[S] = Sym_R(F_R(S))`` says.
    """
    polynomials = QQ.polynomial_ring(("x", "y"))
    symmetric = Modules(QQ).free_module(("x", "y")).symmetric_algebra()

    assert polynomials is symmetric
    assert polynomials == symmetric
    assert (
        polynomials.generating_module()
        is symmetric.generating_module()
    )
    assert (
        polynomials.generating_module().module_generating_set()
        is symmetric.generating_module().module_generating_set()
    )


def test_element_data_agrees_across_the_two_routes() -> None:
    r"""The elements are the same elements, not equal ones in two algebras.

    ``x * y`` built from the polynomial route is an element of the object the
    symmetric route returns, so it adds and multiplies with that route's
    generators without a coercion between two algebras.
    """
    polynomials = QQ.polynomial_ring(("x", "y"))
    symmetric = Modules(QQ).free_module(("x", "y")).symmetric_algebra()

    product = polynomials.algebra_generator("x") * polynomials.algebra_generator("y")
    assert product.parent() is symmetric
    assert product == symmetric.algebra_generator("x") * symmetric.algebra_generator("y")
    assert (product + symmetric.one()) in symmetric


def test_the_free_construction_on_ordered_labels_is_one_object_per_route() -> None:
    r"""Two calls with the same ordered labels are one module and one algebra.

    The same holds for every free construction over it, and the variable-name
    string names the same label set as the tuple.
    """
    free = Modules(QQ).free_module(("x", "y"))

    assert free is Modules(QQ).free_module(("x", "y"))
    assert free.tensor_algebra() is Modules(QQ).free_module(("x", "y")).tensor_algebra()
    assert free.exterior_algebra() is Modules(QQ).free_module(("x", "y")).exterior_algebra()
    assert free.symmetric_algebra() is Modules(QQ).free_module(("x", "y")).symmetric_algebra()
    assert QQ.polynomial_ring("x,y") is QQ.polynomial_ring(("x", "y"))


def test_label_data_that_is_not_the_same_data_keeps_its_own_identity() -> None:
    r"""Interning is by ordered labels, never by what a set happens to equal.

    A family of unhashable points cannot be interned by value, so two such
    families stay two modules.  An ordinal card ``2`` presents ``{0, 1}`` as an
    ordinal and the tuple ``(0, 1)`` presents it as named points: the selected
    basis is the set object, so these are two data and two modules, each of
    them stable across calls.
    """
    first = Modules(QQ).free_module([[1], [2]])
    second = Modules(QQ).free_module([[1], [2]])
    assert first is not second
    assert first.module_generating_set() == second.module_generating_set()

    ordinal = Modules(QQ).free_module(2)
    named = Modules(QQ).free_module((0, 1))
    assert ordinal is Modules(QQ).free_module(2)
    assert named is Modules(QQ).free_module((0, 1))
    assert ordinal is not named
    assert ordinal.module_generating_set() is not named.module_generating_set()
