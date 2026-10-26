"""General algebra nouns used by active preamble signatures."""

from typing import Any

from sage.rings.ring import Ring
from sage.structure.element import Element, Matrix, ModuleElement, RingElement

BaseRing = Ring

# An algebra homomorphism in an owned algebra Mor.  The concrete morphism class
# is selected by the source algebra's retained presentation/framing data.
type AlgebraHomomorphism = Any

# An object of the owned category of monoids.  The active grading surface admits
# both multiplicative and additive monoids, whose generated ObjectType classes
# are selected from the runtime grading datum.
type MonoidObject = Any

__all__ = [
    "AlgebraHomomorphism",
    "BaseRing",
    "Element",
    "Matrix",
    "ModuleElement",
    "MonoidObject",
    "RingElement",
]
