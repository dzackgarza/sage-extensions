"""Finite coordinate presentations built from owned indexed families."""

from collections.abc import Callable, Iterable
from itertools import islice

from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent

from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.lexicon.category_theory import ElementOfCategoryObject


def _finite_framing(module: Parent) -> Sets().ObjectType:
    r"""Return a selected module framing after asserting that it is finite."""

    labels = module.module_generating_set()
    if not cardinal(labels.cardinality()).is_finite():
        raise TypeError(
            f"coordinates on {module} need a finite generating set, but its module generating set "
            f"{labels} is infinite"
        )
    return labels


def _coordinate_index_set(
    left_labels: Parent,
    right_labels: Parent,
) -> Sets().ObjectType:
    r"""Return the dependent two-factor index set for a rectangular family."""

    return Sets().product(indexed_family(Sets.Δ[1], lambda index: left_labels if int(index) == 0 else right_labels))


def _coerce_family_value[CoordinateValueInputT](
    value_module: Parent,
    value: CoordinateValueInputT,
) -> ElementOfCategoryObject:
    r"""``value`` as an element of ``value_module``: itself when that is its parent, its conversion otherwise."""
    return value if element_parent(value) is value_module else value_module(value)


def _coordinate_family_from_family(
    left_labels: Parent,
    right_labels: Parent,
    value_module: Parent,
    datum: IndexedFamily,
    *,
    name: str,
) -> IndexedFamily:
    r"""Transport a family indexed by pairs of labels to ``left × right``, coercing its values."""
    indices = _coordinate_index_set(left_labels, right_labels)
    source_indices = datum.index_set()

    def transported(pair: Element) -> ElementOfCategoryObject:
        source_pair = source_indices(lambda index: pair.component(index))
        return _coerce_family_value(value_module, datum[source_pair])

    return indexed_family(indices, transported, name=name)


def _coordinate_rows[CoordinateValueInputT](
    left_labels: Parent,
    right_labels: Parent,
    value_module: Parent,
    rows: Iterable[Iterable[CoordinateValueInputT]],
    *,
    name: str,
) -> tuple[tuple[ElementOfCategoryObject, ...], ...]:
    r"""Read finite rectangular rows, in the order of the two framings, into ``value_module``.

    Literal ingress: the rows are read once and their entries converted into
    ``value_module``.  Read at most one excess row or entry, so a malformed
    infinite iterator is rejected too.
    """
    left_size = int(left_labels.cardinality())
    right_size = int(right_labels.cardinality())
    entries = tuple(
        tuple(_coerce_family_value(value_module, entry) for entry in islice(row, right_size + 1))
        for row in islice(rows, left_size + 1)
    )
    if len(entries) != left_size or any(len(row) != right_size for row in entries):
        raise ValueError(
            f"the coordinate array for {name} must have {left_size} rows of {right_size} entries each, but "
            f"the rows given have lengths {tuple(len(row) for row in entries)}"
        )
    return entries


def _coordinate_family_from_rows[CoordinateValueInputT](
    left_labels: Parent,
    right_labels: Parent,
    value_module: Parent,
    rows: Iterable[Iterable[CoordinateValueInputT]],
    *,
    name: str,
) -> IndexedFamily:
    r"""Parse finite rectangular rows as a family indexed by ``left × right``."""
    indices = _coordinate_index_set(left_labels, right_labels)
    entries = _coordinate_rows(left_labels, right_labels, value_module, rows, name=name)

    return indexed_family(
        indices,
        lambda pair: entries[
            int(left_labels.ranking_map()(pair.component(0)))
        ][int(right_labels.ranking_map()(pair.component(1)))],
        name=name,
    )


def _coordinate_family[CoordinateValueInputT](
    left_labels: Parent,
    right_labels: Parent,
    value_module: Parent,
    datum: IndexedFamily | Iterable[Iterable[CoordinateValueInputT]],
    *,
    name: str,
) -> IndexedFamily:
    r"""Parse finite coordinate data, a family over pairs of labels or rows, as a family over ``left × right``.

    Declared representation ingress (``OWN-06``) for the quadratic-lift
    element constructor: an already-indexed family and literal rows are two
    representations of the same finite coordinate datum.  The family engine
    is owned by ``Objects()`` rather than by a fabricated family category, so
    this is representation dispatch rather than categorical membership.

    The shared literal ingress of the quadratic-lift element constructor in
    ``modules/powers.py``, which admits either presentation in one branch; it
    reads which presentation ``datum`` is and hands it to the parser for it.
    """
    match datum:
        case _ if isinstance(datum, IndexedFamily):
            return _coordinate_family_from_family(
                left_labels, right_labels, value_module, datum, name=name
            )
        case _:
            return _coordinate_family_from_rows(
                left_labels, right_labels, value_module, datum, name=name
            )


def _coordinate_pair[LeftLabelT, RightLabelT](
    values: IndexedFamily,
    left_label: LeftLabelT,
    right_label: RightLabelT,
) -> ElementOfCategoryObject:
    indices = values.index_set()
    return values[
        indices(lambda index: left_label if int(index) == 0 else right_label)
    ]


def _coordinate_family_from_function[LeftLabelT, RightLabelT, CoordinateValueInputT](
    left_labels: Parent,
    right_labels: Parent,
    value_module: Parent,
    function: Callable[[LeftLabelT, RightLabelT], CoordinateValueInputT],
    *,
    name: str,
) -> IndexedFamily:
    indices = _coordinate_index_set(left_labels, right_labels)
    return indexed_family(
        indices,
        lambda pair: _coerce_family_value(
            value_module,
            function(pair.component(0), pair.component(1)),
        ),
        name=name,
    )
