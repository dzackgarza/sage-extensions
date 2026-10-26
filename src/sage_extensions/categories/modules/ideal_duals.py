r"""Ideal-valued metric duals and their inverse images in an integral module.

The defining map sends x in the rational span to (y |-> b(x,y) mod I).
Its kernel is the ideal dual, including the rational radical when I=0.
See lean-categories, Lattices/Valued/IdealDual.lean, ``idealDualMap`` and
``toRationalSpan_mem_idealDual_iff``. Finite integral inverse images use
the existing module kernel computation.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.modules.affine_fibres import ModuleInverseImages
from sage_extensions.categories.modules.framed.fraction_field_quotients import FractionFieldQuotients
from sage_extensions.categories.modules.pure.modules import Modules, ModulesOverIntegralDomains
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.owned_category import _object_of


class IdealMetricDuals(OwnedCategoryOverBaseRing):
    r"""The submodules ``{x in K tensor M : b(x,M) subset dR}``."""

    def super_categories(self):
        return [ModuleInverseImages(self.base_ring())]

    def _call_(self, source, modulus):
        ring = self.base_ring()
        if source.base_ring() is not ring or source.value_module() is not ring:
            raise ValueError("an ideal metric dual requires a scalar-valued bilinear module over its base ring")
        modulus = ring(modulus)
        inclusion = ModulesOverIntegralDomains(ring)(source).generic_fibre_map()
        ambient = inclusion.codomain()
        rational = ambient.module_over_extension()
        values = FractionFieldQuotients(ring)(modulus)
        functionals = Modules(ring).Mor(source, values)
        pairing = Modules(ring).Mor(ambient, functionals)._from_constructed_element_map(
            lambda point: functionals._from_constructed_element_map(
                lambda vector: values(rational.b(
                    point.underlying_element(), inclusion(vector).underlying_element()
                ))
            )
        )
        zero = functionals.zero_subobject()
        return _object_of(
            self, source_module=source, modulus=modulus,
            linear_map=pairing, target_inclusion=zero.inclusion(),
        )

    class ParentMethods:
        def __init__(self, source_module, modulus, **rest):
            self._ideal_dual_source = source_module
            self._ideal_dual_modulus = modulus
            super().__init__(**rest)

        def source_module(self):
            return self._ideal_dual_source

        def value_ideal(self):
            return self.base_ring().ideal(self._ideal_dual_modulus)

        @cached_method
        def integral_pullback(self):
            r"""Return the formed inverse image under ``M -> K tensor M``."""
            from sage_extensions.categories.modules.framed.formed.form_modules import FormModules

            source = self.source_module()
            if self._ideal_dual_modulus == self.base_ring().zero():
                kernel = source.algebraic_correlation_morphism().kernel()
            else:
                kernel = (self.defining_morphism() * ModulesOverIntegralDomains(self.base_ring())(source).generic_fibre_map()).kernel()
            restricted = source.pullback_form(kernel.inclusion())

            def inclusion_factory(formed):
                linear = Modules(self.base_ring()).Mor(formed, source)(
                    lambda label: kernel.inclusion()(kernel.module_generator(label))
                )
                return Modules(self.base_ring()).Mono(formed, source)._subobject_inclusion(
                    linear, lift=lambda value: (
                        formed(kernel.inclusion().lift(value))
                        if kernel.inclusion().is_in_image(value) else None
                    ),
                )

            categories = [IdealDualPullbacks(self.base_ring())]
            data = {"ideal_dual": self}
            from sage_extensions.categories.lattices import Lattices

            if source in Lattices(self.base_ring()):
                categories.append(Lattices(self.base_ring()))
                data["gram_tensor"] = restricted.gram_tensor()
            return FormModules(self.base_ring())(
                restricted, _extra_categories=tuple(categories),
                _extra_construction_data=data,
                _subobject_ambient=source,
                _subobject_inclusion_factory=inclusion_factory,
            )


class IdealDualPullbacks(OwnedCategoryOverBaseRing):
    r"""Formed inverse images retaining both maps to the ideal-dual square."""

    def super_categories(self):
        from sage_extensions.categories.modules.framed.formed.form_modules import FormModules

        return [FormModules(self.base_ring())]

    class ParentMethods:
        def __init__(self, ideal_dual, **rest):
            self._ideal_dual = ideal_dual
            super().__init__(**rest)

        def defining_ideal_dual(self):
            return self._ideal_dual

        @cached_method
        def map_to_ideal_dual(self):
            dual = self.defining_ideal_dual()
            rational_inclusion = ModulesOverIntegralDomains(self.base_ring())(dual.source_module()).generic_fibre_map()
            return Modules(self.base_ring()).Mor(self, dual)(
                lambda label: dual.inclusion().lift(
                    rational_inclusion(self.inclusion()(self.module_generator(label)))
                )
            )
