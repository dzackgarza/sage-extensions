"""The central typing layer: one name for each type that is known but not yet statically expressible (`LEX-15`)."""

from typing import Any

# A point $(n_1, \ldots, n_k)$ of the product monoid $\mathbb N^k$: an element
# of `Sets().product` of the constant family $\mathbb N$ over a finite index
# set.  The parent is built at runtime, so the referent has no static name yet
# and this aliases `Any` under `LEX-15`.  It checks nothing and is not intended
# to; it names the codomain so a reader can audit a signature against the
# operation's definition, and it is the single point at which a sharper
# refinement will later apply to every consumer at once (`LEX-17`, `LEX-18`).
ProductOfNaturalNumbers = Any

# A value that IPython hands to a display formatter registered for every type
# with `formatter.for_type(object, ...)`: the result of any notebook cell, so
# genuinely any Python value.  The formatter's job is to decide about it, which
# is why it aliases `Any` under `LEX-15`.
DisplayedValue = Any

__all__ = ["DisplayedValue", "ProductOfNaturalNumbers"]
