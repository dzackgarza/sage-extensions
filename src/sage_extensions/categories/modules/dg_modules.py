r"""Graded modules and differential graded modules over a represented DGA."""

from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.modules.cochain_complexes import CochainComplexes
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.logic import AtomicProposition, Propositions
from sage_extensions.validation import validator


class GradedAlgebraModules(OwnedParameterizedCategory):
    r"""Right graded modules over one selected graded algebra ``A``."""

    def an_object(self):
        r"""The graded algebra this category is over, as a module over itself."""
        return self.base()

    @classmethod
    def _repr_object_names(cls):
        return "graded modules over a graded algebra"

    def graded_algebra(self):
        return self.base()

    def parameter_category(self):
        r"""The graded algebras over the parameter's own base and grading monoid."""
        from sage_extensions.categories.algebras.graded_algebras import (
            GradedAlgebras,
        )

        algebra = self.parameter()
        return GradedAlgebras(algebra.base_ring(), algebra.grading_monoid())

    def super_categories(self):

        algebra = self.graded_algebra()
        return [GradedModules(algebra.base_ring(), algebra.grading_monoid())]

    class ParentMethods:
        def __init__(self, graded_algebra, graded_algebra_action, **rest) -> None:
            self._preamble_graded_algebra = graded_algebra
            self._preamble_graded_algebra_action = graded_algebra_action
            super().__init__(**rest)

        def graded_algebra(self):
            return self._preamble_graded_algebra

        def right_action(self):
            return self._preamble_graded_algebra_action

        def act(self, module_element, algebra_element):
            return self.right_action()(module_element, algebra_element)


class DifferentialGradedModules(OwnedParameterizedCategory):
    r"""Right differential graded modules over one selected DGA ``(A,d)``."""

    def an_object(self):
        r"""The DGA this category is over, as a module over itself."""
        return self.base()

    @classmethod
    def _repr_object_names(cls):
        return "differential graded modules"

    def dga(self):
        return self.base()

    def parameter_category(self):
        r"""The differential graded algebras over the parameter's own base."""
        from sage_extensions.categories.algebras.differential_graded_algebras import (
            DifferentialGradedAlgebras,
        )

        return DifferentialGradedAlgebras(self.parameter().base_ring())

    def super_categories(self):

        dga = self.dga()
        return [
            GradedAlgebraModules(dga),
            CochainComplexes(dga.base_ring()),
        ]

    class ParentMethods:
        def __init__(
            self,
            dg_algebra,
            regular_module_source=None,
            dg_module_leibniz_decision=None,
            **rest,
        ) -> None:
            self._preamble_dg_algebra = dg_algebra
            self._preamble_regular_dg_module_source = regular_module_source
            if not (
                dg_module_leibniz_decision is None
                or dg_module_leibniz_decision is True
                or dg_module_leibniz_decision in Propositions
            ):
                raise ValueError(
                    "the DG-module Leibniz law is retained only as True, an owned proposition, or None"
                )
            self._preamble_dg_module_leibniz_decision = dg_module_leibniz_decision
            super().__init__(**rest)

        def dga(self):
            return self._preamble_dg_algebra

        def is_differential_graded_module(self) -> bool:
            return True

        def dg_module_leibniz_decision(self):
            r"""Return the retained law ``d(ma)=d(m)a+(-1)^|m| m d(a)``."""
            selected = self._preamble_dg_module_leibniz_decision
            return (
                AtomicProposition("satisfies_dg_module_leibniz", self)
                if selected is None
                else selected
            )

        @validator
        def validate_dg_module_leibniz(self):
            r"""Reject only a proved failure of the DG-module Leibniz law."""
            decision = self.dg_module_leibniz_decision()
            if decision is False:
                raise ValueError(
                    f"{self} is not a differential graded module over {self.dga()}: "
                    "its differential does not satisfy the graded module Leibniz rule"
                )
            return decision

        def unformed_module(self):
            source = self._preamble_regular_dg_module_source
            return super().unformed_module() if source is None else source

        def _element_of_unformed_module(self, element):
            source = self._preamble_regular_dg_module_source
            if source is None:
                return super()._element_of_unformed_module(element)
            return source(element)

        def _element_from_unformed_module(self, element):
            if self._preamble_regular_dg_module_source is None:
                return super()._element_from_unformed_module(element)
            return self(element)

        def differential_component(self, degree):
            source_module = self._preamble_regular_dg_module_source
            if source_module is None:
                return super().differential_component(degree)
            dga = self.dga()
            source = self.graded_piece(degree)
            target = self.graded_piece(int(degree) + 1)
            dga_source = dga.graded_piece(degree)
            dga_target = dga.graded_piece(int(degree) + 1)
            differential = dga.differential_component(degree)
            return source.Mor(target)(
                lambda element: target(
                    differential(dga_source(element))
                    if differential.codomain() is dga_target
                    else dga_target(differential(dga_source(element)))
                )
            )



__all__ = [
    "DifferentialGradedModules",
    "GradedAlgebraModules",
]
