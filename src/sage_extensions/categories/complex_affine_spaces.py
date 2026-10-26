r"""Complex affine chart models over the exact complex field."""

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.modules.pure.modules import VectorSpaces
from sage_extensions.categories.rings.ring_foundation import _owned_integers
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.rings.complex import CC


class ComplexVectorSpaces(OwnedParameterizedCategory):
    r"""Complex vector spaces of a fixed finite dimension."""

    @staticmethod
    def __classcall__(cls, dimension):
        dimension = _owned_integers()(dimension)
        if dimension < 0:
            raise ValueError(f"a complex vector-space dimension must be nonnegative, not {dimension}")
        return Category.__classcall__(cls, dimension)

    def dimension(self):
        return self.parameter()

    def super_categories(self):
        return [VectorSpaces(CC)]

    def _repr_object_names(self):
        return f"complex vector spaces of dimension {self.dimension()}"

    def an_object(self):
        pass

    def __contains__(self, vector_space):
        return vector_space in VectorSpaces(CC) and vector_space.dimension() == self.dimension()

    def on(self, vector_space):
        if vector_space not in self:
            raise TypeError(f"{vector_space} is not a complex vector space of dimension {self.dimension()}")
        return vector_space

    @cached_method
    def affinization(self):
        return _ComplexAffinizationFunctor(self.dimension())


class ComplexAffineSpaceMor(CategoricalMor):
    r"""Affine maps with a complex-linear part and an equivariant point map."""

    class ElementMethods:
        def __init__(self, parent, linear_part, point_map):
            Morphism.__init__(self, parent)
            self._linear_part = linear_part
            self._point_map = point_map

        def linear_part(self):
            return self._linear_part

        def point_map(self):
            return self._point_map

        def _call_(self, point):
            return self._point_map(point)

        def __mul__(self, other):
            pass

    def _element_constructor_(self, linear_part, point_map):
        pass

    @object_level
    def identity(self):
        pass


class ComplexAffineSpaceMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = ComplexAffineSpaceMor


class _ComplexAffinizationFunctor(Functor):
    def __init__(self, dimension):
        super().__init__(ComplexVectorSpaces(dimension), ComplexAffineSpaces())

    def _apply_object(self, vector_space):
        pass

    def _apply_morphism(self, linear_map):
        pass


class _ComplexAffineUnderlyingSetFunctor(Functor):
    def __init__(self):
        super().__init__(ComplexAffineSpaces(), Sets())

    def _apply_object(self, affine_space):
        return affine_space.point_set()

    def _apply_morphism(self, morphism):
        return morphism.point_map()


class _ComplexAffineModelFunctor(Functor):
    def __init__(self):
        super().__init__(ComplexAffineSpaces(), VectorSpaces(CC))

    def _apply_object(self, affine_space):
        return affine_space.model_vector_space()

    def _apply_morphism(self, morphism):
        return morphism.linear_part()


class _ComplexAffineHolomorphicAtlasFunctor(Functor):
    r"""Give a complex affine space its translation charts."""

    def __init__(self):
        from sage_extensions.categories.holomorphic_atlases import HolomorphicAtlases

        super().__init__(ComplexAffineSpaces(), HolomorphicAtlases())

    def _apply_object(self, affine_space):
        pass

    def _apply_morphism(self, affine_map):
        pass


class ComplexAffineSpaces(OwnedCategory):
    r"""Torsors for additive complex vector spaces, with affine maps."""

    _MorCategory = ComplexAffineSpaceMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "complex affine spaces"

    def an_object(self):
        pass

    def on(self, model_vector_space, point_set, translation_action, difference, point):
        r"""Select an affine torsor with its difference map and nonempty witness."""
        pass

    def from_torsor(self, model_vector_space, torsor):
        r"""Place the selected torsor under the model space's additive group."""
        pass

    @cached_method
    def forget(self):
        return _ComplexAffineUnderlyingSetFunctor()

    @cached_method
    def model_vector_space(self):
        return _ComplexAffineModelFunctor()

    @cached_method
    def holomorphic_atlas(self):
        return _ComplexAffineHolomorphicAtlasFunctor()

    @cached_method
    def holomorphic_manifold(self):
        from sage_extensions.categories.holomorphic_atlases import HolomorphicAtlases

        return self.holomorphic_atlas().then(HolomorphicAtlases().maximalization())

    class ParentMethods:
        def __init__(self, model_vector_space, torsor, **rest):
            self._model_vector_space = model_vector_space
            self._torsor = torsor
            super().__init__(facade=torsor.point_set(), **rest)

        def point_set(self):
            return self._torsor.point_set()

        def __contains__(self, point):
            return point in self.point_set()

        def _element_constructor_(self, point):
            return self.point_set()(point)

        def an_element(self):
            return self.underlying_torsor().an_element()

        def model_vector_space(self):
            return self._model_vector_space

        def translation_action(self):
            return self._torsor.action()

        def underlying_torsor(self):
            r"""The selected torsor under the model space's additive group."""
            return self._torsor

        def difference(self, left, right):
            r"""The model vector carrying ``right`` to ``left``."""
            return self.underlying_torsor().difference(left, right)

        def chart_at(self, origin):
            r"""The global holomorphic chart carrying ``origin`` to zero of the model space."""
            pass
