"""Mathematical nouns for dependent set-theoretic types."""

from typing import Any


# An object of the mathematical category Set.  Foundational category modules
# cannot import the concrete Sets() owner without creating an import cycle.
type SetObject = Any


__all__ = ["SetObject"]
