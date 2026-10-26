r"""Every category in the session exhibits an object, over every ring it can be taken over.

A category is inhabited: it answers ``an_object()`` with something that is in
it.  A category over a base ring is inhabited over every ring in the
catalogue, not only over the integers: modules over a principal ideal domain
must exist over every named principal ideal domain, and a category that
answers only over $\mathbb Z$ has not stated what its parameter is.

The category list is read from the session itself: every name the star
import brings in that is a category class.  Nullary ones are built bare;
ones over a base ring are built over each ring in the catalogue.  Sage's
own categories that the session exports are held to the same expectation.
"""

import inspect

import pytest
from sage.categories.category import Category

from sage_extensions.all import *  # noqa: F401,F403


def _session_categories():
    r"""Every category class the session exports, split by how it is constructed."""
    nullary, over_ring = [], []
    for name, candidate in sorted(globals().items()):
        if not (inspect.isclass(candidate) and issubclass(candidate, Category)):
            continue
        # ``Category`` and ``OwnedCategoryOverBaseRing`` are abstract base
        # classes for declaring categories, not concrete mathematical
        # categories a session can instantiate and ask for a witness.
        if candidate in (Category, OwnedCategoryOverBaseRing):
            continue
        if issubclass(candidate, OwnedCategoryOverBaseRing):
            over_ring.append(name)
        elif _is_nullary(candidate):
            nullary.append(name)
    return nullary, over_ring


def _is_nullary(category_class) -> bool:
    parameters = [
        parameter
        for parameter in inspect.signature(category_class.__init__).parameters.values()
        if parameter.name != "self"
        and parameter.kind not in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD)
        and parameter.default is parameter.empty
    ]
    return not parameters


NULLARY, OVER_RING = _session_categories()


@pytest.mark.parametrize("name", NULLARY)
def test_a_nullary_category_is_inhabited(name) -> None:
    category = globals()[name]()
    witness = category.an_object()
    assert witness in category, f"{name}.an_object() is not in {name}"


@pytest.mark.parametrize("name", NULLARY)
def test_the_witness_of_a_nullary_category_has_elements(name) -> None:
    witness = globals()[name]().an_object()
    element = witness.an_element()
    facade_for = getattr(witness, "facade_for", lambda: None)()
    if facade_for is None:
        assert element.parent() is witness
    else:
        assert element.parent() in facade_for
    assert element in witness


@pytest.mark.parametrize("name", OVER_RING)
def test_a_category_over_a_ring_is_inhabited_over_every_ring(name, commutative_ring) -> None:
    category = globals()[name](commutative_ring)
    witness = category.an_object()
    assert witness in category, f"{name}({commutative_ring}).an_object() is not in it"
    assert witness.base_ring() is commutative_ring


@pytest.mark.parametrize("name", OVER_RING)
def test_the_witness_of_a_category_over_a_ring_has_elements(name, pid) -> None:
    witness = globals()[name](pid).an_object()
    element = witness.an_element()
    assert element.parent() is witness
    assert element in witness
    assert element + witness.zero() == element


@pytest.mark.parametrize("name", OVER_RING)
def test_a_category_over_a_ring_remembers_its_ring(name, field) -> None:
    category = globals()[name](field)
    assert category.base_ring() is field
    assert category is globals()[name](field)
