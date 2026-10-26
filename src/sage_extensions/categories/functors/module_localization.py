r"""Localization of modules as scalar extension along a ring localization."""

from sage_extensions.categories.abstract_categories.arrow_categories import (
    _isomorphism_from_known_inverse_pair,
)
from sage_extensions.categories.functors.scalar_change import (
    _ScalarExtensionFunctor,
)
from sage_extensions.categories.modules.localizations import (
    LocalizedModules,
    _localized_module,
)
from sage_extensions.categories.modules.pure.modules import (
    ModuleSubobjects,
)


class ModuleLocalizationFunctor(_ScalarExtensionFunctor):
    r"""The functor ``S^{-1}R tensor_R - : Mod_R -> Mod_{S^{-1}R}``."""

    def __init__(self, localization_ring) -> None:
        from sage_extensions.categories.rings.ring_foundation import LocalizationRings

        match localization_ring in LocalizationRings():
            case True:
                pass
            case False:
                raise TypeError(
                    f"module localization is the functor induced by a localization S^-1 R, but {localization_ring} "
                    "is not a localization"
                )
        self._localization_ring = localization_ring
        super().__init__(localization_ring.localization_map())

    def localization_ring(self):
        return self._localization_ring

    def localization_submonoid(self):
        return self.localization_ring().localization_submonoid()

    def is_exact(self) -> bool:
        r"""Localization of modules is exact."""
        return True

    def _apply_object(self, module):
        source_ring = self.localization_ring().localization_source()
        subobject_data = {}
        if (
            module in ModuleSubobjects(source_ring)
            and module.has_selected_module_resolution()
        ):
            source_inclusion = module.inclusion()
            localized_ambient = self(source_inclusion.codomain())
            def inclusion(localized_subobject):
                # Localization is exact, so ``S^{-1} i`` is a monomorphism
                # because ``i`` is.
                return localized_subobject.Mono(localized_ambient)._from_constructed_embedding(
                    lambda element: localized_ambient.fraction(
                        source_inclusion(element.numerator()), element.denominator(),
                    ),
                    (source_inclusion,),
                    scalar_extension_of=source_inclusion,
                    scalar_extension_functor=self,
                )

            subobject_data = {"subobject_inclusion_factory": inclusion}
        return _localized_module(
            module,
            self.localization_ring(),
            self,
            **subobject_data,
        )

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        if source in ModuleSubobjects(source.base_ring()):
            if morphism is morphism.domain().inclusion():
                inclusion = source.inclusion()
                assert inclusion.codomain() is target
                assert inclusion.scalar_extension_of() is morphism
                return inclusion

        match source:
            case _ if source in LocalizedModules(source.base_ring()):
                match target:
                    case _ if target in LocalizedModules(target.base_ring()):
                        def action(fraction):
                            return target.fraction(
                                morphism(fraction.numerator()), fraction.denominator(),
                            )
                    case _:
                        target_unit = self.unit(morphism.codomain(), localized=target)

                        def action(fraction):
                            numerator = target_unit(morphism(fraction.numerator())).underlying_element()
                            denominator = self.localization_ring().localization_map()(fraction.denominator())
                            return target.scalar_multiple(denominator.inverse_of_unit(), numerator)
                elementwise = True
            case _ if target in LocalizedModules(target.base_ring()):
                match source.has_selected_module_resolution():
                    case True:
                        pass
                    case False:
                        raise TypeError(
                            f"cannot localize the morphism {morphism}: its domain {morphism.domain()} must have a chosen "
                            "generating set"
                        )

                def action(label):
                    return target.fraction(morphism(morphism.domain().module_generator(label)))

                elementwise = False
            case _:
                return super()._apply_morphism(morphism)

        # Flatness preserves a selected monomorphism.  Read its mathematical
        # Mor placement, not its concrete morphism implementation.
        source_mor = morphism.parent().mor_category()
        monomorphisms = morphism.domain().module_category().Mono()
        match source_mor.is_subcategory(monomorphisms):
            case True:
                return source.Mono(target)._from_constructed_embedding(
                    action,
                    (morphism,),
                    elementwise=elementwise,
                    scalar_extension_of=morphism,
                    scalar_extension_functor=self,
                )
            case False:
                mor = source.module_category().Mor(source, target)
        return mor._from_scalar_extension(morphism, action, self, elementwise=elementwise)

    def unit(self, module, *, localized=None):
        r"""Return ``M -> Res_R(S^{-1}M)``, the localization unit."""

        image = self(module) if localized is None else localized
        restricted = image.restrict_scalars(self.ring_map())
        if image in LocalizedModules(image.base_ring()):
            return module.module_category().Mor(module, restricted)._from_constructed_element_map(
                lambda element: restricted.wrap(image.fraction(element))
            )
        return module.module_category().Mor(module, restricted)(
            lambda label: restricted.wrap(image.module_generator(label))
        )

    def cokernel_comparison(self, morphism):
        r"""Return ``S^{-1}coker(f) ~= coker(S^{-1}f)`` in represented regimes."""
        return _localization_cokernel_comparison(self, morphism)

    def kernel_comparison(self, morphism):
        r"""Return ``S^{-1}ker(f) ~= ker(S^{-1}f)``."""
        return _localization_kernel_comparison(self, morphism)

    def _repr_(self):
        return f"Module localization along {self.localization_ring().localization_map()}"


def _localization_cokernel_comparison(functor, morphism):
    r"""The canonical represented isomorphism ``S^-1 coker(f) ~= coker(S^-1 f)``.

    The comparison is an arrow in the core of the module category, not a
    separate record carrying two arrows.  The current explicit construction
    uses the selected finite framings of the two represented cokernels.
    """

    localized_morphism = functor(morphism)
    source_cokernel = morphism.cokernel()
    localized_source_cokernel = functor(source_cokernel)
    target_cokernel = localized_morphism.cokernel()
    localized_codomain = localized_morphism.codomain()
    assert (
        localized_source_cokernel.has_selected_module_resolution()
        and target_cokernel.has_selected_module_resolution()
        and localized_codomain.has_selected_module_resolution()
    ), (
        f"the comparison of S^-1 coker({morphism}) with coker(S^-1 {morphism}) is computed only when "
        f"both cokernels and {localized_codomain} have chosen generating sets"
    )

    source_projection = source_cokernel.cokernel_projection()
    localized_source_projection = functor(source_projection)
    target_projection = target_cokernel.cokernel_projection()
    left_labels = tuple(localized_source_cokernel.module_generating_set())
    right_labels = tuple(target_cokernel.module_generating_set())
    codomain_labels = tuple(localized_codomain.module_generating_set())
    assert left_labels == codomain_labels and right_labels == codomain_labels, (
        f"the comparison of S^-1 coker({morphism}) with coker(S^-1 {morphism}) needs both cokernels "
        f"generated by the images of the generators of {localized_codomain}, but they are generated by "
        f"{left_labels} and {right_labels}, not {codomain_labels}"
    )

    forward = localized_source_cokernel.module_category().Mor(
        localized_source_cokernel,
        target_cokernel,
    )(
        {
            label: target_projection(localized_codomain.module_generator(label))
            for label in codomain_labels
        }
    )
    inverse = target_cokernel.module_category().Mor(
        target_cokernel,
        localized_source_cokernel,
    )(
        {
            label: localized_source_projection(
                localized_codomain.module_generator(label)
            )
            for label in codomain_labels
        }
    )
    return _isomorphism_from_known_inverse_pair(forward, inverse)


def _localization_kernel_comparison(functor, morphism):
    r"""The canonical represented isomorphism ``S^-1 ker(f) ~= ker(S^-1 f)``."""

    localized_morphism = functor(morphism)
    localized_source_kernel = functor(morphism.kernel())
    target_kernel = localized_morphism.kernel()
    assert target_kernel is localized_source_kernel, (
        f"the kernel of S^-1 {morphism} is {target_kernel}, not the localization {localized_source_kernel} "
        f"of ker({morphism})"
    )
    identity = localized_source_kernel.module_category().Mor(
        localized_source_kernel,
        target_kernel,
    ).identity()
    return _isomorphism_from_known_inverse_pair(identity, identity)


__all__ = []
