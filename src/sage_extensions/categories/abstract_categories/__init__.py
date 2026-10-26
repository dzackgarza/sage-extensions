r"""Lazy public aggregation for the owned abstract-category vocabulary.

The defining modules must remain independently importable.  Python executes a
package ``__init__`` before any submodule, so eager re-exports here create
artificial defining-module cycles.  Public names are resolved lazily instead.
"""

from importlib import import_module as _import_module

_EXPORTS = {
    "FunctorImageForgetfulFunctor": ("sage_extensions.categories.abstract_categories.functor_images", "FunctorImageForgetfulFunctor"),
    "FunctorImageMorphism": ("sage_extensions.categories.abstract_categories.functor_images", "FunctorImageMorphism"),
    "ImageOfFunctor": ("sage_extensions.categories.abstract_categories.functor_images", "ImageOfFunctor"),
    "DirectSumObjects": ("sage_extensions.categories.abstract_categories.direct_sum_objects", "DirectSumObjects"),
    "DirectedSystem": ("sage_extensions.categories.abstract_categories.products", "DirectedSystem"),
    "FiniteOrdinalCategory": ("sage_extensions.categories.abstract_categories.products", "FiniteOrdinalCategory"),
    "FiniteSequenceDiagram": ("sage_extensions.categories.abstract_categories.products", "FiniteSequenceDiagram"),
    "InverseSystem": ("sage_extensions.categories.abstract_categories.products", "InverseSystem"),
    "ParallelFamilyCategory": ("sage_extensions.categories.abstract_categories.products", "ParallelFamilyCategory"),
    "ParallelFamilyDiagram": ("sage_extensions.categories.abstract_categories.products", "ParallelFamilyDiagram"),
    "ParallelPairCategory": ("sage_extensions.categories.abstract_categories.products", "ParallelPairCategory"),
    "ParallelPairDiagram": ("sage_extensions.categories.abstract_categories.products", "ParallelPairDiagram"),
    "PosetCategory": ("sage_extensions.categories.abstract_categories.products", "PosetCategory"),
    "RestrictedDiagram": ("sage_extensions.categories.abstract_categories.products", "RestrictedDiagram"),
    "SelectedColimitConstruction": ("sage_extensions.categories.abstract_categories.products", "SelectedColimitConstruction"),
    "SelectedLimitConstruction": ("sage_extensions.categories.abstract_categories.products", "SelectedLimitConstruction"),
    "Cat": ("sage_extensions.categories.abstract_categories.cat", "Cat"),
    "NaturalTransformationMorphism": ("sage_extensions.categories.abstract_categories.cat", "NaturalTransformationMorphism"),
    "CategoricalMor": ("sage_extensions.categories.abstract_categories.mor_categories", "CategoricalMor"),
    "CategoryPacketMethods": ("sage_extensions.categories.abstract_categories.mor_categories", "CategoryPacketMethods"),
    "MorCategories": ("sage_extensions.categories.abstract_categories.mor_categories", "MorCategories"),
    "OppositeMorphism": ("sage_extensions.categories.abstract_categories.category_constructions", "OppositeMorphism"),
    "ProductMorphism": ("sage_extensions.categories.abstract_categories.category_constructions", "ProductMorphism"),
    "CategoricalIsomorphism": ("sage_extensions.categories.abstract_categories.mor_categories", "CategoricalIsomorphism"),
    "CommutativeSquare": ("sage_extensions.categories.abstract_categories.arrow_categories", "CommutativeSquare"),
    "SubobjectMor": ("sage_extensions.categories.abstract_categories.arrow_categories", "SubobjectMor"),
    "SubobjectMorphism": ("sage_extensions.categories.abstract_categories.arrow_categories", "SubobjectMorphism"),
    "Coverage": ("sage_extensions.categories.abstract_categories.presheaves", "Coverage"),
    "CoveringFamilies": ("sage_extensions.categories.abstract_categories.presheaves", "CoveringFamilies"),
    "DescentData": ("sage_extensions.categories.abstract_categories.presheaves", "DescentData"),
    "DescentDataOnCover": ("sage_extensions.categories.abstract_categories.presheaves", "DescentDataOnCover"),
    "DescentEqualizer": ("sage_extensions.categories.abstract_categories.presheaves", "DescentEqualizer"),
    "DescentEqualizerComparison": ("sage_extensions.categories.abstract_categories.presheaves", "DescentEqualizerComparison"),
    "OpenCoveringFamilies": ("sage_extensions.categories.abstract_categories.presheaves", "OpenCoveringFamilies"),
    "Sheaves": ("sage_extensions.categories.abstract_categories.presheaves", "Sheaves"),
    "TrivialCoveringFamilies": ("sage_extensions.categories.abstract_categories.presheaves", "TrivialCoveringFamilies"),
    "trivial_coverage": ("sage_extensions.categories.abstract_categories.presheaves", "trivial_coverage"),
    "ResolutionMorphism": ("sage_extensions.categories.abstract_categories.resolutions", "ResolutionMorphism"),
    "Resolutions": ("sage_extensions.categories.abstract_categories.resolutions", "Resolutions"),
}

__all__ = [
    "FunctorImageForgetfulFunctor",
    "FunctorImageMorphism",
    "ImageOfFunctor",
    "DirectSumObjects",
    "DirectedSystem",
    "FiniteOrdinalCategory",
    "FiniteSequenceDiagram",
    "InverseSystem",
    "ParallelFamilyCategory",
    "ParallelFamilyDiagram",
    "ParallelPairCategory",
    "ParallelPairDiagram",
    "PosetCategory",
    "RestrictedDiagram",
    "SelectedColimitConstruction",
    "SelectedLimitConstruction",
    "Cat",
    "NaturalTransformationMorphism",
    "CategoricalMor",
    "CategoryPacketMethods",
    "MorCategories",
    "OppositeMorphism",
    "ProductMorphism",
    "CategoricalIsomorphism",
    "CommutativeSquare",
    "SubobjectMor",
    "SubobjectMorphism",
    "Coverage",
    "CoveringFamilies",
    "DescentData",
    "DescentDataOnCover",
    "DescentEqualizer",
    "DescentEqualizerComparison",
    "OpenCoveringFamilies",
    "Sheaves",
    "TrivialCoveringFamilies",
    "trivial_coverage",
    "ResolutionMorphism",
    "Resolutions",
]


def __getattr__(name):
    # Python's module attribute protocol: a name this package does not
    # export is an AttributeError.
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    value = getattr(_import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__():
    return sorted((*globals(), *__all__))
