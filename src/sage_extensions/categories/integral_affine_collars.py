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
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.integral_affine_manifolds import (
    IntegralAffineManifolds,
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
        r"""Select a face, its neighborhood in the piece, and an affine collar chart.

        A collar is the datum that makes "glue along this face" an integral-affine
        operation rather than a topological one: a face of an affine piece, a
        neighborhood of that face in the piece, and an affine chart of the
        neighborhood, so that two pieces presented with collars along a common face
        can be compared chartwise.  The four selected data are exactly that, and the
        object retains them rather than reconstructing any of them (``OWN-15``).

        Both inclusions select into the smooth manifold *this* affine structure is
        added to -- the piece's own underlying manifold, which is where its faces
        live -- and the collar chart is a chart of the neighborhood it is stated on.
        An arrow of integral-affine manifolds has no constructor in this tree yet, so
        a selection into the piece as an affine object is not writable, and a
        selection into another manifold, even an equal one, is refused.  Whether the
        neighbourhood really
        is a neighbourhood of the face -- that the face lies in it and that it
        contains an open set around every point of the face -- is a question about
        the piece's own topology, and it is not re-decided here.
        """
        assert affine_piece in IntegralAffineManifolds(), (
            f"a collar is selected on an integral-affine piece, and {affine_piece} is "
            f"in {affine_piece.category()}"
        )
        selected_in = affine_piece.underlying_smooth_manifold()
        for inclusion in (face_inclusion, neighborhood_inclusion):
            assert inclusion.codomain() is selected_in, (
                f"{inclusion} selects into {inclusion.codomain()}, not into "
                f"{selected_in}, the manifold {affine_piece} adds its affine structure "
                f"to: a collar's face and neighbourhood are selected in the piece itself"
            )
        assert collar_chart.domain() is neighborhood_inclusion.domain(), (
            f"the collar chart is stated on the neighbourhood "
            f"{neighborhood_inclusion.domain()}, but {collar_chart} is defined on "
            f"{collar_chart.domain()}"
        )
        return _object_of(
            self,
            affine_piece=affine_piece,
            face_inclusion=face_inclusion,
            neighborhood_inclusion=neighborhood_inclusion,
            collar_chart=collar_chart,
        )

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
