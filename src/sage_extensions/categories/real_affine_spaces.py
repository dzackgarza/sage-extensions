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
from sage_extensions.owned_category import _object_of
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
            if other.codomain() is not self.domain():
                raise ValueError(
                    f"cannot compose {self} after {other}: the codomain "
                    f"{other.codomain()} of the second map is not the domain "
                    f"{self.domain()} of the first"
                )
            # A linear map is its images on the model's selected generating
            # set, so the composite's linear part is the composite's values
            # there; the point maps compose as maps of sets.
            model = self.codomain().model_vector_space()
            composite_linear = model.Mor(model)(
                lambda label: self.linear_part()(
                    other.linear_part()(model.module_generator(label))
                )
            )
            return RealAffineSpaces().Mor(other.domain(), self.codomain())(
                composite_linear,
                self.point_map() * other.point_map(),
            )

    def _element_constructor_(self, linear_part, point_map):
        r"""Construct the affine map with this linear part and point map."""
        if (
            linear_part.domain() is not self.domain().model_vector_space()
            or linear_part.codomain() is not self.codomain().model_vector_space()
        ):
            raise ValueError(
                f"the linear part of an affine map {self.domain()} -> {self.codomain()} "
                f"carries {self.domain().model_vector_space()} into "
                f"{self.codomain().model_vector_space()}, but {linear_part} carries "
                f"{linear_part.domain()} into {linear_part.codomain()}"
            )
        if (
            point_map.domain() is not self.domain().point_set()
            or point_map.codomain() is not self.codomain().point_set()
        ):
            raise ValueError(
                f"the point map of an affine map {self.domain()} -> {self.codomain()} "
                f"carries {self.domain().point_set()} into {self.codomain().point_set()}, "
                f"but {point_map} carries {point_map.domain()} into {point_map.codomain()}"
            )
        return self.element_class(self, linear_part, point_map)

    @object_level
    @cached_method
    def identity(self):
        r"""The identity affine map: the identities of the model space and of the point set."""
        space = self.domain()
        return self(
            space.model_vector_space().Mor(space.model_vector_space()).identity(),
            Sets().Mor(space.point_set(), space.point_set()).identity(),
        )


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


class _AffineTorsor:
    r"""An affine space as the torsor it is: a nonempty set under the model's translations.

    Private computation class (``OWN-06``).  Its data are the four the affine
    space is selected by -- the acted set, the translation action of the model
    vectors on it, the difference map, and a point witnessing nonemptiness --
    held as the torsor the affine space is realized on.  These are the fields
    of an additive torsor (Mathlib, ``Mathlib/Algebra/Torsor/Defs.lean``):
    ``difference p q`` is the unique vector ``v`` with ``v + q = p``.
    """

    def __init__(
        self, model_vector_space, point_set, translation_action, difference, selected_point
    ) -> None:
        self._model_vector_space = model_vector_space
        self._point_set = point_set
        self._translation_action = translation_action
        self._difference = difference
        self._selected_point = selected_point

    def model_vector_space(self):
        return self._model_vector_space

    def point_set(self):
        return self._point_set

    def action(self):
        r"""The translation action, a map of two arguments: a vector and a point."""
        return self._translation_action

    def difference(self, left, right):
        r"""The model vector carrying ``right`` to ``left``."""
        return self._difference(left, right)

    def an_element(self):
        return self._selected_point


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
        r"""Select an affine torsor with its difference map and nonempty witness.

        The model space is the space of translations, ``point_set`` is the set
        they act on, ``translation_action`` is that action read as a map of two
        arguments, ``difference`` is the vector carrying one point to another,
        and ``point`` witnesses that the acted set is nonempty.  Nothing is
        computed from them: which points a chart sends where is what the maps
        built on this space answer.
        """
        assert model_vector_space in VectorSpaces(RR), (
            f"an affine space is a torsor under the translations of a real vector space, "
            f"but {model_vector_space} is not a real vector space"
        )
        assert point_set in Sets(), (
            f"the translations of {model_vector_space} must act on a set, but {point_set} "
            f"is not in the category of sets"
        )
        return self.from_torsor(
            model_vector_space,
            _AffineTorsor(
                model_vector_space, point_set, translation_action, difference, point
            ),
        )

    def from_torsor(self, model_vector_space, torsor):
        r"""Place the selected torsor under the model space's additive group."""
        return _object_of(
            self, model_vector_space=model_vector_space, torsor=torsor
        )

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
            if other.codomain() is not self.domain():
                raise ValueError(
                    f"cannot compose {self} after {other}: the codomain "
                    f"{other.codomain()} of the second map is not the domain "
                    f"{self.domain()} of the first"
                )
            return AffineSpacesWithLattice().Mor(other.domain(), self.codomain())(
                self.affine_map() * other.affine_map(),
                self.lattice_map() * other.lattice_map(),
            )

    def _element_constructor_(self, affine_map, lattice_map):
        r"""Construct the lattice-compatible affine map from its two parts."""
        if (
            affine_map.domain() is not self.domain().underlying_affine_space()
            or affine_map.codomain() is not self.codomain().underlying_affine_space()
        ):
            raise ValueError(
                f"the affine part of a map {self.domain()} -> {self.codomain()} is an affine "
                f"map {self.domain().underlying_affine_space()} -> "
                f"{self.codomain().underlying_affine_space()}, but {affine_map} is an affine "
                f"map {affine_map.domain()} -> {affine_map.codomain()}"
            )
        if (
            lattice_map.domain() is not self.domain().affine_lattice()
            or lattice_map.codomain() is not self.codomain().affine_lattice()
        ):
            raise ValueError(
                f"the lattice part of a map {self.domain()} -> {self.codomain()} is a map "
                f"{self.domain().affine_lattice()} -> {self.codomain().affine_lattice()}, but "
                f"{lattice_map} is a map {lattice_map.domain()} -> {lattice_map.codomain()}"
            )
        return self.element_class(self, affine_map, lattice_map)

    @object_level
    @cached_method
    def identity(self):
        r"""The identity: the identities of the underlying affine space and of the selected lattice."""
        space = self.domain()
        return self(
            space.underlying_affine_space()
            .Mor(space.underlying_affine_space())
            .identity(),
            space.affine_lattice().Mor(space.affine_lattice()).identity(),
        )


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
        r"""Select a full integral lattice in the model of ``affine_space``.

        The lattice is the domain of ``lattice_inclusion``, and that map is the
        inclusion of the lattice in the real model space the affine space's
        translations live in.  The lattice is the tangent lattice: its vectors
        are translations, and its points are the points of the model space it
        is a full sublattice of, not a second copy of the affine space.
        """
        assert affine_space in RealAffineSpaces(), (
            f"an affine space with a selected lattice is an affine space with a full "
            f"integral lattice in its model, but {affine_space} is in "
            f"{affine_space.category()}"
        )
        assert lattice_inclusion.codomain() is affine_space.model_vector_space(), (
            f"the selected lattice must lie in the model space "
            f"{affine_space.model_vector_space()} of {affine_space}, but "
            f"{lattice_inclusion} lands in {lattice_inclusion.codomain()}"
        )
        lattice = lattice_inclusion.domain()
        assert lattice.module_rank() == affine_space.model_vector_space().dimension(), (
            f"the selected lattice must be a full lattice in "
            f"{affine_space.model_vector_space()}, of rank "
            f"{affine_space.model_vector_space().dimension()}, but {lattice} has rank "
            f"{lattice.module_rank()}"
        )
        return _object_of(
            self, affine_space=affine_space, lattice_inclusion=lattice_inclusion
        )

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
            super().__init__(facade=affine_space.point_set(), **rest)

        def underlying_affine_space(self):
            return self._affine_space

        def lattice_inclusion(self):
            return self._lattice_inclusion

        def affine_lattice(self):
            return self._lattice_inclusion.domain()

        def point_set(self):
            r"""The points of the underlying affine space: the lattice is selected in the model, not on the points."""
            return self.underlying_affine_space().point_set()

        def __contains__(self, point):
            return point in self.point_set()

        def _element_constructor_(self, point):
            return self.point_set()(point)

        def an_element(self):
            return self.underlying_affine_space().an_element()

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
