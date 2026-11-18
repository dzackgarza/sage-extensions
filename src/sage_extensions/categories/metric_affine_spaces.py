r"""Euclidean affine spaces and their spherical unit subspaces."""

from sage.misc.cachefunc import cached_method
from sage.categories.morphism import Morphism

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.real_affine_spaces import RealAffineSpaces, RealVectorSpaces
from sage_extensions.owned_category import _object_of
from sage_extensions.rings.real import RR


class EuclideanSpaceMor(CategoricalMor):
    r"""Affine isometries between selected Euclidean spaces."""

    class ElementMethods:
        def __init__(self, parent, affine_map):
            Morphism.__init__(self, parent)
            self._affine_map = affine_map

        def affine_map(self):
            return self._affine_map

        def _call_(self, point):
            return self._affine_map(point)

        def __mul__(self, other):
            r"""Compose the affine maps of the two arrows, in this order.

            An isometry composed with an isometry is an isometry, and the
            composite's affine map is the composite of theirs: the two linear
            parts compose and the two translation parts follow, which the
            underlying affine space's own composition already computes.
            """
            if other.codomain() is not self.domain():
                return NotImplemented
            return self.parent().base_category().Mor(other.domain(), self.codomain())(
                self._affine_map * other._affine_map
            )

    def _element_constructor_(self, affine_map):
        r"""Construct the arrow from its affine map.

        The arrow is an affine map of the underlying affine spaces, that map is
        its defining datum, and one of other endpoints is refused here rather
        than stored and found later.  Whether the map preserves the metric is
        the decision of :meth:`EuclideanSpaces.ParentMethods.is_an_isometry`,
        which this category states and does not make.
        """
        if (
            affine_map.domain() is not self.domain().underlying_affine_space()
            or affine_map.codomain() is not self.codomain().underlying_affine_space()
        ):
            raise ValueError(
                f"an arrow of {self} is an affine map {self.domain().underlying_affine_space()} "
                f"-> {self.codomain().underlying_affine_space()}, but {affine_map} is an affine "
                f"map {affine_map.domain()} -> {affine_map.codomain()}"
            )
        return self.element_class(self, affine_map)

    @object_level
    @cached_method
    def identity(self):
        r"""The identity isometry: the identity affine map of the underlying space."""
        space = self.domain()
        affine_space = space.underlying_affine_space()
        return self(RealAffineSpaces().Mor(affine_space, affine_space).identity())


class EuclideanSpaceMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = EuclideanSpaceMor


class _ForgetEuclideanMetric(Functor):
    def __init__(self):
        super().__init__(EuclideanSpaces(), RealAffineSpaces())

    def _apply_object(self, space):
        return space.underlying_affine_space()

    def _apply_morphism(self, morphism):
        return morphism.affine_map()


class EuclideanSpaces(OwnedCategory):
    r"""Real affine spaces with a selected positive-definite model-space form."""

    _MorCategory = EuclideanSpaceMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "Euclidean affine spaces"

    def an_object(self):
        r"""Return the Euclidean line: the real line with the standard inner product."""
        vector_space = RealVectorSpaces(1).an_object()
        affine_space = RealVectorSpaces(1).affinization()(vector_space)
        return self.on(affine_space, vector_space.bilinear_forms(RR)([[RR.one()]]))

    def on(self, affine_space, positive_definite_form):
        r"""Select a Euclidean space: an affine space and the inner product of its model.

        The inner product is chosen data, as a Riemannian metric is: a real
        affine space admits many positive definite forms on its model and none
        of them is canonical, so the form is read from the caller and not
        computed here.  What this category states is that this form is the
        space's metric, and every isometry decision it makes is a decision about
        this form: a map of the space is an isometry exactly when its linear
        part preserves it (:meth:`ParentMethods.is_an_isometry`).
        """
        assert affine_space in RealAffineSpaces(), (
            f"a Euclidean space is a real affine space with a selected inner product, but "
            f"{affine_space} is in {affine_space.category()}"
        )
        model = affine_space.model_vector_space()
        assert positive_definite_form in model.bilinear_forms(RR), (
            f"the inner product of a Euclidean space is a bilinear form on the model space "
            f"{model} of its affine space, but {positive_definite_form} is not one"
        )
        return _object_of(
            self,
            affine_space=affine_space,
            positive_definite_form=positive_definite_form,
        )

    @cached_method
    def forget_metric(self):
        r"""Forget the selected inner product on objects and on their arrows.

        An isometry of a Euclidean space is an affine map of the underlying
        affine space, and forgetting the metric sends it there: the arrow keeps
        its affine map and loses the statement that the map preserves the form.
        """
        return _ForgetEuclideanMetric()

    class ParentMethods:
        def __init__(self, affine_space, positive_definite_form, **rest):
            self._affine_space = affine_space
            self._positive_definite_form = positive_definite_form
            super().__init__(**rest)

        def underlying_affine_space(self):
            return self._affine_space

        def model_inner_product(self):
            return self._positive_definite_form

        def point_set(self):
            return self._affine_space.point_set()

        def __contains__(self, point):
            return point in self.point_set()

        def _element_constructor_(self, point):
            r"""Coerce a point through the point set: an element of this space is one of its points."""
            return self.point_set()(point)

        def model_vector_space(self):
            r"""The model space of the underlying affine space, where the inner product lives."""
            return self._affine_space.model_vector_space()

        def translation_action(self):
            r"""The translations of the underlying affine space, acting on the points of this space.

            Forgetting the metric forgets this action and nothing else: the points
            of a Euclidean space are the points of its affine space, so the same
            model vectors translate them.
            """
            return self._affine_space.translation_action()

        def difference(self, left, right):
            r"""The model vector carrying the point ``right`` to the point ``left``."""
            return self._affine_space.difference(left, right)

        def an_element(self):
            return self._affine_space.an_element()

        def is_an_isometry(self, ambient_map) -> bool:
            r"""Decide whether a map of this Euclidean space is an isometry of it.

            An affine map ``x |-> A x + t`` of a Euclidean space is an isometry
            exactly when its linear part ``A`` preserves the selected inner
            product ``b`` (a translation is an isometry of every Euclidean
            space), that is when ``b(A x, A y) = b(x, y)`` for all ``x, y``.
            ``b`` is bilinear, so its values on pairs of the model space's
            generators determine it, and those finitely many equalities are the
            decision: it reads the form of this space and the map's linear part,
            and nothing about any lattice or any chosen coordinates.

            A map of another space is refused rather than answered: this space's
            inner product is not the form of a map between other endpoints.
            """
            if ambient_map.domain() is not self or ambient_map.codomain() is not self:
                raise ValueError(
                    f"the isometry decision of {self} is a decision about its own maps, but "
                    f"{ambient_map} carries {ambient_map.domain()} into {ambient_map.codomain()}"
                )
            form = self.model_inner_product()
            linear_part = ambient_map.affine_map().linear_part()
            generators = tuple(self.model_vector_space().module_generators())
            preserved = tuple(
                form(linear_part(left), linear_part(right)) == form(left, right)
                for left in generators
                for right in generators
            )
            undecided = tuple(
                answer for answer in preserved if not isinstance(answer, bool)
            )
            assert not undecided, (
                f"the inner product of {self} does not decide whether {ambient_map} preserves it: "
                f"{undecided[0]} is not decided, so this space states no isometry decision for it"
            )
            return all(preserved)


class SphericalSpaceMor(CategoricalMor):
    r"""Isometries of selected round spheres."""

    class ElementMethods:
        def __init__(self, parent, ambient_isometry):
            Morphism.__init__(self, parent)
            self._ambient_isometry = ambient_isometry

        def ambient_isometry(self):
            return self._ambient_isometry

        def underlying_sphere_morphism(self):
            pass

        def _call_(self, point):
            return self._ambient_isometry(point)

        def __mul__(self, other):
            r"""Compose the ambient isometries of the two arrows, in this order.

            An isometry of the sphere composed with an isometry of the sphere is
            one, and the composite's ambient isometry is the composite of theirs:
            the sphere's arrows carry no other datum.
            """
            if other.codomain() is not self.domain():
                return NotImplemented
            return self.parent().base_category().Mor(other.domain(), self.codomain())(
                self._ambient_isometry * other._ambient_isometry
            )

    def _element_constructor_(self, ambient_isometry):
        r"""Construct the arrow from the ambient isometry it is.

        An arrow of a round sphere is an ambient isometry of the Euclidean space
        the sphere lies in -- the datum this category states -- and one carrying
        another sphere's Euclidean space is refused here rather than stored.  That
        the ambient isometry preserves the sphere, and not only the Euclidean
        metric, is the decision of
        :meth:`SphericalSpaces.ParentMethods.is_an_isometry`, which this category
        states and does not make.
        """
        if (
            ambient_isometry.domain() is not self.domain().euclidean_space()
            or ambient_isometry.codomain() is not self.codomain().euclidean_space()
        ):
            raise ValueError(
                f"an arrow of {self} is an isometry of the Euclidean space "
                f"{self.domain().euclidean_space()} the sphere lies in, but "
                f"{ambient_isometry} carries {ambient_isometry.domain()} into "
                f"{ambient_isometry.codomain()}"
            )
        return self.element_class(self, ambient_isometry)

    @object_level
    @cached_method
    def identity(self):
        r"""The identity isometry: the identity of the Euclidean space the sphere lies in."""
        euclidean = self.domain().euclidean_space()
        return self(euclidean.category().Mor(euclidean, euclidean).identity())


class SphericalSpaceMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SphericalSpaceMor


class SphericalSpaces(OwnedCategory):
    r"""Round spheres with selected center, radius and Euclidean inclusion."""

    _MorCategory = SphericalSpaceMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "round spherical spaces"

    def an_object(self):
        r"""Return the zero-sphere: the two points at distance one from the line's origin.

        The round zero-sphere `S^0` is the pair `\{-1, 1\}` of the Euclidean line,
        centred at the line's origin with radius one.  Its isometry group is the
        pair of its two permutations, the identity and the swap, as the sphere's
        own decision answers.
        """
        euclidean = EuclideanSpaces().an_object()
        centre = euclidean.an_element()
        radius = RR.one()
        inner_product = euclidean.model_inner_product()
        points = euclidean.point_set()
        return self.in_space(
            euclidean,
            centre,
            radius,
            points.condition_set(
                lambda point: inner_product(
                    euclidean.difference(point, centre),
                    euclidean.difference(point, centre),
                )
                == radius * radius
            ).inclusion(),
        )

    def in_space(self, euclidean_space, center, radius, inclusion):
        r"""Select the round sphere with this centre, radius and inclusion.

        ``euclidean_space`` is the Euclidean space the sphere lies in, ``center``
        its centre and ``radius`` its radius there, and ``inclusion`` is the map
        of the sphere's points into that space's points.  These four are the
        sphere: they are read from the caller and nothing is computed from them,
        because which round sphere a use wants is a choice.  Every decision the
        sphere makes is a decision about them -- an arrow of it is an ambient
        isometry, and it preserves the sphere exactly when it fixes this centre
        (:meth:`ParentMethods.is_an_isometry`).
        """
        assert euclidean_space in EuclideanSpaces(), (
            f"a round sphere lies in a Euclidean space, but {euclidean_space} is in "
            f"{euclidean_space.category()}"
        )
        assert inclusion.codomain() is euclidean_space.point_set(), (
            f"the points of a sphere in {euclidean_space} are points of that space, but "
            f"{inclusion} lands in {inclusion.codomain()}"
        )
        assert radius.is_zero() is False, (
            f"a round sphere has a nonzero radius, and this one is selected with radius {radius}"
        )
        return _object_of(
            self,
            euclidean_space=euclidean_space,
            center=center,
            radius=radius,
            inclusion=inclusion,
        )

    class ParentMethods:
        def __init__(self, euclidean_space, center, radius, inclusion, **rest):
            self._euclidean_space = euclidean_space
            self._center = center
            self._radius = radius
            self._inclusion = inclusion
            super().__init__(**rest)

        def euclidean_space(self):
            return self._euclidean_space

        def center(self):
            return self._center

        def radius(self):
            return self._radius

        def inclusion(self):
            return self._inclusion

        def underlying_sphere(self):
            return self._inclusion.domain()

        def point_set(self):
            r"""The points of the sphere: the points of its underlying sphere."""
            return self._inclusion.domain()

        def underlying_affine_space(self):
            r"""The affine space of the Euclidean space the sphere lies in."""
            return self._euclidean_space.underlying_affine_space()

        def __contains__(self, point):
            return point in self.point_set()

        def _element_constructor_(self, point):
            r"""Coerce a point through the point set: an element of this sphere is one of its points."""
            return self.point_set()(point)

        def is_an_isometry(self, ambient_map) -> bool:
            r"""Decide whether a map of this round sphere is an isometry of it.

            An arrow of a round sphere is an ambient isometry of the Euclidean
            space it lies in, so the decision has two parts.  The ambient map must
            be a Euclidean isometry, which that space decides from its own inner
            product; and it must carry the sphere to itself, which -- the centre
            determining the sphere it is the centre of -- is that it fixes the
            centre.  A Euclidean isometry that moves the centre is a map of the
            Euclidean space and not of this sphere, and is refused here, so no
            affine or Euclidean check stands in for the sphere's own.

            A map of another sphere is refused rather than answered: this
            sphere's centre is not the centre of a map between other endpoints.
            """
            if ambient_map.domain() is not self or ambient_map.codomain() is not self:
                raise ValueError(
                    f"the isometry decision of {self} is a decision about its own maps, but "
                    f"{ambient_map} carries {ambient_map.domain()} into {ambient_map.codomain()}"
                )
            euclidean = self.euclidean_space()
            ambient = ambient_map.ambient_isometry()
            if euclidean.is_an_isometry(ambient) is not True:
                return False
            return ambient(self.center()) == self.center()
