"""Mathematical nouns for category-theoretic dependent types."""

from typing import Any


# An object of a mathematically specified category C.  The category is often a
# runtime parameter (for example the codomain D of a functor F : C -> D), so
# Python cannot currently express the dependent type C.ObjectType here.
type ObjectOfCategory = Any

# An element of an object of a mathematically specified category when that
# element type is itself determined only after the runtime category/object is
# known.  This is the dependent referent of a category packet's ElementType.
type ElementOfCategoryObject = Any


__all__ = ["ElementOfCategoryObject", "ObjectOfCategory"]
