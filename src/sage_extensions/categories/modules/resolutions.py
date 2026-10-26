r"""Chosen truncated projective resolutions of modules.

For modules the common resolution classifier is represented by augmented chain
complexes.  A truncation through degree n contains projective terms P_0,...,P_n,
an epimorphism P_0 -> M, and is exact at P_i for i < n.  No injectivity is
required at P_n: that would confuse a truncation with a resolution whose actual
length is n.
"""

from __future__ import annotations

from collections.abc import Mapping

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method
from sage.misc.unknown import Unknown
from sage_extensions.categories.sets.cardinals import omega0

from sage_extensions.categories.abstract_categories.mor_categories import (
    _category_accepts_morphism,
)
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
)
from sage_extensions.categories.abstract_categories.resolutions import (
    ResolutionMorCategoryConstruction,
    Resolutions,
    _ResolutionTargetFunctor,
)
from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedFreeModules,
    FreeResolution,
    Modules,
    _module_subobjects_agree,
)
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing, _owned_ring
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.owned_category import _object_of


def _degree_function(values, *, name: str):
    match values:
        case Mapping():
            return values.__getitem__
        case _ if callable(values):
            return values
        case _:
            raise TypeError(
                f"{name} must be supplied as a mapping by degree or as a callable"
            )


class ModuleResolutions(OwnedCategory):
    r"""The Dold--Kan chain-complex realization of one module resolution category.

    This category stores the exact simplicial resolution category whose
    Dold--Kan image it represents.  It is not declared as a subcategory of that
    category: a normalized chain complex and its simplicial preimage are
    equivalent resolution data, not literally the same object.
    """

    _MorCategory = ResolutionMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, simplicial_resolution_category):
        return Category.__classcall__(cls, simplicial_resolution_category)

    def __init__(self, simplicial_resolution_category) -> None:
        match simplicial_resolution_category:
            case Resolutions():
                pass
            case _:
                raise TypeError(
                    f"a module Dold--Kan realization needs a simplicial resolution category, "
                    f"but got {simplicial_resolution_category}"
                )
        base = simplicial_resolution_category.base_category()
        match base:
            case Modules():
                pass
            case _:
                raise TypeError(
                    f"Dold--Kan module resolutions need a resolution category over modules, "
                    f"but {simplicial_resolution_category} is over {base}"
                )
        self._simplicial_resolution_category = simplicial_resolution_category
        self._base_ring = _owned_ring(base.base_ring())
        super().__init__()

    def simplicial_resolution_category(self):
        r"""Return the common simplicial resolution category represented here."""
        return self._simplicial_resolution_category

    dold_kan_source_category = simplicial_resolution_category

    def ring(self):
        return self._base_ring

    base_ring = ring

    def base_category(self):
        return self.simplicial_resolution_category().base_category()

    def projective_class(self):
        return self.simplicial_resolution_category().projective_class()

    def level_category(self):
        return self.simplicial_resolution_category().level_category()

    def truncation(self):
        return self.simplicial_resolution_category().truncation()

    def super_categories(self):
        return [Objects()]

    def _repr_(self) -> str:
        return (
            f"Dold--Kan image of {self.simplicial_resolution_category()}"
        )

    def an_object(self):
        return self.constant(self.level_category().an_object())

    @cached_method
    def target_functor(self):
        return _ResolutionTargetFunctor(self)

    def degree_zero(self, augmentation, *, length=Unknown):
        r"""Return the chain-model truncation-zero resolution of a surjective map."""
        match self.truncation():
            case 0:
                pass
            case _:
                raise ValueError(
                    f"a single augmentation supplies truncation zero, but {self} has "
                    f"truncation {self.truncation()}"
                )
        return self.chain(
            augmentation.codomain(),
            {0: augmentation.domain()},
            {},
            augmentation,
            length=length,
        )

    def constant(self, projective_object):
        r"""Return the length-zero chain resolution of a selected projective object."""
        match projective_object in self.level_category():
            case False:
                raise TypeError(
                    f"a constant resolution in {self} needs degree zero in "
                    f"{self.level_category()}, but {projective_object} is not one"
                )
            case True:
                pass
        zero = self.base_ring().free_module(0)

        def term(degree):
            match int(degree):
                case 0:
                    return projective_object
                case _:
                    return zero

        def differential(degree):
            source = term(degree)
            target = term(int(degree) - 1)
            return source.module_category().Mor(source, target).zero()

        identity = projective_object.module_category().Mor(
            projective_object, projective_object
        ).identity()
        match self.truncation():
            case _ if self.truncation() is omega0:
                return _object_of(
                    self,
                    resolution_target=projective_object,
                    resolution_level_function=term,
                    resolution_augmentation=identity,
                    resolution_length=0,
                    resolution_model="chain",
                    module_differential_function=differential,
                )
            case _:
                pass
        return self.chain(
            projective_object,
            term,
            differential,
            identity,
            length=0,
        )

    def selected_constant(
        self,
        projective_object,
        *,
        generating_set,
        generator_morphism,
    ):
        r"""Retain a selected finite basis as the length-zero truncation-one resolution."""
        match self.truncation():
            case 1:
                pass
            case _:
                raise ValueError(
                    f"a selected finite basis supplies the canonical truncation-one presentation, "
                    f"but {self} has truncation {self.truncation()}"
                )
        match projective_object in self.level_category():
            case False:
                raise TypeError(
                    f"the selected basis object {projective_object} must lie in the finite-free "
                    f"level category {self.level_category()}"
                )
            case True:
                pass
        match generator_morphism.domain() is generating_set and generator_morphism.codomain() is projective_object:
            case False:
                raise ValueError(
                    f"the selected basis map of {projective_object} must be a map from "
                    f"{generating_set} to {projective_object}"
                )
            case True:
                pass
        zero = self.base_ring().free_module(0)
        ordinary_modules = OwnedCategoryOverBaseRing.__classcall__(Modules, self.base_ring())
        identity = ordinary_modules.Mor(
            projective_object, projective_object
        ).identity()

        def term(degree):
            match int(degree):
                case 0:
                    return projective_object
                case 1:
                    return zero
                case _:
                    raise ValueError(
                        f"the canonical finite presentation of {projective_object} is represented only in degrees 0 and 1"
                    )

        def differential(degree):
            match int(degree):
                case 1:
                    return ordinary_modules.Mor(zero, projective_object).zero()
                case _:
                    raise ValueError(
                        f"the canonical finite presentation of {projective_object} has only the degree-one differential"
                    )

        return _object_of(
            self,
            resolution_target=projective_object,
            resolution_level_function=term,
            resolution_augmentation=identity,
            resolution_length=0,
            resolution_model="selected-basis",
            module_differential_function=differential,
            resolution_generating_set=generating_set,
            resolution_generator_morphism=generator_morphism,
        )

    def chain(
        self,
        target,
        terms,
        differentials,
        augmentation,
        *,
        length=Unknown,
    ):
        r"""Build an admitted augmented chain complex through this truncation."""
        match self.truncation():
            case _ if self.truncation() is omega0:
                raise ValueError(
                    "an arbitrary infinite chain resolution cannot be admitted by finite "
                    "source checks; use a theorem-backed infinite construction"
                )
            case _:
                pass
        term = _degree_function(terms, name="resolution terms")
        differential = _degree_function(
            differentials, name="resolution differentials"
        )
        base = self.base_category()
        match target in base:
            case False:
                raise TypeError(
                    f"a module resolution over {self.base_ring()} must resolve a module over "
                    f"{self.base_ring()}, but {target} is not an object of {base}"
                )
            case True:
                pass
        for degree in range(self.truncation() + 1):
            match term(degree) in self.level_category():
                case False:
                    raise TypeError(
                        f"degree {degree} of a resolution in {self} must lie in "
                        f"{self.level_category()}, but it is {term(degree)}"
                    )
                case True:
                    pass
        match _category_accepts_morphism(
            base,
            term(0),
            target,
            augmentation,
        ):
            case False:
                raise TypeError(
                    f"the augmentation of a module resolution in {self} must be a morphism "
                    f"{term(0)} -> {target}, but it is {augmentation}"
                )
            case True:
                pass
        match augmentation.is_surjective():
            case False:
                raise ValueError(
                    f"the augmentation of a module resolution must be surjective, but "
                    f"{augmentation} is not"
                )
            case True:
                pass
        for degree in range(1, self.truncation() + 1):
            arrow = differential(degree)
            match _category_accepts_morphism(
                base,
                term(degree),
                term(degree - 1),
                arrow,
            ):
                case False:
                    raise TypeError(
                        f"d_{degree} of a module resolution must be a morphism "
                        f"{term(degree)} -> {term(degree - 1)}, but it is {arrow}"
                    )
                case True:
                    pass
        match self.truncation():
            case 0:
                pass
            case _:
                match (
                    augmentation * differential(1)
                    == term(1).module_category().Mor(
                        term(1), target
                    ).zero()
                ):
                    case False:
                        raise ValueError(
                            f"the augmented chain condition fails: {augmentation} composed with "
                            f"d_1={differential(1)} is not zero"
                        )
                    case True:
                        pass
        for degree in range(2, self.truncation() + 1):
            match (
                differential(degree - 1) * differential(degree)
                == term(degree).module_category().Mor(
                    term(degree), term(degree - 2)
                ).zero()
            ):
                case False:
                    raise ValueError(
                        f"the chain condition fails in degree {degree}: "
                        f"d_{degree - 1} d_{degree} is not zero"
                    )
                case True:
                    pass
        for degree in range(self.truncation()):
            incoming = differential(degree + 1)
            match degree:
                case 0:
                    outgoing = augmentation
                    outgoing_name = "augmentation"
                case _:
                    outgoing = differential(degree)
                    outgoing_name = f"d_{degree}"
            match _module_subobjects_agree(
                incoming.image(),
                outgoing.kernel(),
                term(degree),
            ):
                case False:
                    raise ValueError(
                        f"the augmented complex is not exact at degree {degree}: "
                        f"im(d_{degree + 1}) is not ker({outgoing_name})"
                    )
                case True:
                    pass
        match length:
            case _ if length is Unknown or length is omega0:
                pass
            case _:
                finite_length = int(length)
                match finite_length < 0:
                    case True:
                        raise ValueError(
                            f"a finite resolution length is nonnegative, but got {length}"
                        )
                    case False:
                        pass
                match finite_length <= self.truncation():
                    case False:
                        pass
                    case True:
                        match finite_length:
                            case 0:
                                match augmentation.is_injective():
                                    case False:
                                        raise ValueError(
                                            f"{augmentation} is not an isomorphism, so this resolution "
                                            "does not have length zero"
                                        )
                                    case True:
                                        pass
                            case _:
                                match differential(finite_length).is_injective():
                                    case False:
                                        raise ValueError(
                                            f"d_{finite_length} is not injective, so the represented "
                                            f"resolution does not terminate in degree {finite_length}"
                                        )
                                    case True:
                                        pass
                        for degree in range(finite_length + 1, self.truncation() + 1):
                            match term(degree).is_zero():
                                case False:
                                    raise ValueError(
                                        f"{self} was declared to have length {finite_length}, but its "
                                        f"degree-{degree} term {term(degree)} is nonzero"
                                    )
                                case True:
                                    pass
        return _object_of(
            self,
            resolution_target=target,
            resolution_level_function=term,
            resolution_augmentation=augmentation,
            resolution_length=length,
            resolution_model="chain",
            module_differential_function=differential,
        )

    def selected_presentation(
        self,
        target,
        presentation,
        augmentation,
        *,
        generating_set,
        generator_morphism,
    ):
        r"""Retain a constructor-selected finite presentation as truncation one.

        The quotient constructor already knows that ``target`` is the cokernel
        of ``presentation``.  This entry therefore records that chosen exact
        datum without asking the generic ``chain`` constructor to recompute its
        exactness.  The degree-zero generator data are retained on the same
        resolution object, so there is no second framing record beside it.
        """
        match self.truncation():
            case 1:
                pass
            case _:
                raise ValueError(
                    f"a selected finite presentation supplies truncation one, but {self} has "
                    f"truncation {self.truncation()}"
                )
        degree_one = presentation.domain()
        degree_zero = presentation.codomain()
        for degree, term in ((0, degree_zero), (1, degree_one)):
            match term in self.level_category():
                case False:
                    raise TypeError(
                        f"degree {degree} of a selected presentation in {self} must lie in "
                        f"{self.level_category()}, but it is {term}"
                    )
                case True:
                    pass
        base = self.base_category()
        match _category_accepts_morphism(base, degree_zero, target, augmentation):
            case False:
                raise TypeError(
                    f"the augmentation of a selected presentation in {self} must be a morphism "
                    f"{degree_zero} -> {target}, but it is {augmentation}"
                )
            case True:
                pass
        match _category_accepts_morphism(base, degree_one, degree_zero, presentation):
            case False:
                raise TypeError(
                    f"the relation map of a selected presentation in {self} must be a morphism "
                    f"{degree_one} -> {degree_zero}, but it is {presentation}"
                )
            case True:
                pass
        match generator_morphism.domain() is generating_set and generator_morphism.codomain() is target:
            case False:
                raise ValueError(
                    f"the selected generator map of {target} must be a map from "
                    f"{generating_set} to {target}"
                )
            case True:
                pass

        def term(degree):
            match int(degree):
                case 0:
                    return degree_zero
                case 1:
                    return degree_one
                case _:
                    raise ValueError(
                        f"a selected finite presentation in {self} has represented terms only in degrees 0 and 1"
                    )

        def differential(degree):
            match int(degree):
                case 1:
                    return presentation
                case _:
                    raise ValueError(
                        f"a selected finite presentation in {self} has only the degree-one differential"
                    )

        return _object_of(
            self,
            resolution_target=target,
            resolution_level_function=term,
            resolution_augmentation=augmentation,
            resolution_length=Unknown,
            resolution_model="selected-presentation",
            module_differential_function=differential,
            resolution_generating_set=generating_set,
            resolution_generator_morphism=generator_morphism,
        )

    def from_selected_presentation(self, module):
        r"""The degree-one partial free resolution selected by a presentation."""
        match self.truncation():
            case 1:
                pass
            case _:
                raise ValueError(
                    f"a selected finite presentation supplies truncation one, but {self} has "
                    f"truncation {self.truncation()}"
                )
        match module.has_selected_module_resolution():
            case False:
                raise TypeError(
                    f"{module} has no selected finite module presentation over "
                    f"{self.base_ring()}"
                )
            case True:
                pass
        selected = module.selected_module_resolution()
        match selected.resolution_category() is self:
            case False:
                raise TypeError(
                    f"the selected resolution of {module} lies in {selected.resolution_category()}, "
                    f"not in the finite-presentation classifier {self}"
                )
            case True:
                return selected

    def from_selected_generators(self, module):
        r"""The degree-zero partial free resolution selected by a framing."""
        match self.truncation():
            case 0:
                pass
            case _:
                raise ValueError(
                    f"a chosen generating epimorphism supplies truncation zero, but {self} has "
                    f"truncation {self.truncation()}"
                )
        match module.has_selected_module_resolution():
            case False:
                raise TypeError(
                    f"{module} has no selected module generating set over {self.base_ring()}"
                )
            case True:
                return self.degree_zero(module.framing_morphism())

    def from_free_resolution(self, resolution: FreeResolution):
        r"""Place an existing selected free resolution in this classifier."""
        match resolution.module().base_ring() is self.base_ring():
            case False:
                raise ValueError(
                    f"{resolution} resolves a module over {resolution.module().base_ring()}, "
                    f"not over {self.base_ring()}"
                )
            case True:
                pass
        match resolution.is_exact():
            case False:
                raise ValueError(
                    f"{resolution} is not exact, so it cannot define an object of {self}"
                )
            case True:
                pass
        return self.chain(
            resolution.module(),
            resolution.term,
            resolution.differential,
            resolution.augmentation(),
            length=resolution.length(),
        )

    def canonical_simplicial_resolution(self, module):
        r"""Return the common simplicial bar resolution represented before Dold--Kan."""
        from sage_extensions.categories.sets.set_categories import Sets

        adjunction = Sets().free_module_adjunction(self.base_ring())
        return self.simplicial_resolution_category().comonadic(adjunction, module)

    class ParentMethods:
        def __init__(
            self,
            resolution_target,
            resolution_level_function,
            resolution_augmentation,
            resolution_length=Unknown,
            resolution_model="chain",
            module_differential_function=None,
            resolution_generating_set=None,
            resolution_generator_morphism=None,
            **rest,
        ) -> None:
            self._resolution_target = resolution_target
            self._resolution_level_function = resolution_level_function
            self._resolution_augmentation = resolution_augmentation
            self._resolution_length = resolution_length
            self._resolution_model = resolution_model
            self._module_differential_function = module_differential_function
            self._resolution_generating_set = resolution_generating_set
            self._resolution_generator_morphism = resolution_generator_morphism
            super().__init__(**rest)

        def resolution_category(self):
            return self.category()

        def base_category(self):
            return self.resolution_category().base_category()

        def projective_class(self):
            return self.resolution_category().projective_class()

        def level_category(self):
            return self.resolution_category().level_category()

        def truncation(self):
            return self.resolution_category().truncation()

        def target(self):
            return self._resolution_target

        resolved_object = target

        def level(self, degree):
            degree = int(degree)
            match 0 <= degree <= self.truncation():
                case False:
                    raise ValueError(
                        f"{self} is chosen only through degree {self.truncation()}, "
                        f"so degree {degree} is not represented"
                    )
                case True:
                    return self._resolution_level_function(degree)

        term = level

        def augmentation(self):
            return self._resolution_augmentation

        def generating_set(self):
            selected = self._resolution_generating_set
            match selected:
                case None:
                    raise TypeError(f"{self} carries no selected generator indexing set")
                case _:
                    return selected

        def generator_morphism(self):
            selected = self._resolution_generator_morphism
            match selected:
                case None:
                    raise TypeError(f"{self} carries no selected map from generator labels")
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
            return indexed_family(
                self.generating_set(),
                self.generator,
                name=name,
            )

        def generator_count(self):
            return self.generating_set().cardinality()

        def length(self):
            return self._resolution_length

        resolution_length = length

        def model(self):
            return self._resolution_model

        def differential(self, degree: int):
            degree = int(degree)
            match 1 <= degree <= self.truncation():
                case False:
                    raise ValueError(
                        f"the chosen chain truncation {self} has differentials in "
                        f"degrees 1 through {self.truncation()}, but d_{degree} was requested"
                    )
                case True:
                    return self._module_differential_function(degree)

        def is_acyclic_through_truncation(self) -> bool:
            return True

        def _validate_resolution_morphism_to(
            self,
            target,
            target_morphism,
            component_function,
        ) -> None:
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
                            f"degree {degree} of a chain-resolution morphism must be a morphism "
                            f"{self.level(degree)} -> {target.level(degree)}, but it is {component}"
                        )
                    case True:
                        pass
            match (
                target.augmentation() * component_function(0)
                == target_morphism * self.augmentation()
            ):
                case False:
                    raise ValueError(
                        f"the degree-zero component of a resolution morphism {self} -> {target} "
                        "does not commute with the augmentations"
                    )
                case True:
                    pass
            for degree in range(1, self.truncation() + 1):
                match (
                    target.differential(degree) * component_function(degree)
                    == component_function(degree - 1)
                    * self.differential(degree)
                ):
                    case False:
                        raise ValueError(
                            f"the resolution morphism {self} -> {target} is not a chain map in "
                            f"degree {degree}"
                        )
                    case True:
                        pass


def finitely_generated_resolution_category(base_ring):
    r"""The chosen finite-free degree-zero classifier whose image is finite generation."""
    from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing

    ring = _owned_ring(base_ring)
    ordinary = OwnedCategoryOverBaseRing.__classcall__(Modules, ring)
    return Resolutions(
        ordinary,
        ordinary.Projective(),
        0,
        FinitelyGeneratedFreeModules(ring),
    ).dold_kan_image()


def finitely_presented_resolution_category(base_ring):
    r"""The chosen finite-free degree-one classifier whose image is finite presentation."""
    from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing

    ring = _owned_ring(base_ring)
    ordinary = OwnedCategoryOverBaseRing.__classcall__(Modules, ring)
    return Resolutions(
        ordinary,
        ordinary.Projective(),
        1,
        FinitelyGeneratedFreeModules(ring),
    ).dold_kan_image()


__all__ = [
    "ModuleResolutions",
    "finitely_generated_resolution_category",
    "finitely_presented_resolution_category",
]
