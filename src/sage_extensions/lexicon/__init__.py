"""Lazy public aggregation for mathematical nouns used by the preamble.

The lexicon's defining modules must remain independently importable. Python
executes a package ``__init__`` before any submodule, so eager re-exports here
pull category-owning modules into dependency-light type imports and create
artificial import cycles. Public names are resolved lazily instead.
"""

from importlib import import_module as _import_module


_EXPORTS = {
    "AlgebraHomomorphism": ("sage_extensions.lexicon.algebra", "AlgebraHomomorphism"),
    "BaseRing": ("sage_extensions.lexicon.algebra", "BaseRing"),
    "Element": ("sage_extensions.lexicon.algebra", "Element"),
    "Matrix": ("sage_extensions.lexicon.algebra", "Matrix"),
    "ModuleElement": ("sage_extensions.lexicon.algebra", "ModuleElement"),
    "MonoidObject": ("sage_extensions.lexicon.algebra", "MonoidObject"),
    "RingElement": ("sage_extensions.lexicon.algebra", "RingElement"),
    "ElementOfCategoryObject": (
        "sage_extensions.lexicon.category_theory",
        "ElementOfCategoryObject",
    ),
    "ObjectOfCategory": ("sage_extensions.lexicon.category_theory", "ObjectOfCategory"),
    "CartanType": ("sage_extensions.lexicon.foundations", "CartanType"),
    "GramMatrix": ("sage_extensions.lexicon.foundations", "GramMatrix"),
    "Integer": ("sage_extensions.lexicon.foundations", "Integer"),
    "LatticeName": ("sage_extensions.lexicon.foundations", "LatticeName"),
    "MatrixData": ("sage_extensions.lexicon.foundations", "MatrixData"),
    "OrderedSet": ("sage_extensions.lexicon.foundations", "OrderedSet"),
    "Rational": ("sage_extensions.lexicon.foundations", "Rational"),
    "SignaturePair": ("sage_extensions.lexicon.foundations", "SignaturePair"),
    "SymbolicExpression": ("sage_extensions.lexicon.foundations", "SymbolicExpression"),
    "Graph": ("sage_extensions.lexicon.geometry", "Graph"),
    "Polyhedron": ("sage_extensions.lexicon.geometry", "Polyhedron"),
    "SageCategory": ("sage_extensions.lexicon.interop", "SageCategory"),
    "SageElement": ("sage_extensions.lexicon.interop", "SageElement"),
    "SageMorphism": ("sage_extensions.lexicon.interop", "SageMorphism"),
    "SageParent": ("sage_extensions.lexicon.interop", "SageParent"),
    "SageUniqueRepresentation": (
        "sage_extensions.lexicon.interop",
        "SageUniqueRepresentation",
    ),
    "SetObject": ("sage_extensions.lexicon.set_theory", "SetObject"),
}

__all__ = [
    "AlgebraHomomorphism",
    "BaseRing",
    "CartanType",
    "Element",
    "ElementOfCategoryObject",
    "GramMatrix",
    "Graph",
    "Integer",
    "LatticeName",
    "Matrix",
    "MatrixData",
    "ModuleElement",
    "MonoidObject",
    "OrderedSet",
    "ObjectOfCategory",
    "Polyhedron",
    "Rational",
    "RingElement",
    "SageCategory",
    "SageElement",
    "SageMorphism",
    "SageParent",
    "SageUniqueRepresentation",
    "SetObject",
    "SignaturePair",
    "SymbolicExpression",
]


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module_name, attribute = _EXPORTS[name]
    value = getattr(_import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__():
    return sorted((*globals(), *__all__))
