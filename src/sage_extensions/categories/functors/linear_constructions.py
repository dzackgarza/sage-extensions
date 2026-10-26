r"""Duality, arrow kernels/cokernels, and additive/form biproduct functors."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.lattices import Lattices
from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedFreeModules,
    FinitelyPresentedModules,
    Modules,
)
from sage_extensions.categories.rings.ring_foundation import _owned_ring


class _DualizationFunctor(Functor):
    r"""Finite-free duality ``(-)^* : C^op -> C``."""

    def __init__(self, base_ring) -> None:
        category = FinitelyGeneratedFreeModules(_owned_ring(base_ring))
        super().__init__(category.opposite(), category)

    def _repr_(self):
        return "Dual-module functor (-)^*"

    def _apply_object(self, opposite_module):
        return opposite_module.underlying_object().dual_module()

    def _apply_morphism(self, opposite_morphism):
        morphism = opposite_morphism.underlying_arrow()
        source_dual = self(opposite_morphism.domain())
        target_dual = self(opposite_morphism.codomain())
        images = {}
        for codomain_label in morphism.codomain().module_generating_set():
            coefficients = {}
            for domain_label in morphism.domain().module_generating_set():
                image_coordinates = morphism.codomain().framing_morphism().lift(morphism(morphism.domain().module_generator(domain_label)))
                coefficient = image_coordinates(codomain_label)
                if (coefficient == target_dual.base_ring().zero()) is not True:
                    coefficients[domain_label] = coefficient
            images[codomain_label] = target_dual.linear_combination(coefficients)
        return source_dual.module_category().Mor(source_dual, target_dual)(images)

    def double_dual_morphism(self, module):
        r"""Return the canonical finite-free biduality map ``M -> M**``."""
        opposite = self.domain()
        dual = self(opposite(module))
        double_dual = self(opposite(dual))
        return module.module_category().Mor(module, double_dual)(
            {
                label: double_dual(
                    {
                        dual_label: dual.module_generator(dual_label)(module.module_generator(label))
                        for dual_label in dual.module_generating_set()
                    }
                )
                for label in module.module_generating_set()
            }
        )


class _BiproductBifunctor(Functor):
    r"""The direct-sum/biproduct bifunctor on finitely presented modules."""

    def __init__(self, base_ring) -> None:
        category = FinitelyPresentedModules(_owned_ring(base_ring))
        super().__init__(Cat().product((category, category)), category)

    def _repr_(self):
        return "Direct-sum bifunctor"

    def _apply_object(self, pair):
        return self.codomain().biproduct((pair.first(), pair.second()))

    def _apply_morphism(self, pair_morphism):
        left_morphism = pair_morphism.first()
        right_morphism = pair_morphism.second()
        return left_morphism.biproduct_map(
            right_morphism,
            source=self(pair_morphism.domain()),
            target=self(pair_morphism.codomain()),
        )


class _ArrowConstructionFunctor(Functor):
    r"""A functor out of the genuine arrow category of a represented category."""

    def __init__(self, object_category, codomain) -> None:
        super().__init__(object_category.ArrowCategory(), codomain)


class _KernelArrowFunctor(_ArrowConstructionFunctor):
    r"""The kernel functor from finite-free arrows to modules.

    A kernel of a map between finite-free modules need not be free or even
    finitely generated over an arbitrary coefficient ring.  The selected
    arrow computation below uses a finite generating family when one is
    supplied; this computation does not strengthen the codomain category.
    """

    def __init__(self, base_ring) -> None:
        ring = _owned_ring(base_ring)
        finite_free = FinitelyGeneratedFreeModules(ring)
        super().__init__(finite_free, Modules(ring))

    def _repr_(self):
        return "Kernel functor"

    def _apply_object(self, arrow_object):
        return arrow_object.arrow().kernel()

    def _apply_morphism(self, square):
        source_kernel = self(square.domain())
        target_kernel = self(square.codomain())
        labels = source_kernel.module_generating_set()
        assert labels.is_finite() is True, (
            "kernel-arrow computation on morphisms needs a selected finite "
            "generating family for the source kernel"
        )
        return source_kernel.module_category().Mor(source_kernel, target_kernel)(
            {
                label: target_kernel.inclusion().lift(
                    square.left()(
                        source_kernel.inclusion()(source_kernel.module_generator(label))
                    )
                )
                for label in labels
            }
        )


class _CokernelArrowFunctor(_ArrowConstructionFunctor):
    r"""The cokernel functor from the finitely presented module arrow category."""

    def __init__(self, base_ring) -> None:
        ring = _owned_ring(base_ring)
        category = FinitelyPresentedModules(ring)
        super().__init__(category, category)

    def _repr_(self):
        return "Cokernel functor"

    def _apply_object(self, arrow_object):
        return arrow_object.arrow().cokernel()

    def _apply_morphism(self, square):
        source_cokernel = self(square.domain())
        target_cokernel = self(square.codomain())
        target_projection = target_cokernel.cokernel_projection()
        return source_cokernel.module_category().Mor(source_cokernel, target_cokernel)(
            {
                label: target_projection(
                    square.right()(
                        square.domain().arrow().codomain().module_generator(label)
                    )
                )
                for label in source_cokernel.module_generating_set()
            }
        )


class _OrthogonalDirectSumBifunctor(Functor):
    r"""The orthogonal-direct-sum bifunctor on finite-rank lattices."""

    def __init__(self, base_ring) -> None:

        category = Lattices(_owned_ring(base_ring))
        super().__init__(Cat().product((category, category)), category)

    def _repr_(self):
        return "Orthogonal direct-sum bifunctor"

    def _apply_object(self, pair):
        left, right = pair.first(), pair.second()
        assert left.module_rank().is_finite() and right.module_rank().is_finite(), (
            f"the orthogonal direct sum {left} + {right} acts on morphisms here only for lattices of finite "
            f"rank, but the ranks are {left.module_rank()} and {right.module_rank()}"
        )
        return left + right

    @staticmethod
    def _embed_summand(element, summand, target, offset):
        coordinates = element.to_vector()
        summand_labels = summand.module_generating_set()
        target_labels = target.module_generating_set()
        return target.linear_combination(
            {
                target_labels[offset + int(summand_labels.ranking_map()(label))]: coefficient
                for label, coefficient in coordinates.parent()._selected_module_coefficients(coordinates).items()
            }
        )

    def _apply_morphism(self, pair_morphism):

        left_morphism = pair_morphism.first()
        right_morphism = pair_morphism.second()
        source = self(pair_morphism.domain())
        target = self(pair_morphism.codomain())
        source_labels = source.module_generating_set()
        left_source_labels = left_morphism.domain().module_generating_set()
        right_source_labels = right_morphism.domain().module_generating_set()
        left_source_rank = int(left_source_labels.cardinality())
        left_target_rank = int(left_morphism.codomain().module_generating_set().cardinality())

        def image(source_label):
            position = int(source_labels.ranking_map()(source_label))
            if position < left_source_rank:
                label = left_source_labels[position]
                return self._embed_summand(
                    left_morphism(left_morphism.domain().module_generator(label)),
                    left_morphism.codomain(),
                    target,
                    0,
                )
            label = right_source_labels[position - left_source_rank]
            return self._embed_summand(
                right_morphism(right_morphism.domain().module_generator(label)),
                right_morphism.codomain(),
                target,
                left_target_rank,
            )

        return self.codomain().Mor(source, target)(image)


@cached_function
def _dualization_functor(base_ring) -> _DualizationFunctor:
    return _DualizationFunctor(base_ring)


@cached_function
def _biproduct_bifunctor(base_ring) -> _BiproductBifunctor:
    return _BiproductBifunctor(base_ring)


@cached_function
def _kernel_arrow_functor(base_ring) -> _KernelArrowFunctor:
    return _KernelArrowFunctor(base_ring)


@cached_function
def _cokernel_arrow_functor(base_ring) -> _CokernelArrowFunctor:
    return _CokernelArrowFunctor(base_ring)


@cached_function
def _orthogonal_direct_sum_bifunctor(base_ring) -> _OrthogonalDirectSumBifunctor:
    return _OrthogonalDirectSumBifunctor(base_ring)


__all__ = []
