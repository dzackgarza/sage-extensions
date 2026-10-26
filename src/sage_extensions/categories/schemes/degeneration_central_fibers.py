r"""Central fibres with selected component and intersection incidence data."""

from sage.misc.cachefunc import cached_method
from sage.categories.morphism import Morphism

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects
from sage_extensions.categories.cell_complexes import CellComplexes
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)
from sage_extensions.categories.schemes.schemes import Schemes


class DegenerationCentralFiberMor(CategoricalMor):
    r"""Scheme maps with a compatible map of selected intersection strata."""

    class ElementMethods:
        def __init__(self, parent, scheme_map, incidence_map):
            Morphism.__init__(self, parent)
            self._scheme_map = scheme_map
            self._incidence_map = incidence_map

        def underlying_scheme_morphism(self):
            return self._scheme_map

        def incidence_map(self):
            return self._incidence_map

        def dual_complex_map(self):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, scheme_map, incidence_map):
        pass

    @object_level
    def identity(self):
        pass


class DegenerationCentralFiberMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = DegenerationCentralFiberMor


class _UnderlyingCentralFiberFunctor(Functor):
    r"""Forget selected incidence data on central fibres and their maps."""

    def __init__(self, source):
        super().__init__(source, Schemes(source.base_ring()))

    def _apply_object(self, central_fiber):
        return central_fiber.underlying_scheme()

    def _apply_morphism(self, morphism):
        return morphism.underlying_scheme_morphism()


class _DualComplexFunctor(Functor):
    r"""Send selected intersection strata and their maps to cell complexes."""

    def __init__(self, source):
        super().__init__(source, CellComplexes())

    def _apply_object(self, central_fiber):
        return central_fiber.dual_complex()

    def _apply_morphism(self, morphism):
        return morphism.dual_complex_map()


class DegenerationCentralFibers(OwnedCategoryOverBaseRing):
    r"""Central fibres over one base with connected intersection strata."""

    _MorCategory = DegenerationCentralFiberMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    def _repr_object_names(self):
        return f"central fibres with component incidence over {self.base_ring()}"

    def an_object(self):
        pass

    def on(self, central_fiber, component_inclusions, intersection_strata):
        r"""Select the exact scheme, its components, and connected intersection strata."""
        pass

    def from_family(self, family, central_point, component_inclusions, intersection_strata):
        r"""Select the central fibre of a family with its intersection data."""
        pass

    @cached_method
    def forget(self):
        return _UnderlyingCentralFiberFunctor(self)

    @cached_method
    def dual_complexes(self):
        return _DualComplexFunctor(self)

    class ParentMethods:
        def __init__(self, central_fiber, component_inclusions, intersection_strata, **rest):
            self._central_fiber = central_fiber
            self._component_inclusions = component_inclusions
            self._intersection_strata = intersection_strata
            super().__init__(**rest)

        def underlying_scheme(self):
            return self._central_fiber

        def component_inclusions(self):
            return self._component_inclusions

        def intersection_strata(self):
            return self._intersection_strata

        def dual_complex(self):
            pass

        def dual_cell_correspondence(self):
            pass
