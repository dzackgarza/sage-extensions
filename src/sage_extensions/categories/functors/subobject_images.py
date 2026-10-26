r"""Direct and inverse image on fixed-ambient module subobject categories."""

from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.modules.pure.modules import Modules


def _inverse_image_subobject(morphism, subobject):
    r"""Construct the pullback/preimage as the source image of ``ker(f,-i)``."""
    if subobject.inclusion().codomain() is not morphism.codomain():
        raise ValueError(
            f"the preimage f^-1(A) needs A to be a subobject of the codomain {morphism.codomain()} of "
            f"f = {morphism}, but {subobject} is a subobject of {subobject.inclusion().codomain()}"
        )

    direct_sum = Modules(morphism.domain().base_ring()).biproduct(
        (morphism.domain(), subobject)
    )
    difference = direct_sum.from_summands(morphism, -subobject.inclusion())
    kernel = difference.kernel()
    return (direct_sum.left_projection() * kernel.inclusion()).image()


class _DirectImageSubobjectFunctor(Functor):
    r"""The monotone map ``f_* : Sub(M) -> Sub(N)``."""

    def __init__(self, morphism) -> None:
        self._morphism = morphism
        super().__init__(
            morphism.domain().category().Subobjects(morphism.domain()),
            morphism.codomain().category().Subobjects(morphism.codomain()),
        )

    def morphism(self):
        return self._morphism

    def _apply_object(self, subobject):
        return (self.morphism() * subobject.inclusion()).image()

    def _repr_(self):
        return f"Direct image f_* on subobjects along {self.morphism()}"

    def _apply_morphism(self, order_morphism):
        return self.codomain().Mor(
            self(order_morphism.domain()),
            self(order_morphism.codomain()),
        ).canonical_morphism()


class _InverseImageSubobjectFunctor(Functor):
    r"""The monotone map ``f^{-1} : Sub(N) -> Sub(M)``."""

    def __init__(self, morphism) -> None:
        self._morphism = morphism
        super().__init__(
            morphism.codomain().category().Subobjects(morphism.codomain()),
            morphism.domain().category().Subobjects(morphism.domain()),
        )

    def morphism(self):
        return self._morphism

    def _apply_object(self, subobject):
        return _inverse_image_subobject(self.morphism(), subobject)

    def _repr_(self):
        return f"Inverse image f^(-1) on subobjects along {self.morphism()}"

    def _apply_morphism(self, order_morphism):
        return self.codomain().Mor(
            self(order_morphism.domain()),
            self(order_morphism.codomain()),
        ).canonical_morphism()


class _SubobjectImageAdjunction(Adjunction):
    r"""The Galois connection ``f_* ⊣ f^{-1}`` on fixed-ambient subobjects."""

    def __init__(self, morphism) -> None:
        self._morphism = morphism
        super().__init__(
            _DirectImageSubobjectFunctor(morphism),
            _InverseImageSubobjectFunctor(morphism),
        )


    def _repr_(self):
        return f"Galois connection f_* ⊣ f^(-1) along {self._morphism}"

    def _unit_component(self, subobject):
        target = self.right_adjoint()(self.left_adjoint()(subobject))
        return self.left_adjoint().domain().Mor(subobject, target).canonical_morphism()

    def _counit_component(self, subobject):
        source = self.left_adjoint()(self.right_adjoint()(subobject))
        return self.left_adjoint().codomain().Mor(source, subobject).canonical_morphism()


__all__ = []
