r"""Real affine spaces as torsors over a selected real vector space."""

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
from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedFreeModules,
    VectorSpaces,
)
from sage_extensions.categories.rings.ring_foundation import _owned_integers
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.rings.real import RR


class _CanonicalAffineSpaceFunctor(Functor):
    r"""Use a real vector space as its canonically based affine space."""

    def __init__(self, dimension):
        super().__init__(RealVectorSpaces(dimension), RealAffineSpaces())

    def _apply_object(self, vector_space):
        pass

    def _apply_morphism(self, linear_map):
        pass


class RealVectorSpaces(OwnedParameterizedCategory):
    r"""Full category of real vector spaces of one fixed finite dimension."""

    @staticmethod
    def __classcall__(cls, dimension):
        dimension = _owned_integers()(dimension)
        if dimension < 0:
            raise ValueError(f"a real vector-space dimension must be nonnegative, not {dimension}")
        return Category.__classcall__(cls, dimension)

    def dimension(self):
        return self.parameter()

    def super_categories(self):
        return [VectorSpaces(RR)]

    def _repr_object_names(self):
        return f"real vector spaces of dimension {self.dimension()}"

    def an_object(self):
        pass

    def __contains__(self, vector_space):
        return vector_space in VectorSpaces(RR) and vector_space.dimension() == self.dimension()

    def on(self, vector_space):
        r"""Place the exact real vector space in its dimension stratum."""
        if vector_space not in self:
            raise TypeError(f"{vector_space} is not a real vector space of dimension {self.dimension()}")
        return vector_space

    @cached_method
    def affinization(self):
        return _CanonicalAffineSpaceFunctor(self.dimension())


class RealAffineSpaceMor(CategoricalMor):
    r"""Affine maps with a linear part and an equivariant point map."""

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
    @cached_method
    def identity(self):
        pass


class RealAffineSpaceMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RealAffineSpaceMor


class _AffineUnderlyingSetFunctor(Functor):
    r"""Forget the translation action, on affine spaces and affine maps."""

    def __init__(self):
        super().__init__(RealAffineSpaces(), Sets())

    def _apply_object(self, affine_space):
        return affine_space.point_set()

    def _apply_morphism(self, morphism):
        return morphism.point_map()


class _AffineModelVectorSpaceFunctor(Functor):
    r"""Take the translation space and linear part of an affine map."""

    def __init__(self):
        super().__init__(RealAffineSpaces(), VectorSpaces(RR))

    def _apply_object(self, affine_space):
        return affine_space.model_vector_space()

    def _apply_morphism(self, morphism):
        return morphism.linear_part()


class _RealAffineAtlasFunctor(Functor):
    r"""Present real affine spaces and maps by their C^k charts."""

    def __init__(self, degree):
        from sage_extensions.categories.real_ck_atlases import RealCkAtlases

        super().__init__(RealAffineSpaces(), RealCkAtlases(degree))

    def _apply_object(self, affine_space):
        pass

    def _apply_morphism(self, affine_map):
        pass


class RealAffineSpaces(OwnedCategory):
    r"""Torsors for additive real vector spaces, with affine maps."""

    _MorCategory = RealAffineSpaceMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "real affine spaces"

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
        return _AffineUnderlyingSetFunctor()

    @cached_method
    def model_vector_space(self):
        return _AffineModelVectorSpaceFunctor()

    @cached_method
    def real_ck_atlas(self, degree):
        return _RealAffineAtlasFunctor(degree)

    @cached_method
    def real_ck_manifold(self, degree):
        from sage_extensions.categories.real_ck_atlases import RealCkAtlases

        return self.real_ck_atlas(degree).then(RealCkAtlases(degree).maximalization())

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
            r"""The global affine chart carrying ``origin`` to zero of the model space."""
            pass


class AffineSpaceWithLatticeMor(CategoricalMor):
    r"""Affine maps whose linear parts carry the selected lattice into the target lattice."""

    class ElementMethods:
        def __init__(self, parent, affine_map, lattice_map):
            Morphism.__init__(self, parent)
            self._affine_map = affine_map
            self._lattice_map = lattice_map

        def affine_map(self):
            return self._affine_map

        def linear_part(self):
            return self._affine_map.linear_part()

        def lattice_map(self):
            return self._lattice_map

        def _call_(self, point):
            return self._affine_map(point)

        def __mul__(self, other):
            pass

    def _element_constructor_(self, affine_map, lattice_map):
        pass

    @object_level
    @cached_method
    def identity(self):
        pass


class AffineSpaceWithLatticeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = AffineSpaceWithLatticeMor


class _UnderlyingAffineSpaceFunctor(Functor):
    r"""Forget the selected lattice embedding, on spaces and maps."""

    def __init__(self):
        super().__init__(AffineSpacesWithLattice(), RealAffineSpaces())

    def _apply_object(self, space):
        return space.underlying_affine_space()

    def _apply_morphism(self, morphism):
        return morphism.affine_map()


class _AffineLatticeFunctor(Functor):
    r"""Take the selected integral lattice and induced linear lattice map."""

    def __init__(self):
        super().__init__(AffineSpacesWithLattice(), FinitelyGeneratedFreeModules(_owned_integers()))

    def _apply_object(self, space):
        return space.affine_lattice()

    def _apply_morphism(self, morphism):
        return morphism.lattice_map()


class AffineSpacesWithLattice(OwnedCategory):
    r"""Real affine spaces with a selected full lattice in their model space."""

    _MorCategory = AffineSpaceWithLatticeMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "real affine spaces with a selected lattice"

    def an_object(self):
        pass

    def on(self, affine_space, lattice_inclusion):
        r"""Select a full integral lattice in the model of ``affine_space``."""
        pass

    @cached_method
    def forget(self):
        return _UnderlyingAffineSpaceFunctor()

    @cached_method
    def lattice(self):
        return _AffineLatticeFunctor()

    class ParentMethods:
        def __init__(self, affine_space, lattice_inclusion, **rest):
            self._affine_space = affine_space
            self._lattice_inclusion = lattice_inclusion
            super().__init__(**rest)

        def underlying_affine_space(self):
            return self._affine_space

        def lattice_inclusion(self):
            return self._lattice_inclusion

        def affine_lattice(self):
            return self._lattice_inclusion.domain()

        def chart_at(self, origin):
            r"""The origin-based affine chart with its selected lattice embedding."""
            pass

        def translation_group(self):
            return self.underlying_affine_space().model_vector_space().underlying_additive_group()

        def linear_extension_of_lattice_automorphisms(self):
            r"""Return the action of ``GL(Lambda)`` on the real model space."""
            pass

        def integral_affine_group(self):
            pass

        def integral_affine_group_action(self):
            pass
