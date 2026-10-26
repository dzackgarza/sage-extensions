"""Finite indexed families on the canonical finite ordinal."""

from collections.abc import Iterable

from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets


def finite_family[ValueT](
    values: IndexedFamily | Iterable[ValueT],
    *,
    name: str | None = None,
) -> IndexedFamily:
    r"""Return the family over \(\Delta[k-1]\) taking the stated values in order.

    A finite sequence of owned values is a family, not a set: two of them may be
    equal, which a set would collapse, and each is addressed by its position.
    The ``IndexedFamily`` case is declared representation ingress (``OWN-06``):
    it preserves an already-owned family rather than reindexing it by positions.
    ``IndexedFamily`` itself is an engine object in ``Objects()``, not a category
    whose membership could honestly replace this representation distinction.
    """
    if isinstance(values, IndexedFamily):
        return values
    entries = tuple(values)
    positions = Sets.Δ[len(entries) - 1]
    return indexed_family(
        positions,
        lambda position: entries[int(position)],
        name=name,
    )


__all__ = ["finite_family"]
