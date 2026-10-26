r"""Adic formal spectra and their compatible infinitesimal thickenings."""

from sage.misc.cachefunc import cached_method
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.products import DirectedSystem, PosetCategory
from sage_extensions.categories.abstract_categories.cat import NaturalTransformationMorphism
from sage_extensions.categories.functors.core import Functor, NaturalTransformation
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.categories.rings.ring_foundation import OwnedRings


from sage_extensions.categories.schemes.schemes import Schemes, _affine_spec_morphism




class _FormalThickeningSystem(Functor):
    r"""The directed system ``Spec(A/I) -> Spec(A/I^2) -> ...``."""

    def __init__(self, source_ring, ideal_of_definition) -> None:
        assert ideal_of_definition.ring() is source_ring, (
            f"the ideal of definition {ideal_of_definition} is an ideal of "
            f"{ideal_of_definition.ring()}, not of the ring {source_ring} being completed"
        )
        self._source_ring = source_ring
        self._ideal = ideal_of_definition
        self._base_index = PosetCategory(NN)
        self._scheme_base_ring = source_ring.affine_spectrum().scheme_base_ring()
        self._system_category = DirectedSystem(
            self._base_index,
            Schemes(self._scheme_base_ring),
        )
        super().__init__(self._base_index, Schemes(self._scheme_base_ring))

    def source_ring(self):
        return self._source_ring

    def ideal_of_definition(self):
        return self._ideal

    def scheme_base_ring(self):
        return self._scheme_base_ring

    def base_index_category(self):
        return self._base_index

    def system_category(self):
        return self._system_category

    def exponent(self, index):
        return NN(int(index.value()) + 1)

    def thickening_ring(self, exponent):
        exponent = int(exponent)
        assert exponent > 0, (
            f"the thickening A/I^n of {self.source_ring()} needs an exponent n >= 1, got {exponent}"
        )
        return self.source_ring().quotient_ring(
            self.ideal_of_definition().power(exponent)
        )

    def transition_ring_map(self, higher_exponent, lower_exponent):
        higher_exponent = int(higher_exponent)
        lower_exponent = int(lower_exponent)
        assert higher_exponent >= lower_exponent > 0, (
            f"the transition map A/I^m -> A/I^n needs m >= n >= 1, got m = {higher_exponent} "
            f"and n = {lower_exponent}"
        )
        higher = self.thickening_ring(higher_exponent)
        lower = self.thickening_ring(lower_exponent)
        lower_projection = lower.quotient_map()
        return OwnedRings().Mor(higher, lower)(
            lambda element: lower_projection(element.lift())
        )

    def _apply_object(self, index):
        quotient = self.thickening_ring(self.exponent(index))
        return quotient.affine_spectrum(base_ring=self.scheme_base_ring())

    def _apply_morphism(self, morphism):
        lower = self.exponent(morphism.domain())
        higher = self.exponent(morphism.codomain())
        return _affine_spec_morphism(
            self.transition_ring_map(higher, lower)
        )

    def functor_category(self):
        return self.system_category()

    @cached_method(key=lambda self, precision=20: int(precision))
    def completion(self, precision=20):
        r"""The ``I``-adic completion ``A^`` realized at one computation precision."""
        return self.source_ring().adic_completion(
            self.ideal_of_definition(),
            precision=int(precision),
        )


    def completed_affine_scheme(self, precision=20):
        r"""Return ``Spec(A^)`` for one computational realization, not ``Spf(A,I)``."""
        completion = self.completion(precision)
        return completion.affine_spectrum(base_ring=self.scheme_base_ring())


    def thickening(self, exponent):
        r"""Return the finite stage ``Spec(A/I^exponent)`` from the owned directed system."""
        exponent = int(exponent)
        assert exponent > 0, (
            f"the thickening Spec(A/I^n) of {self} needs an exponent n >= 1, got {exponent}"
        )
        return self.stage(self.base_index_category()(NN(exponent - 1)))


    def formal_restriction(self, higher_exponent, lower_exponent):
        r"""Return ``Spec(A/I^lower) -> Spec(A/I^higher)`` from the directed-system arrow."""
        index = self.base_index_category()
        lower = index(NN(int(lower_exponent) - 1))
        higher = index(NN(int(higher_exponent) - 1))
        return self.transition(index.Mor(lower, higher).unique())


    def completion_projection(self, precision, exponent):
        r"""Return the actual map ``A^ -> A/I^exponent`` from one realization."""
        return self.completion(precision).adic_projection(exponent)


    def compare_precisions(self, first_precision, second_precision):
        r"""Return the canonical isomorphism between two realizations of the same completion."""
        first = self.completion(first_precision)
        second = self.completion(second_precision)
        identity = self.source_ring().Mor(self.source_ring()).identity()
        forward = first.induced_map(identity, second)
        backward = second.induced_map(identity, first)
        return first.category().Core().Mor(first, second)._from_known_inverse_pair(
            forward, backward
        )


    def morphism_to(self, codomain, coordinate_ring_morphism):
        r"""Return the continuous formal-affine morphism to ``codomain``."""
        return FormalAffineMorphism(self, codomain, coordinate_ring_morphism)


    def _repr_(self):
        return f"Spf({self.source_ring()}, {self.ideal_of_definition()}-adic)"



def FormalSpectrum(source_ring, ideal_of_definition):
    r"""Return ``Spf(A,I)`` through its represented directed system of finite thickenings."""
    return _FormalThickeningSystem(source_ring, ideal_of_definition)


class _FormalAffineNaturalTransformation(NaturalTransformationMorphism):
    r"""A same-power formal-affine morphism as a natural transformation of thickening systems."""

    def __init__(self, parent, transformation, *, coordinate_ring_morphism) -> None:
        self._ring_map = coordinate_ring_morphism
        super().__init__(parent, transformation)

    def coordinate_ring_morphism(self):
        return self._ring_map

    def thickening_ring_map(self, exponent):
        source = self.codomain().thickening_ring(exponent)
        target = self.domain().thickening_ring(exponent)
        target_projection = target.quotient_map()
        ring_map = self.coordinate_ring_morphism()
        return source.Mor(target).elementwise(
            lambda element: target_projection(ring_map(element.lift()))
        )

    def thickening_morphism(self, exponent):
        exponent = int(exponent)
        index = self.domain().functor().base_index_category()(NN(exponent - 1))
        return self.component(index)

    def completed_ring_map(self, domain_precision=20, codomain_precision=20):
        r"""Return the continuous map on selected completion realizations."""
        codomain_completion = self.codomain().completion(codomain_precision)
        domain_completion = self.domain().completion(domain_precision)
        return codomain_completion.induced_map(
            self.coordinate_ring_morphism(),
            domain_completion,
        )

    def _repr_(self):
        return f"Formal morphism {self.domain()} -> {self.codomain()}"


def FormalAffineMorphism(domain, codomain, coordinate_ring_morphism):
    r"""Return the same-power formal morphism as a natural transformation of thickenings."""
    assert coordinate_ring_morphism.domain() is codomain.source_ring(), (
        f"the ring map {coordinate_ring_morphism} cannot define a formal morphism "
        f"{domain} -> {codomain}: its domain must be {codomain.source_ring()}, the ring of the "
        f"codomain, but it is {coordinate_ring_morphism.domain()}"
    )
    assert coordinate_ring_morphism.codomain() is domain.source_ring(), (
        f"the ring map {coordinate_ring_morphism} cannot define a formal morphism "
        f"{domain} -> {codomain}: its codomain must be {domain.source_ring()}, the ring of the "
        f"domain, but it is {coordinate_ring_morphism.codomain()}"
    )
    assert all(
        domain.ideal_of_definition().contains_ambient_element(
            coordinate_ring_morphism(generator)
        )
        for generator in codomain.ideal_of_definition().ideal_generators()
    ), (
        f"the ring map {coordinate_ring_morphism} does not send the ideal of definition "
        f"{codomain.ideal_of_definition()} into {domain.ideal_of_definition()}, so it does not "
        "induce maps A/J^n -> B/I^n of thickenings"
    )

    def component(index):
        exponent = domain.functor().exponent(index)
        source = codomain.thickening_ring(exponent)
        target = domain.thickening_ring(exponent)
        target_projection = target.quotient_map()
        ring_map = coordinate_ring_morphism
        stage_map = source.Mor(target).elementwise(
            lambda element: target_projection(ring_map(element.lift()))
        )
        return _affine_spec_morphism(stage_map)

    transformation = NaturalTransformation(
        domain.functor(),
        codomain.functor(),
        component,
    )
    return domain.category().Mor(domain, codomain)._transformation(
        transformation,
        element_class=_FormalAffineNaturalTransformation,
        construction_data={"coordinate_ring_morphism": coordinate_ring_morphism},
    )


__all__ = [
    "FormalAffineMorphism",
    "FormalSpectrum",
]
