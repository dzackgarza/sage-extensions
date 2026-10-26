r"""Selected polynomial and associative algebra quotient computations."""


from sage.algebras.free_algebra import FreeAlgebra as _SageFreeAlgebra
from sage.algebras.free_algebra import FreeAlgebra_generic
from sage.rings.noncommutative_ideals import Ideal_nc

from sage_extensions.categories.algebras.algebras import (
    AlgebrasWithChosenFinitePresentation,
    FinitelyPresentedAlgebras,
)
from sage_extensions.categories.algebras.free_algebras import (
    GradedFreeAlgebras,
    TensorAlgebras,
    _WordFramedPresentedAlgebra,
)
from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import _relation_morphism
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.modules.tensor_products import (
    _flatten_tensor_label,
    _nested_tensor_label,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    _engine_element,
    _engine_ring,
)
from sage_extensions.categories.sets.indexed_families import indexed_family




class _HomogeneousPresentationTensorIdeal(Ideal_nc):
    r"""A homogeneous two-sided ideal with degree-local letterplace reduction.

    The ring and ideal remain the original generic free associative algebra
    and its supplied relations.  Letterplace is only a normal-form supplier:
    an element's finite word support is split into homogeneous components,
    each component uses Sage's degree-bounded ``normal_form``, and the results
    are transported back and added in the original ring.  Thus this presents
    the whole quotient, including inhomogeneous elements; it neither requests
    a global Groebner basis nor replaces the quotient by one graded piece.

    Apart from the zero and unit ideals, the selected computation requires
    homogeneous relations over an exact field supported by libSingular.
    Other associative finite presentations remain valid mathematical data
    but need a different normal-form computation.

    Source contract (not an executed validation): Sage's ``normal_form``
    requests ``groebner_basis(degbound=element.degree())``; see
    https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/letterplace/free_algebra_element_letterplace.html
    and the generic free-algebra conversion at
    https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/free_algebra.html.
    """

    def __init__(self, presentation_ring, relations) -> None:
        engine = _engine_ring(presentation_ring)
        assert isinstance(engine, FreeAlgebra_generic), (
            f"the selected homogeneous associative quotient of {presentation_ring} "
            "needs the native free-word presentation computation"
        )
        backend_relations = tuple(
            _engine_element(presentation_ring, relations.value(index))
            for index in relations.index_set()
        )
        Ideal_nc.__init__(self, engine, backend_relations, side="twosided")
        self._presentation_ring = presentation_ring
        self._selected_relations = relations
        self._nonzero_relations = tuple(
            relation for relation in backend_relations
            if relation.monomial_coefficients()
        )
        self._unit_relation = next(
            (relation for relation in self._nonzero_relations
             if all(len(word) == 0 for word in relation.monomial_coefficients())
             and relation.is_unit() is True),
            None,
        )
        if not self._nonzero_relations or self._unit_relation is not None:
            return

        for relation in self._nonzero_relations:
            assert len({len(word) for word in relation.monomial_coefficients()}) == 1, (
                f"the selected associative quotient of {presentation_ring} needs "
                "a normal-form computation for nonhomogeneous defining relations"
            )
        assert presentation_ring.base_ring() in OwnedFields(), (
            f"the selected homogeneous associative quotient of {presentation_ring} "
            "needs a two-sided normal-form computation over this coefficient ring"
        )
        assert engine.base_ring().is_exact() is True, (
            f"the selected homogeneous associative quotient of {presentation_ring} "
            "needs exact coefficient computations"
        )
        try:
            letterplace = _SageFreeAlgebra(
                engine.base_ring(), names=engine.variable_names(),
                implementation="letterplace",
            )
        except (ImportError, TypeError, NotImplementedError) as error:
            assert False, (
                f"the selected homogeneous associative quotient of {presentation_ring} "
                "needs a letterplace coefficient realization: "
                f"{error}"
            )
        # A generic free-algebra hom evaluates ordered words.  Calling the
        # letterplace element constructor on a generic word polynomial is not
        # this conversion and can discard its noncommutative interpretation.
        self._to_letterplace = engine.hom(letterplace.gens(), letterplace)
        self._letterplace_ideal = letterplace.ideal(
            tuple(self._to_letterplace(relation) for relation in self._nonzero_relations),
            side="twosided",
        )

    def reduce(self, element):
        engine = self.ring()
        element = engine(element)
        if self._unit_relation is not None:
            return engine.zero()
        if not self._nonzero_relations:
            return element

        components = {}
        for word, coefficient in element.monomial_coefficients().items():
            components.setdefault(len(word), {})[word] = coefficient
        result = engine.zero()
        for degree, coefficients in components.items():
            component = engine(coefficients)
            if degree == 0:
                # A proper homogeneous ideal over a field has no degree-zero
                # part; the nonzero constant-relation case was handled above.
                result += component
                continue
            reduced = self._to_letterplace(component).normal_form(
                self._letterplace_ideal
            )
            # Sage's maintained conversion reads successive letterplace
            # blocks as ordered free-monoid letters, with the same scalars.
            result += engine(reduced)
        return result

    def _contains_(self, element) -> bool:
        return self.reduce(element) == self.ring().zero()


class _LinearPresentationTensorIdeal(Ideal_nc):
    r"""Two-sided linear-relation ideal reduced by tensor powers of a module.

    Sage's generic noncommutative quotient ring delegates normal forms to the
    ideal.  For the ideal generated by the linear relations of a finitely
    presented module ``M``, its homogeneous degree-``d`` quotient is exactly
    ``M^{tensor d}``.  The module category's tensor-product construction therefore
    supplies the normal form; this class is only the adapter from free-algebra
    words to those tensor-product coordinates.
    """

    def __init__(self, presentation_ring, module, relations) -> None:
        engine = _engine_ring(presentation_ring)
        Ideal_nc.__init__(self, engine, relations, side="twosided")
        self._presentation_ring = presentation_ring
        self._module = module
        self._labels = module.module_generating_set()
        self._tensor_powers = {1: module}

    def _tensor_power(self, degree):
        power = self._tensor_powers.get(degree)
        if power is not None:
            return power

        power = Modules(self._module.base_ring()).tensor_product(
            (self._tensor_power(degree - 1), self._module)
        )
        self._tensor_powers[degree] = power
        return power

    def _free_word(self, word):
        engine = self.ring()
        result = engine.one()
        ranking = self._labels.ranking_map()
        for label in word:
            result *= engine.gen(int(ranking(label)))
        return result

    def reduce(self, element):
        engine = self.ring()
        represented = _owned_engine_element(self._presentation_ring, engine(element))
        homogeneous_components = self._presentation_ring.homogeneous_components(
            represented
        )

        result = engine.zero()
        for degree, component in homogeneous_components.items():
            degree = int(degree)
            if degree == 0:
                coordinates = component.parent().framing_morphism().lift(component)
                scalar = sum(
                    (coordinates(label) for label in coordinates.support().domain()),
                    self._module.base_ring().zero(),
                )
                result += _engine_element(self._module.base_ring(), scalar)
                continue

            tensor_power = self._tensor_power(degree)
            source_coordinates = component.parent().framing_morphism().lift(component)
            tensor_element = tensor_power.linear_combination(
                {
                    _nested_tensor_label(
                        self._module,
                        _flatten_tensor_label(source_label, degree),
                    ): source_coordinates(source_label)
                    for source_label in source_coordinates.support().domain()
                }
            )
            representative = tensor_power._smith_representative(tensor_element)
            coordinates = tensor_power.framing_morphism().lift(representative)
            for tensor_label in coordinates.support().domain():
                result += _engine_element(
                    tensor_power.base_ring(), coordinates(tensor_label)
                ) * self._free_word(
                    _flatten_tensor_label(tensor_label, degree)
                )
        return result

    def _contains_(self, element) -> bool:
        return self.reduce(element) == self.ring().zero()


def _tensor_algebra_from_module_presentation(presentation_ring, module):
    r"""Quotient a free associative algebra by ``module``'s linear relations."""

    engine = _engine_ring(presentation_ring)
    relations = _relation_morphism(module)
    generator_labels = tuple(relations.codomain().module_generating_set())
    base = presentation_ring.base_ring()

    def backend_relation(relation_label):
        image = relations(relations.domain().module_generator(relation_label)).to_vector()
        result = engine.zero()
        for position, generator_label in enumerate(generator_labels):
            coefficient = image(generator_label)
            if coefficient:
                result += _engine_element(base, coefficient) * engine.gen(position)
        return result

    selected_relations = indexed_family(
        relations.domain().module_generating_set(),
        lambda index: _owned_engine_element(presentation_ring,
            backend_relation(index)
        ),
        name="Tensor-algebra defining relations",
    )
    if all(relation == presentation_ring.zero() for relation in selected_relations):
        return presentation_ring

    # Private serialization for Sage's noncommutative ideal object.
    backend_relations = [
        _engine_element(presentation_ring, relation)
        for relation in selected_relations
    ]
    presentation_ideal = _LinearPresentationTensorIdeal(
        presentation_ring,
        module,
        backend_relations,
    )
    quotient_engine = engine.quotient(presentation_ideal)
    labels = presentation_ring.algebra_generating_set()
    presented = _WordFramedPresentedAlgebra(
        quotient_engine,
        base,
        labels,
        presentation_ring,
        selected_relations,
        presentation_ideal,
        extra_categories=(
            GradedFreeAlgebras(base),
            TensorAlgebras(base),
            GradedAlgebras(base),
        ),
        generating_module=module,
    )
    return presented


__all__ = [
    "AlgebrasWithChosenFinitePresentation",
    "FinitelyPresentedAlgebras",
]
