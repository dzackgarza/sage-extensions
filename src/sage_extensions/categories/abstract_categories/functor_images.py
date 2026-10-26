r"""Presented images of a functor.

For ``F : C -> D`` an object of ``ImageOfFunctor(F)`` is a chosen presentation
``(X, F(X))``.  Two different ``X`` may therefore give distinct presented
objects even when ``F(X)`` is literally the same object of ``D``.  Morphisms
are the arrows of ``D`` between the underlying images, wrapped so their
endpoints are the presented objects.  The faithful forgetful functor to ``D``
forgets only the chosen presentation.
"""

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _category_accepts_morphism,
    _category_mor,
    _category_mor_parent,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class FunctorImageMorphism(CategoricalMor.ElementMethods):
    r"""Methods for a generated codomain arrow between chosen functor presentations."""

    def __init__(self, parent, underlying_arrow) -> None:
        Morphism.__init__(self, parent)
        self._underlying_arrow = underlying_arrow

    def underlying_arrow(self):
        return self._underlying_arrow

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        category = self.parent().image_category()
        return category.Mor(other.domain(), self.codomain())(
            self.underlying_arrow() * other.underlying_arrow()
        )


class FunctorImageMor(CategoricalMor):
    ElementMethods = FunctorImageMorphism

    def image_category(self):
        return self.base_category()

    def _underlying_mor(self):
        category = self.image_category().functor().codomain()
        return _category_mor(
            category,
            self.domain().underlying_image(),
            self.codomain().underlying_image(),
        )

    def codomain_mor_category(self):
        r"""Return the codomain Mor represented by this presentation Mor."""
        return self._underlying_mor()

    def _element_constructor_(self, arrow):
        match arrow:
            case FunctorImageMorphism():
                if arrow.parent() is self:
                    return arrow
                raise TypeError(f"{arrow} belongs to another Mor; apply the functor between the categories")
        if not _category_accepts_morphism(
            self.image_category().functor().codomain(),
            self.domain().underlying_image(),
            self.codomain().underlying_image(),
            arrow,
        ):
            raise ValueError(
                f"{arrow} is not a morphism {self.domain().underlying_image()} -> "
                f"{self.codomain().underlying_image()} in {self.image_category().functor().codomain()}"
            )
        return self.element_class(self, arrow)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        underlying = self.domain().underlying_image()
        category = self.image_category().functor().codomain()
        return self(_category_mor_parent(category, underlying, underlying).identity())

    def compose(self, second, first):
        r"""Compose two presented-image arrows through their codomain arrows."""
        if first.codomain() is not second.domain():
            raise ValueError(
                f"cannot compose {second} o {first}: {first} ends at {first.codomain()}, but {second} starts "
                f"at {second.domain()}"
            )
        if first.domain() is not self.domain() or second.codomain() is not self.codomain():
            raise ValueError(
                f"the composite {second} o {first} is a morphism {first.domain()} -> {second.codomain()}, not "
                f"a morphism {self.domain()} -> {self.codomain()}"
            )
        composite = second * first
        if composite.parent() is not self:
            return self(composite)
        return composite


class FunctorImageMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = FunctorImageMor


class ImageOfFunctor(OwnedCategory):
    r"""The category of outputs of one functor with a chosen source presentation."""

    _MorCategory = FunctorImageMorCategoryConstruction

    @staticmethod
    @cached_function(key=lambda cls, functor: (cls, id(functor)))
    def __classcall__(cls, functor):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(functor)
        return typecall(cls, functor)

    class ParentMethods:
        r"""``F(X)`` presented by its chosen preimage ``X``.

        The preimage is the defining datum; the image is ``F`` applied to it,
        which ``F`` computes once and returns as the same object each time.
        """

        def __init__(self, preimage, **rest) -> None:
            self._preimage = preimage
            super().__init__(**rest)

        def preimage(self):
            return self._preimage

        def underlying_image(self):
            return self.constructing_functor()(self.preimage())

        def constructing_functor(self):
            return self.category().functor()

        def _repr_(self) -> str:
            return f"{self.underlying_image()} presented as {self.constructing_functor()}({self.preimage()})"

    def __init__(self, functor) -> None:
        self._functor = functor
        super().__init__()

    def _make_named_class_key(self, name):
        return id(self._functor)

    def super_categories(self):
        return [Objects()]

    def functor(self):
        return self._functor

    def an_object(self):
        return self.object(self.functor().domain().an_object())

    @cached_method(key=lambda self, preimage: id(preimage))
    def object(self, preimage):
        r"""``F(X)`` presented by ``X``: this category's one entry, one object per preimage."""
        if preimage not in self.functor().domain():
            raise TypeError(
                f"the image F(X) under F = {self.functor()} needs X an object of {self.functor().domain()}, "
                f"but {preimage} is not one"
            )
        # The image is computed here, so a preimage the functor does not send
        # anywhere is refused at construction rather than when first read.
        self.functor()(preimage)
        return _object_of(self, preimage=preimage)

    def __call__(self, *args, **kwargs):
        return self.object(*args, **kwargs)

    def Mor(self, domain: Parent, codomain: Parent):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two of its objects, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    def identity(self, obj):
        return self.Mor(obj, obj).identity()

    @cached_method
    def inclusion(self):
        return FunctorImageForgetfulFunctor(self)

    def _repr_(self) -> str:
        return f"Category of chosen presentations in the image of {self.functor()}"


class FunctorImageForgetfulFunctor(Functor):
    r"""Forget a chosen preimage and retain the underlying codomain object."""

    _faithful = True

    def __init__(self, image_category: ImageOfFunctor) -> None:
        self._image_category = image_category
        super().__init__(image_category, image_category.functor().codomain())

    def image_category(self):
        return self._image_category

    def _apply_object(self, presented):
        return presented.underlying_image()

    def _apply_morphism(self, morphism):
        return morphism.underlying_arrow()


__all__ = [
    "FunctorImageForgetfulFunctor",
    "FunctorImageMor",
    "FunctorImageMorphism",
    "ImageOfFunctor",
]
