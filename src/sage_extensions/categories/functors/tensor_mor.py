r"""The tensor--internal-Mor adjunction on modules with chosen finite presentations."""

from sage_extensions.categories.functors.core import Adjunction, Functor

from sage_extensions.categories.modules.pure.modules import BilinearMap, ModulesWithChosenFinitePresentation

from sage_extensions.categories.rings.ring_foundation import _owned_ring


class _TensorByFunctor(Functor):
    r"""The endofunctor ``- tensor_R M`` on chosen finite presentations."""

    def __init__(self, fixed_module) -> None:
        self._fixed_module = fixed_module
        ring = _owned_ring(fixed_module.base_ring())
        category = ModulesWithChosenFinitePresentation(ring)
        if fixed_module not in category:
            raise TypeError(
                f"the functor - (x) M needs M to be finitely presented with chosen generators and relations, but "
                f"{fixed_module} is not"
            )
        super().__init__(category, category)

    def fixed_module(self):
        return self._fixed_module

    def _apply_object(self, module):
        return self.codomain().tensor_product((module, self.fixed_module()))

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        fixed = self.fixed_module()
        identity = fixed.module_category().Mor(fixed, fixed).identity()
        return morphism.tensor_product_map(identity, source=source, target=target)

    def _repr_(self):
        return f"- tensor {self.fixed_module()}"


class _InternalMorFromFunctor(Functor):
    r"""The endofunctor ``Hom_R(M,-)`` represented by internal Mor modules."""

    def __init__(self, fixed_source) -> None:
        self._fixed_source = fixed_source
        ring = _owned_ring(fixed_source.base_ring())
        category = ModulesWithChosenFinitePresentation(ring)
        if fixed_source not in category:
            raise TypeError(
                f"the internal Mor functor Mor(M, -) needs M to be finitely presented with chosen generators and relations, "
                f"but {fixed_source} is not"
            )
        super().__init__(category, category)

    def fixed_source(self):
        return self._fixed_source

    def _apply_object(self, module):
        source = self.fixed_source()
        return source.module_category().Mor(source, module)

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        fixed = self.fixed_source()
        identity = fixed.module_category().Mor(fixed, fixed).identity()
        return identity.internal_mor_map(morphism, source_internal_mor=source, target_internal_mor=target)

    def _repr_(self):
        return f"Internal Mor({self.fixed_source()}, -)"


class _TensorMorAdjunction(Adjunction):
    r"""The adjunction ``- tensor_R M ⊣ Hom_R(M,-)``."""

    def __init__(self, fixed_module) -> None:
        self._fixed_module = fixed_module
        super().__init__(
            _TensorByFunctor(fixed_module),
            _InternalMorFromFunctor(fixed_module),
        )

    def fixed_module(self):
        return self._fixed_module


    def _unit_component(self, module):
        tensor = self.left_adjoint()(module)
        internal_mor = self.right_adjoint()(tensor)
        fixed = self.fixed_module()
        return module.module_category().Mor(module, internal_mor)(
            lambda module_label: fixed.module_category().Mor(fixed, tensor)(
                lambda fixed_label: tensor.pure_tensor(
                    module.module_generator(module_label),
                    fixed.module_generator(fixed_label),
                )
            )
        )

    def _counit_component(self, module):
        internal_mor = self.right_adjoint()(module)
        return BilinearMap(
            internal_mor,
            self.fixed_module(),
            module,
            lambda mor_label, fixed_label: internal_mor.module_generator(mor_label)(
                self.fixed_module().module_generator(fixed_label)
            ),
        )

    def _repr_(self):
        return f"Tensor/internal-Mor adjunction with {self.fixed_module()}"


__all__ = []
