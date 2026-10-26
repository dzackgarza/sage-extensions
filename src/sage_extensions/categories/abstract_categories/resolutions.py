r"""Categories of chosen truncated projective resolutions.

For a category C, a projective class P <= C and an ordinal n <= omega, Resolutions(C, P, n)
is a category of chosen data over objects of C.  Its objects are augmented
simplicial resolutions through degree n whose resolved levels lie in P; its
morphisms are maps of the augmented truncated simplicial objects.  The target
projection remembers only the augmentation target.  Hence this is not a
subcategory of C: several resolution objects can lie over the same object.
For finite truncation the resolution equations concern the augmentation
and degrees below the last chosen level. A degree-one presentation gives
its degree-zero coequalizer, not vanishing of top-degree homotopy or a
resolution terminating in degree one.
The session ordinal ``omega0`` selects an untruncated resolution.

The common owner supplies three constructions whose acyclicity follows from
the construction itself: a projective-source epimorphism in truncation zero,
the constant length-zero resolution of a projective object, and the standard
comonadic bar resolution attached to an adjunction F left adjoint to U.
Additive specializations may represent the same datum by a chain complex.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage.misc.unknown import Unknown
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _category_accepts_morphism,
    _category_mor_parent,
    _category_packet,
)
from sage_extensions.categories.abstract_categories.mor_foundation import (
    object_level,
)
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
)
from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.sets.cardinals import omega0
from sage_extensions.owned_category import _object_of


def _normalize_truncation(truncation):
    match truncation:
        case _ if truncation is omega0:
            return omega0
        case _:
            value = int(truncation)
            match value < 0:
                case True:
                    raise ValueError(
                        f"a resolution truncation is a nonnegative degree, but got {truncation}"
                    )
                case False:
                    return value


def _iterate_functor(functor: Functor, value, count: int):
    result = value
    for _ in range(int(count)):
        result = functor(result)
    return result


def _component_function(components):
    match components:
        case Mapping():
            return components.__getitem__
        case _ if callable(components):
            return components
        case _:
            raise TypeError(
                "a morphism of resolutions needs its degree components as a mapping or callable"
            )


class ResolutionMorphism(Morphism):
    r"""A map of chosen truncated resolutions."""

    def __init__(self, parent, components, *, target_morphism=None) -> None:
        Morphism.__init__(self, parent)
        source = self.domain()
        target = self.codomain()
        category = source.resolution_category()
        match target.resolution_category() is category:
            case False:
                raise ValueError(
                    f"a resolution morphism needs one resolution category, but {source} lies in "
                    f"{category} and {target} lies in {target.resolution_category()}"
                )
            case True:
                pass
        base = category.base_category()
        match target_morphism:
            case None:
                match source.target() is target.target():
                    case False:
                        raise ValueError(
                            f"a resolution map {source} -> {target} over different targets needs a base morphism "
                            f"{source.target()} -> {target.target()}"
                        )
                    case True:
                        target_morphism = _category_mor_parent(
                            base, source.target(), target.target()
                        ).identity()
            case _:
                pass
        match _category_accepts_morphism(
            base, source.target(), target.target(), target_morphism
        ):
            case False:
                raise TypeError(
                    f"the map below a resolution morphism {source} -> {target} must be a morphism "
                    f"{source.target()} -> {target.target()} of {base}, but it is {target_morphism}"
                )
            case True:
                pass
        self._target_morphism = target_morphism
        self._component_function = _component_function(components)
        source._validate_resolution_morphism_to(
            target,
            self._target_morphism,
            self._component_function,
        )

    def target_morphism(self):
        return self._target_morphism

    base_morphism = target_morphism

    def component(self, degree: int):
        degree = int(degree)
        match 0 <= degree <= self.domain().truncation():
            case False:
                raise ValueError(
                    f"the resolution map {self} has components only in degrees 0 through "
                    f"{self.domain().truncation()}, but degree {degree} was requested"
                )
            case True:
                return self._component_function(degree)

    def __mul__(self, other):
        match other:
            case ResolutionMorphism() if other.codomain() is self.domain():
                category = self.domain().resolution_category()
                return category.Mor(other.domain(), self.codomain())(
                    lambda degree: self.component(degree) * other.component(degree),
                    target_morphism=self.target_morphism() * other.target_morphism(),
                )
            case _:
                return NotImplemented

    def __eq__(self, other):
        match self is other:
            case True:
                return True
            case False:
                pass
        match (
            isinstance(other, ResolutionMorphism)
            and self.domain() is other.domain()
            and self.codomain() is other.codomain()
        ):
            case False:
                return False
            case True:
                pass
        from sage_extensions.logic import AtomicProposition, conjunction

        target_equal = self.target_morphism() == other.target_morphism()
        match target_equal:
            case False:
                return False
            case _:
                pass
        match self.domain().truncation():
            case _ if self.domain().truncation() is omega0:
                return AtomicProposition("equal", self, other)
            case truncation:
                return conjunction(
                    (
                        target_equal,
                        *(
                            self.component(degree) == other.component(degree)
                            for degree in range(truncation + 1)
                        ),
                    )
                )

    def __ne__(self, other):
        from sage_extensions.logic import negation

        return negation(self == other)

    def _repr_(self) -> str:
        return (
            f"Resolution morphism {self.domain()} -> {self.codomain()} over "
            f"{self.target_morphism()}"
        )


class ResolutionMor(CategoricalMor):
    r"""The Mor object between two chosen truncated resolutions."""

    Element = ResolutionMorphism

    def _element_constructor_(self, components, *, target_morphism=None):
        match components:
            case ResolutionMorphism() as morphism:
                match (
                    morphism.domain() is self.domain()
                    and morphism.codomain() is self.codomain()
                ):
                    case False:
                        raise ValueError(
                            f"cannot view {morphism} as a resolution morphism {self.domain()} -> "
                            f"{self.codomain()}: its endpoints are {morphism.domain()} -> "
                            f"{morphism.codomain()}"
                        )
                    case True:
                        pass
                match morphism.parent() is self:
                    case True:
                        return morphism
                    case False:
                        raise TypeError(
                            f"{morphism} belongs to another Mor; give the resolution components"
                        )
            case _:
                return self.element_class(
                    self,
                    components,
                    target_morphism=target_morphism,
                )

    @object_level
    @cached_method
    def identity(self):
        match self.domain() is self.codomain():
            case False:
                raise ValueError(
                    f"the identity resolution morphism exists only on Mor(P, P), but this is "
                    f"Mor({self.domain()}, {self.codomain()})"
                )
            case True:
                pass
        resolution = self.domain()
        base = resolution.base_category()
        return self(
            lambda degree: _category_mor_parent(
                base, resolution.level(degree), resolution.level(degree)
            ).identity(),
            target_morphism=_category_mor_parent(
                base, resolution.target(), resolution.target()
            ).identity(),
        )


class ResolutionMorCategoryConstruction(MorCategoryConstruction):
    r"""The Mor family of chosen truncated resolutions."""

    def fixed_category_class(self):
        return ResolutionMor


class _ResolutionTargetFunctor(Functor):
    r"""The target projection from a resolution category to its base."""

    def __init__(self, resolution_category) -> None:
        self._resolution_category = resolution_category
        super().__init__(
            resolution_category,
            resolution_category.base_category(),
        )

    def _apply_object(self, resolution: Parent):
        return resolution.target()

    def _apply_morphism(self, morphism: ResolutionMorphism):
        return morphism.target_morphism()

    def _repr_(self) -> str:
        return f"Target projection from {self.domain()}"


class _DegreeZeroResolutionTransport(Functor):
    r"""Transport degree-zero resolutions along a functor preserving the datum."""

    def __init__(self, source, target, functor: Functor) -> None:
        match (source.truncation(), target.truncation()):
            case (0, 0):
                pass
            case _:
                raise ValueError(
                    "generic resolution transport is defined here for degree-zero resolutions; "
                    f"the source and target truncations are {source.truncation()} and "
                    f"{target.truncation()}"
                )
        match functor.domain() == source.base_category():
            case False:
                raise ValueError(
                    f"transport from {source} needs a functor with domain {source.base_category()}, "
                    f"but {functor} starts at {functor.domain()}"
                )
            case True:
                pass
        match functor.codomain() == target.base_category():
            case False:
                raise ValueError(
                    f"transport to {target} needs a functor with codomain {target.base_category()}, "
                    f"but {functor} ends at {functor.codomain()}"
                )
            case True:
                pass
        self._transported_functor = functor
        super().__init__(source, target)

    def transported_functor(self) -> Functor:
        return self._transported_functor

    def _apply_object(self, resolution: Parent):
        return self.codomain().degree_zero(
            self.transported_functor()(resolution.augmentation()),
            length=resolution.length(),
        )

    def _apply_morphism(self, morphism: ResolutionMorphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return self.codomain().Mor(source, target)(
            {0: self.transported_functor()(morphism.component(0))},
            target_morphism=self.transported_functor()(morphism.target_morphism()),
        )

    def _repr_(self) -> str:
        return f"Degree-zero resolution transport along {self.transported_functor()}"


class Resolutions(OwnedCategory):
    r"""The category of chosen n-truncated resolutions with levels in P.

    ``augmentation_family`` states the represented covering arrows used by
    the bare degree-zero constructor. It defaults to categorical
    epimorphisms of the base. A theory may instead supply a stronger exact
    family, such as epimorphisms of the underlying sets for algebra
    generation. The supplied projective class is projective relative to
    those covering arrows; this is part of the resolution datum, not a
    theorem inferred from an arbitrary category's name.
    """

    _MorCategory = ResolutionMorCategoryConstruction

    @staticmethod
    def __classcall__(
        cls,
        base_category: Category,
        projective_class: Category,
        truncation=0,
        level_category=None,
        augmentation_family=None,
    ):
        match level_category:
            case None:
                level_category = projective_class
            case _:
                pass
        if augmentation_family is None:
            augmentation_family = _category_packet(base_category).Epis()
        return Category.__classcall__(
            cls,
            base_category,
            projective_class,
            _normalize_truncation(truncation),
            level_category,
            augmentation_family,
        )

    def __init__(
        self,
        base_category: Category,
        projective_class: Category,
        truncation=0,
        level_category=None,
        augmentation_family=None,
    ) -> None:
        truncation = _normalize_truncation(truncation)
        match level_category:
            case None:
                level_category = projective_class
            case _:
                pass
        if augmentation_family is None:
            augmentation_family = _category_packet(base_category).Epis()
        match projective_class.is_subcategory(base_category):
            case False:
                raise TypeError(
                    f"the projective class of a resolution category over {base_category} must be a "
                    f"subcategory of it, but {projective_class} is not"
                )
            case True:
                pass
        match level_category.is_subcategory(projective_class):
            case False:
                raise TypeError(
                    f"the allowed resolution levels in {level_category} must lie in the projective class "
                    f"{projective_class}, but that subcategory relation is not declared"
                )
            case True:
                pass
        self._base_category = base_category
        self._projective_class = projective_class
        self._level_category = level_category
        self._augmentation_family = augmentation_family
        self._truncation = truncation
        super().__init__()

    def base_category(self) -> Category:
        return self._base_category

    def projective_class(self) -> Category:
        return self._projective_class

    def level_category(self) -> Category:
        r"""Return the category imposed levelwise on this chosen truncation."""
        return self._level_category

    def augmentation_family(self):
        r"""Return the exact covering-arrow family for bare degree-zero data."""
        return self._augmentation_family

    def truncation(self):
        return self._truncation

    def super_categories(self):
        return [Objects()]

    def _repr_(self) -> str:
        return (
            f"{self.truncation()}-truncated resolutions in {self.base_category()} "
            f"with projective class {self.projective_class()}, levels in {self.level_category()}, "
            f"and augmentations in {self.augmentation_family()}"
        )

    def an_object(self):
        return self.constant(self.level_category().an_object())

    @cached_method
    def target_functor(self) -> Functor:
        r"""Return the target projection to the base category."""
        return _ResolutionTargetFunctor(self)

    def _object(
        self,
        target,
        level_function,
        augmentation,
        *,
        face_function=None,
        degeneracy_function=None,
        length=Unknown,
        model="simplicial",
        **construction_data,
    ):
        match target in self.base_category():
            case False:
                raise TypeError(
                    f"a resolution in {self} must resolve an object of {self.base_category()}, "
                    f"but {target} is not one"
                )
            case True:
                pass
        match self.truncation():
            case _ if self.truncation() is omega0:
                pass
            case truncation:
                for degree in range(truncation + 1):
                    term = level_function(degree)
                    match term in self.level_category():
                        case False:
                            raise TypeError(
                                f"degree {degree} of a resolution in {self} must lie in "
                                f"{self.level_category()}, but it is {term}"
                            )
                        case True:
                            pass
        level_zero = level_function(0)
        match _category_accepts_morphism(
            self.base_category(), level_zero, target, augmentation
        ):
            case False:
                raise TypeError(
                    f"the augmentation of a resolution in {self} must be a morphism "
                    f"{level_zero} -> {target} of {self.base_category()}, but it is "
                    f"{augmentation}"
                )
            case True:
                pass
        return _object_of(
            self,
            resolution_target=target,
            resolution_level_function=level_function,
            resolution_augmentation=augmentation,
            resolution_face_function=face_function,
            resolution_degeneracy_function=degeneracy_function,
            resolution_length=length,
            resolution_model=model,
            **construction_data,
        )

    def degree_zero(self, augmentation, *, length=Unknown):
        r"""Return degree-zero data with represented covering-arrow evidence.

        Failure of admission to the selected family may mean that its
        predicate is undecided; it does not establish that the map fails
        the covering condition. Constructor-selected generating data enter
        separately through ``selected_degree_zero`` with their own premise.
        """
        match self.truncation():
            case 0:
                pass
            case _:
                raise ValueError(
                    f"a bare generating epimorphism belongs to truncation zero, but {self} has "
                    f"truncation {self.truncation()}"
                )
        if self.augmentation_family().accepts(augmentation) is not True:
            raise ValueError(
                f"the degree-zero resolution of {augmentation.codomain()} needs represented "
                f"admission of {augmentation} to {self.augmentation_family()}; no such evidence "
                "was supplied by this map's current realization. Constructor-selected "
                "generating augmentations use selected_degree_zero with their defining premise"
            )
        return self._object(
            augmentation.codomain(),
            lambda degree: augmentation.domain(),
            augmentation,
            length=length,
            model="degree-zero",
        )

    def selected_degree_zero(
        self,
        target,
        source,
        augmentation,
        *,
        generating_set,
        generator_morphism,
    ):
        r"""Store one constructor-selected generating epimorphism as resolution data."""
        match self.truncation():
            case 0:
                pass
            case _:
                raise ValueError(
                    f"a selected generating epimorphism supplies truncation zero, but {self} has "
                    f"truncation {self.truncation()}"
                )
        match target in self.base_category():
            case False:
                raise TypeError(
                    f"{target} is not an object of the base category {self.base_category()}"
                )
            case True:
                pass
        match source in self.level_category():
            case False:
                raise TypeError(
                    f"the selected source {source} must lie in the level category "
                    f"{self.level_category()}"
                )
            case True:
                pass
        match augmentation.domain() is source and augmentation.codomain() is target:
            case False:
                raise ValueError(
                    f"the selected augmentation of {target} must be a map {source} -> {target}, "
                    f"but got {augmentation.domain()} -> {augmentation.codomain()}"
                )
            case True:
                pass
        match (
            generator_morphism.domain() is generating_set
            and generator_morphism.codomain() is target
        ):
            case False:
                raise ValueError(
                    f"the selected generator map of {target} must be a map from "
                    f"{generating_set} to {target}"
                )
            case True:
                pass
        return self._object(
            target,
            lambda degree: source,
            augmentation,
            length=Unknown,
            model="selected-generators",
            resolution_generating_set=generating_set,
            resolution_generator_morphism=generator_morphism,
        )

    def selected_presentation(
        self,
        target,
        degree_zero_source,
        degree_one_source,
        augmentation,
        first_face,
        second_face,
        degeneracy,
        *,
        generating_set,
        generator_morphism,
        relation_source=None,
        relations=None,
    ):
        r"""Store a chosen presentation as a 1-truncated reflexive resolution.

        The constructor's presentation premise identifies the target with
        the coequalizer of the two faces. It supplies the represented two
        levels, not a theorem that the projective resolution terminates in
        degree one. The full resolution length therefore remains unknown.
        """
        match self.truncation():
            case 1:
                pass
            case _:
                raise ValueError(
                    f"a selected presentation supplies truncation one, but {self} has "
                    f"truncation {self.truncation()}"
                )
        for degree, source in ((0, degree_zero_source), (1, degree_one_source)):
            match source in self.level_category():
                case False:
                    raise TypeError(
                        f"degree {degree} of a selected presentation in {self} must lie in "
                        f"{self.level_category()}, but it is {source}"
                    )
                case True:
                    pass
        base = self.base_category()
        for name, domain, codomain, morphism in (
            ("augmentation", degree_zero_source, target, augmentation),
            ("first face", degree_one_source, degree_zero_source, first_face),
            ("second face", degree_one_source, degree_zero_source, second_face),
            ("degeneracy", degree_zero_source, degree_one_source, degeneracy),
        ):
            match _category_accepts_morphism(base, domain, codomain, morphism):
                case False:
                    raise TypeError(
                        f"the {name} of a selected presentation in {self} must be a morphism "
                        f"{domain} -> {codomain} of {base}, but it is {morphism}"
                    )
                case True:
                    pass

        def level(degree):
            match int(degree):
                case 0:
                    return degree_zero_source
                case 1:
                    return degree_one_source
                case _:
                    raise ValueError(
                        f"a selected presentation in {self} has represented levels only in degrees 0 and 1"
                    )

        def face(degree, index):
            match int(degree), int(index):
                case (1, 0):
                    return first_face
                case (1, 1):
                    return second_face
                case _:
                    raise ValueError(
                        f"the selected presentation of {target} has only the two degree-one faces"
                    )

        def degeneracy_map(degree, index):
            match int(degree), int(index):
                case (0, 0):
                    return degeneracy
                case _:
                    raise ValueError(
                        f"the selected presentation of {target} has only the degree-zero degeneracy"
                    )

        return self._object(
            target,
            level,
            augmentation,
            face_function=face,
            degeneracy_function=degeneracy_map,
            length=Unknown,
            model="selected-presentation",
            resolution_generating_set=generating_set,
            resolution_generator_morphism=generator_morphism,
            resolution_relation_source=relation_source,
            resolution_relations=relations,
        )

    def constant(self, projective_object):
        r"""Return the length-zero constant resolution of a projective object."""
        match projective_object in self.level_category():
            case False:
                raise TypeError(
                    f"a constant resolution in {self} needs an object of "
                    f"{self.level_category()}, but {projective_object} is not one"
                )
            case True:
                pass
        base = self.base_category()

        def identity():
            return _category_mor_parent(
                base, projective_object, projective_object
            ).identity()

        return self._object(
            projective_object,
            lambda degree: projective_object,
            identity(),
            face_function=lambda degree, index: identity(),
            degeneracy_function=lambda degree, index: identity(),
            length=0,
            model="constant",
        )

    def comonadic(self, adjunction: Adjunction, target):
        r"""Return the selected truncated comonadic bar resolution of target."""
        left = adjunction.left_adjoint()
        right = adjunction.right_adjoint()
        match left.codomain() == self.base_category():
            case False:
                raise ValueError(
                    f"the left adjoint defining a resolution in {self} must land in "
                    f"{self.base_category()}, but {left} lands in {left.codomain()}"
                )
            case True:
                pass
        match right.domain() == self.base_category():
            case False:
                raise ValueError(
                    f"the right adjoint defining a resolution in {self} must start in "
                    f"{self.base_category()}, but {right} starts in {right.domain()}"
                )
            case True:
                pass
        match target in self.base_category():
            case False:
                raise TypeError(
                    f"the comonadic resolution in {self} resolves an object of "
                    f"{self.base_category()}, but {target} is not one"
                )
            case True:
                pass
        comonad = right.then(left)

        def level(degree):
            return _iterate_functor(comonad, target, int(degree) + 1)

        def comultiplication(obj):
            return left(adjunction.unit(right(obj)))

        def face(degree, index):
            degree = int(degree)
            index = int(index)
            tail = _iterate_functor(comonad, target, degree - index)
            return _iterate_functor(
                comonad,
                adjunction.counit(tail),
                index,
            )

        def degeneracy(degree, index):
            degree = int(degree)
            index = int(index)
            tail = _iterate_functor(comonad, target, degree - index)
            return _iterate_functor(
                comonad,
                comultiplication(tail),
                index,
            )

        return self._object(
            target,
            level,
            adjunction.counit(target),
            face_function=face,
            degeneracy_function=degeneracy,
            length=omega0,
            model="comonadic",
        )

    def transport_degree_zero(self, functor: Functor, target_resolutions) -> Functor:
        r"""Transport truncation-zero data when the target owner admits the image.

        The target resolution category is explicit because preservation of
        projectivity and epimorphisms is a theorem about the selected functor,
        not a property of arbitrary functors.  The target constructor performs
        its own admission check on every transported augmentation.
        """
        return _DegreeZeroResolutionTransport(self, target_resolutions, functor)

    def dold_kan_image(self):
        r"""Return the augmented-chain realization when the base is a module category."""
        from sage_extensions.categories.modules.pure.modules import Modules
        from sage_extensions.categories.modules.resolutions import (
            ModuleResolutions,
        )

        base = self.base_category()
        match base:
            case Modules():
                return ModuleResolutions(self)
            case _:
                raise TypeError(
                    f"Dold--Kan chain realization is defined here for module resolutions, "
                    f"but {self} is over {base}"
                )

    class ParentMethods:
        r"""One chosen truncated resolution."""

        def __init__(
            self,
            resolution_target,
            resolution_level_function: Callable[[int], Parent],
            resolution_augmentation,
            resolution_face_function=None,
            resolution_degeneracy_function=None,
            resolution_length=Unknown,
            resolution_model="simplicial",
            resolution_generating_set=None,
            resolution_generator_morphism=None,
            resolution_relation_source=None,
            resolution_relations=None,
            resolution_cofiber_data=None,
            **rest,
        ) -> None:
            self._resolution_target = resolution_target
            self._resolution_level_function = resolution_level_function
            self._resolution_augmentation = resolution_augmentation
            self._resolution_face_function = resolution_face_function
            self._resolution_degeneracy_function = resolution_degeneracy_function
            self._resolution_length = resolution_length
            self._resolution_model = resolution_model
            self._resolution_generating_set = resolution_generating_set
            self._resolution_generator_morphism = resolution_generator_morphism
            self._resolution_relation_source = resolution_relation_source
            self._resolution_relations = resolution_relations
            # A cofiber is data in a selected stable enhancement, not a property
            # inferred from the augmentation or from the truncation length.
            self._resolution_cofiber_data = resolution_cofiber_data
            super().__init__(**rest)

        def resolution_category(self) -> Category:
            return self.category()

        def base_category(self) -> Category:
            return self.resolution_category().base_category()

        def projective_class(self) -> Category:
            return self.resolution_category().projective_class()

        def level_category(self) -> Category:
            return self.resolution_category().level_category()

        def truncation(self):
            return self.resolution_category().truncation()

        def target(self):
            return self._resolution_target

        resolved_object = target

        def level(self, degree: int):
            degree = int(degree)
            match 0 <= degree <= self.truncation():
                case False:
                    raise ValueError(
                        f"{self} is chosen only through resolution degree "
                        f"{self.truncation()}, so degree {degree} is not part of its datum"
                    )
                case True:
                    return self._resolution_level_function(degree)

        term = level

        def augmentation(self):
            return self._resolution_augmentation

        def cofiber_data(self):
            r"""Return explicitly selected cofiber-sequence data, when supplied.

            The resolution category does not manufacture a derived/stable
            enhancement for an arbitrary base category. In particular, a
            nonzero cofiber is valid resolution data: vanishing is an optional
            condition imposed by a specialization, not an admission criterion
            of the common owner.
            """
            match self._resolution_cofiber_data:
                case None:
                    raise TypeError(
                        f"{self} has no selected cofiber data; choose a stable enhancement "
                        "and supply its cofiber sequence explicitly"
                    )
                case data:
                    return data

        def generating_set(self):
            r"""Return the selected generator labels carried by degree-zero data."""
            selected = self._resolution_generating_set
            match selected:
                case None:
                    raise TypeError(
                        f"{self} carries no selected generator indexing set"
                    )
                case _:
                    return selected

        def generator_morphism(self):
            r"""Return the selected map from generator labels to the target."""
            selected = self._resolution_generator_morphism
            match selected:
                case None:
                    raise TypeError(
                        f"{self} carries no selected map from generator labels"
                    )
                case _:
                    return selected

        def generator(self, label):
            labels = self.generating_set()
            match label in labels:
                case False:
                    raise ValueError(
                        f"{label!r} is not a selected generator label of {self.target()}; "
                        f"the labels are {labels}"
                    )
                case True:
                    return self.generator_morphism()(labels(label))

        @cached_method
        def generators(self, *, name):
            from sage_extensions.categories.sets.indexed_families import (
                indexed_family,
            )

            return indexed_family(
                self.generating_set(),
                self.generator,
                name=name,
            )

        def generator_count(self):
            return self.generating_set().cardinality()

        def relation_source(self):
            selected = self._resolution_relation_source
            match selected:
                case None:
                    raise TypeError(f"{self} carries no selected relation source")
                case _:
                    return selected

        def relations(self):
            selected = self._resolution_relations
            match selected:
                case None:
                    raise TypeError(f"{self} carries no selected relation family")
                case _:
                    return selected

        def length(self):
            r"""Return the resolution length, independently of truncation."""
            return self._resolution_length

        resolution_length = length

        def model(self) -> str:
            return self._resolution_model

        def face(self, degree: int, index: int):
            degree = int(degree)
            index = int(index)
            match 1 <= degree <= self.truncation():
                case False:
                    raise ValueError(
                        f"faces of {self} occur in represented degrees 1 through "
                        f"{self.truncation()}, but degree {degree} was requested"
                    )
                case True:
                    pass
            match 0 <= index <= degree:
                case False:
                    raise ValueError(
                        f"a degree-{degree} simplicial object has faces indexed 0 through "
                        f"{degree}, but index {index} was requested"
                    )
                case True:
                    pass
            match self._resolution_face_function:
                case None:
                    raise TypeError(
                        f"{self} is represented by the {self.model()} model, not by explicit "
                        "simplicial face maps"
                    )
                case face_function:
                    return face_function(degree, index)

        def degeneracy(self, degree: int, index: int):
            degree = int(degree)
            index = int(index)
            match 0 <= degree < self.truncation():
                case False:
                    raise ValueError(
                        f"degeneracies of {self} occur in degrees 0 through "
                        f"{self.truncation() - 1}, but degree {degree} was requested"
                    )
                case True:
                    pass
            match 0 <= index <= degree:
                case False:
                    raise ValueError(
                        f"a degree-{degree} simplicial object has degeneracies indexed 0 "
                        f"through {degree}, but index {index} was requested"
                    )
                case True:
                    pass
            match self._resolution_degeneracy_function:
                case None:
                    raise TypeError(
                        f"{self} is represented by the {self.model()} model, not by explicit "
                        "simplicial degeneracies"
                    )
                case degeneracy_function:
                    return degeneracy_function(degree, index)

        def is_acyclic_through_truncation(self) -> bool:
            r"""The exactness asserted by these partial resolution data.

            In a finite truncation the last chosen level has unresolved
            higher relations. In particular, a selected presentation
            asserts its degree-zero coequalizer, not vanishing of degree-one
            homotopy. Resolution length is an independent datum.
            """
            return True

        def _validate_resolution_morphism_to(
            self,
            target,
            target_morphism,
            component_function,
        ) -> None:
            match self.truncation():
                case _ if self.truncation() is omega0:
                    # As for a natural transformation on an infinite source
                    # category, the component family is theorem-backed data:
                    # there is no finite admission loop that can establish all
                    # simplicial identities.  Individual components remain
                    # owned morphisms when accessed.
                    return
                case _:
                    pass
            base = self.base_category()
            for degree in range(self.truncation() + 1):
                component = component_function(degree)
                match _category_accepts_morphism(
                    base,
                    self.level(degree),
                    target.level(degree),
                    component,
                ):
                    case False:
                        raise TypeError(
                            f"degree {degree} of a resolution morphism {self} -> {target} "
                            f"must be a morphism {self.level(degree)} -> "
                            f"{target.level(degree)} of {base}, but it is {component}"
                        )
                    case True:
                        pass
            match (
                target.augmentation() * component_function(0)
                == target_morphism * self.augmentation()
            ):
                case False:
                    raise ValueError(
                        f"the degree-zero component of a resolution morphism {self} -> "
                        f"{target} does not commute with the augmentations"
                    )
                case True:
                    pass
            for degree in range(1, self.truncation() + 1):
                for index in range(degree + 1):
                    match target.face(degree, index) * component_function(
                        degree
                    ) == component_function(degree - 1) * self.face(degree, index):
                        case False:
                            raise ValueError(
                                f"the resolution morphism {self} -> {target} does not commute "
                                f"with face {index} in degree {degree}"
                            )
                        case True:
                            pass
            for degree in range(self.truncation()):
                for index in range(degree + 1):
                    match target.degeneracy(degree, index) * component_function(
                        degree
                    ) == component_function(degree + 1) * self.degeneracy(
                        degree, index
                    ):
                        case False:
                            raise ValueError(
                                f"the resolution morphism {self} -> {target} does not commute "
                                f"with degeneracy {index} in degree {degree}"
                            )
                        case True:
                            pass


__all__ = [
    "ResolutionMorphism",
    "Resolutions",
]
