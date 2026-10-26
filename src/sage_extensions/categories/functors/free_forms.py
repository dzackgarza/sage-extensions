r"""Free bilinear/quadratic formed objects and their forgetful adjunctions."""

from sage.misc.cachefunc import cached_function
from sage.misc.abstract_method import abstract_method

from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.modules.framed.formed.form_modules import (
    BilinearFormModules,
    FormModules,
    QuadraticFormModules,
    _represented_value_module,
    _value_as_module_element,
)
from sage_extensions.categories.modules.pure.modules import BilinearMap, FinitelyPresentedModules, Modules

from sage_extensions.categories.rings.ring_foundation import _owned_ring


class _UnderlyingFormModuleFunctor(Functor):
    r"""Forget the selected form while retaining the module object itself."""

    def _apply_object(self, formed):
        return formed

    def _apply_morphism(self, morphism):
        r"""Forget the form from an arrow of the formed-module domain."""
        module_map = morphism.module_morphism()
        ordinary = Modules(morphism.domain().base_ring()).Mor(
            morphism.domain(), morphism.codomain()
        )
        if module_map.parent() is ordinary:
            return module_map
        return ordinary._from_constructed_element_map(
            module_map, premises=(module_map,)
        )


class _ForgetTheFormFunctor(_UnderlyingFormModuleFunctor):
    r"""Forget the selected form from one represented formed-module category."""

    def __init__(self, base_ring, formed_category) -> None:
        ring = _owned_ring(base_ring)

        super().__init__(formed_category, Modules(ring))


class _BilinearUnderlyingModuleFunctor(_UnderlyingFormModuleFunctor):
    def __init__(self, base_ring) -> None:
        ring = _owned_ring(base_ring)
        self._base_ring = ring
        super().__init__(
            BilinearFormModules(ring).FinitelyPresented(),
            FinitelyPresentedModules(ring),
        )

    def base_ring(self):
        return self._base_ring

    def _repr_(self):
        return f"Underlying-module functor on bilinear formed {self.base_ring()}-modules"


class _QuadraticUnderlyingModuleFunctor(_UnderlyingFormModuleFunctor):
    def __init__(self, base_ring) -> None:
        ring = _owned_ring(base_ring)
        self._base_ring = ring
        super().__init__(
            QuadraticFormModules(ring).FinitelyPresented(),
            FinitelyPresentedModules(ring),
        )

    def base_ring(self):
        return self._base_ring

    def _repr_(self):
        return f"Underlying-module functor on quadratic formed {self.base_ring()}-modules"


class _FreeBilinearFormFunctor(Functor):
    r"""Send ``M`` to ``(M, M tensor M, universal pure tensor)``."""

    def __init__(self, base_ring) -> None:
        ring = _owned_ring(base_ring)
        self._base_ring = ring
        super().__init__(
            FinitelyPresentedModules(ring),
            BilinearFormModules(ring).FinitelyPresented(),
        )

    def base_ring(self):
        return self._base_ring

    def _repr_(self):
        return f"Free bilinear-form functor on {self.base_ring()}-modules"

    def _apply_object(self, module):

        classifier = Modules(self.base_ring()).tensor_product((module, module))
        formed = FormModules(module.base_ring())(
            module.bilinear_forms(classifier)(
                lambda left, right: classifier.pure_tensor(left, right)
            )
        )
        return formed

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        module_map = _read_between_free_formed(morphism, source, target)
        value_map = morphism.tensor_product_map(
            morphism,
            source=source.value_module(),
            target=target.value_module(),
        )
        return source.Mor(target)((module_map, value_map))


class _FreeQuadraticFormFunctor(Functor):
    r"""Send ``M`` to ``(M, Gamma^2(M), gamma_2)``."""

    def __init__(self, base_ring) -> None:
        ring = _owned_ring(base_ring)
        self._base_ring = ring
        super().__init__(
            FinitelyPresentedModules(ring),
            QuadraticFormModules(ring).FinitelyPresented(),
        )

    def base_ring(self):
        return self._base_ring

    def _repr_(self):
        return f"Free quadratic-form functor on {self.base_ring()}-modules"

    def _apply_object(self, module):

        classifier = module.divided_square()
        formed = FormModules(module.base_ring())(
            module.quadratic_map(classifier, classifier.quadratic)
        )
        return formed

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        module_map = _read_between_free_formed(morphism, source, target)
        value_map = morphism.divided_square()
        return source.Mor(target)((module_map, value_map))


class _TautologicalFormFunctor(Functor):
    r"""Abstract base for a free form classified by a functorial square."""

    @abstract_method
    def _classifying_square(self, module):
        ...


def _read_between_free_formed(morphism, source, target):
    r"""``F(f)`` on the free formed objects: ``f`` read between the copies built on its endpoints.

    ``source`` and ``target`` are built on the data of ``f``'s domain and
    codomain, so the generator of ``source`` labelled ``l`` is the generator
    of the domain labelled ``l``, and its image reads in ``target`` by
    coercion.
    """
    domain = morphism.domain()
    return source.module_category().Mor(source, target)(
        lambda label: target(morphism(domain.module_generator(label)))
    )


class _FreeFormAdjunction(Adjunction):
    def _repr_(self):
        return f"{self.left_adjoint()} ⊣ {self.right_adjoint()}"

    def _unit_component(self, module):
        r"""``M -> U(F(M))``: the generator of ``M`` labelled ``l`` to the generator of ``F(M)`` labelled ``l``."""
        free_formed = self.left_adjoint()(module)
        return module.module_category().Mor(module, free_formed)(
            free_formed.module_generator
        )

    @abstract_method
    def _counit_value_map(self, free_formed, formed):
        ...

    def _counit_component(self, formed):
        r"""``F(U(N)) -> N``: the identity of the module ``N`` is built on, read between the two formed objects."""
        free_formed = self.left_adjoint()(self.right_adjoint()(formed))
        module_map = free_formed.module_category().Mor(free_formed, formed)(
            formed.module_generator
        )
        return free_formed.Mor(formed)(
            (
                module_map,
                self._counit_value_map(free_formed, formed),
            )
        )


class _BilinearFreeFormAdjunction(_FreeFormAdjunction):
    r"""The tautological bilinear-form classifier adjunction."""

    def __init__(self, base_ring) -> None:
        super().__init__(
            _FreeBilinearFormFunctor(base_ring),
            _BilinearUnderlyingModuleFunctor(base_ring),
        )

    def _counit_value_map(self, free_formed, formed):
        module = self.right_adjoint()(formed)
        target_values = _represented_value_module(formed)
        bilinear = BilinearMap(
            module,
            module,
            target_values,
            lambda left_label, right_label: _value_as_module_element(
                formed,
                formed.b(
                    module.module_generator(left_label),
                    module.module_generator(right_label),
                ),
            ),
        )
        return bilinear


class _QuadraticFreeFormAdjunction(_FreeFormAdjunction):
    r"""The divided-square quadratic-form classifier adjunction."""

    def __init__(self, base_ring) -> None:
        super().__init__(
            _FreeQuadraticFormFunctor(base_ring),
            _QuadraticUnderlyingModuleFunctor(base_ring),
        )

    def _counit_value_map(self, free_formed, formed):
        self.right_adjoint()(formed)
        target_values = _represented_value_module(formed)
        return free_formed.value_module().from_quadratic(
            lambda element: _value_as_module_element(
                formed,
                formed.norm(element),
            ),
            target_values,
        )


@cached_function
def _bilinear_free_form_adjunction(base_ring) -> _BilinearFreeFormAdjunction:
    return _BilinearFreeFormAdjunction(base_ring)


@cached_function
def _quadratic_free_form_adjunction(base_ring) -> _QuadraticFreeFormAdjunction:
    return _QuadraticFreeFormAdjunction(base_ring)


__all__ = []
