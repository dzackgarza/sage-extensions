r"""Selected integral-affine collars along faces of affine pieces."""

from sage.misc.cachefunc import cached_method
from sage.categories.morphism import Morphism

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.integral_affine_manifolds import (
    IntegralAffineManifoldsWithCorners,
)


class IntegralAffineCollarMor(CategoricalMor):
    r"""Affine maps of collar neighborhoods compatible with the selected faces."""

    class ElementMethods:
        def __init__(self, parent, face_map, neighborhood_affine_map):
            Morphism.__init__(self, parent)
            self._face_map = face_map
            self._neighborhood_affine_map = neighborhood_affine_map

        def face_map(self):
            return self._face_map

        def neighborhood_affine_map(self):
            return self._neighborhood_affine_map

        def __mul__(self, other):
            pass

    def _element_constructor_(self, face_map, neighborhood_affine_map):
        pass

    @object_level
    def identity(self):
        pass


class IntegralAffineCollarMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = IntegralAffineCollarMor


class _CollarNeighborhoodFunctor(Functor):
    r"""Take the selected neighborhood and its affine comparison map."""

    def __init__(self):
        super().__init__(IntegralAffineCollars(), IntegralAffineManifoldsWithCorners())

    def _apply_object(self, collar):
        return collar.neighborhood_inclusion().domain()

    def _apply_morphism(self, morphism):
        return morphism.neighborhood_affine_map()


class _CollarFaceFunctor(Functor):
    r"""Send a collar and its comparison to the selected face and face map."""

    def __init__(self):
        super().__init__(IntegralAffineCollars(), IntegralAffineManifoldsWithCorners())

    def _apply_object(self, collar):
        return collar.face()

    def _apply_morphism(self, morphism):
        return morphism.face_map()


class IntegralAffineCollars(OwnedCategory):
    r"""Affine neighborhood collars with a specified face inclusion."""

    _MorCategory = IntegralAffineCollarMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine collars"

    def an_object(self):
        pass

    def on(self, affine_piece, face_inclusion, neighborhood_inclusion, collar_chart):
        r"""Select a face, its neighborhood in the piece, and an affine collar chart."""
        pass

    def comparison(self, source_collar, target_collar, face_map, neighborhood_affine_map):
        r"""Select an affine extension of a specified face pairing."""
        pass

    @cached_method
    def neighborhoods(self):
        return _CollarNeighborhoodFunctor()

    @cached_method
    def faces(self):
        return _CollarFaceFunctor()

    class ParentMethods:
        def __init__(
            self,
            affine_piece,
            face_inclusion,
            neighborhood_inclusion,
            collar_chart,
            **rest,
        ):
            self._affine_piece = affine_piece
            self._face_inclusion = face_inclusion
            self._neighborhood_inclusion = neighborhood_inclusion
            self._collar_chart = collar_chart
            super().__init__(**rest)

        def underlying_affine_manifold(self):
            return self._affine_piece

        def face_inclusion(self):
            return self._face_inclusion

        def neighborhood_inclusion(self):
            return self._neighborhood_inclusion

        def collar_chart(self):
            return self._collar_chart

        def face(self):
            return self._face_inclusion.domain()

        def affine_piece(self):
            return self._affine_piece
