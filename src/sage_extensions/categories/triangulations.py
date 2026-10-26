r"""Chosen triangulations over an exact geometric or complex target."""

from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.cell_complexes import SimplicialComplexes
from sage_extensions.categories.functors.core import Functor
from sage_extensions.owned_category_bases import CategoryWithAxiom


for _axiom in ("Integral", "Unimodular"):
    if _axiom not in all_axioms:
        all_axioms.add(_axiom)


class ChosenTriangulationMor(CategoricalMor):
    r"""Simplicial maps commuting with the two realization maps to the target."""

    class ElementMethods:
        def __init__(self, parent, simplicial_map):
            Morphism.__init__(self, parent)
            self._simplicial_map = simplicial_map

        def simplicial_map(self):
            return self._simplicial_map

        def __mul__(self, other):
            pass

    def _element_constructor_(self, simplicial_map):
        pass

    @object_level
    def identity(self):
        pass


class ChosenTriangulationMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = ChosenTriangulationMor


class _TriangulationSourceFunctor(Functor):
    r"""Forget the chosen map to the target, on objects and arrows."""

    def __init__(self, target):
        super().__init__(ChosenTriangulations(target), SimplicialComplexes())

    def _apply_object(self, triangulation):
        return triangulation.simplicial_complex()

    def _apply_morphism(self, morphism):
        return morphism.simplicial_map()


class ChosenTriangulations(OwnedParameterizedCategory):
    r"""Pairs ``(T, |T| -> K)`` over one exact represented target ``K``."""

    _MorCategory = ChosenTriangulationMorCategoryConstruction

    def parameter_category(self):
        return Objects()

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "chosen triangulations"

    def an_object(self):
        pass

    def on(self, simplicial_complex, realization_map, simplex_inclusions):
        r"""Select ``T``, its simplex inclusions, and ``|T| -> K``."""
        pass

    def _from_engine_triangulation(self, engine_triangulation, vertex_map):
        r"""Raise a private point-configuration triangulation over the exact target."""
        pass

    def target(self):
        return self.parameter()

    @cached_method
    def source(self):
        return _TriangulationSourceFunctor(self.target())

    class ParentMethods:
        def __init__(self, target, simplicial_complex, realization_map, simplex_inclusions, **rest):
            self._target = target
            self._simplicial_complex = simplicial_complex
            self._realization_map = realization_map
            self._simplex_inclusions = simplex_inclusions
            super().__init__(**rest)

        def target(self):
            return self._target

        def simplicial_complex(self):
            return self._simplicial_complex

        def realization_map(self):
            return self._realization_map

        def simplices(self, dimension):
            return self.simplicial_complex().simplices(dimension)

        def simplex_inclusion(self, simplex):
            return self._simplex_inclusions[simplex]

        def covers_target(self):
            pass

        def intersections_are_common_faces(self):
            pass

    class Integral(CategoryWithAxiom):
        r"""Chosen triangulations integral relative to the target's selected lattices."""

        class ParentMethods:
            def lattice_comparison(self):
                pass

            def simplex_vertices_are_integral(self, simplex):
                pass

    class Unimodular(CategoryWithAxiom):
        r"""Integral triangulations whose maximal simplices have normalized volume one."""

        def extra_super_categories(self):
            return [self.base_category().Integral()]

        class ParentMethods:
            def normalized_volume(self, simplex):
                pass
