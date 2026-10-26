r"""The algebraic tensor product without a chosen module framing.

For a finite family ``(M_i)`` over a commutative ring ``R``, start with the
free R-module on ``prod_i M_i`` and quotient by additivity and R-linearity
in every slot.  Elements below are classes of finite sums, not elements of
the free module on pairs.  The presentation retains the factors and their
operations; a multilinear evaluation kills each defining relation, hence
induces the unique linear map on the quotient.

This is the generators-and-relations construction in Mathlib
``LinearAlgebra/TensorProduct/Defs`` (``TensorProduct.Eqv``) and its
``TensorProduct.lift`` in ``Basic``.  The framed and finite-presentation
computations remain at their existing module owners.  Sage's
``CombinatorialFreeModule_Tensor`` requires free factors; it is not an
algorithm for this general quotient.  Equality here proves the reductions
it can perform and otherwise returns the proposition ``equal(x, y)``:
distinct representatives are never evidence of distinct quotient classes.
"""

from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.modules.general_modules import GeneralModules
from sage_extensions.categories.modules.pure.modules import (
    TensorProductModules,
)
from sage_extensions.categories.rings.ring_foundation import OwnedRings
from sage_extensions.logic import AtomicProposition, negation
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


def _same_elements(left, right):
    return all(a is b or (a == b) is True for a, b in zip(left, right, strict=True))


class _TensorClass:
    r"""A class of a finite R-linear combination modulo multilinearity."""

    def __init__(self, parent, terms) -> None:
        self._terms = parent.reduced_terms(terms)
        super().__init__(parent)

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        difference = self.parent().reduced_terms(
            (*self._terms, *((-scalar, factors) for scalar, factors in other._terms))
        )
        decision = True if not difference else AtomicProposition("equal", self, other)
        return decision if op == op_EQ else negation(decision)

    __hash__ = None

    def _repr_(self):
        return " + ".join(
            f"{scalar} * (" + " ⊗ ".join(map(str, factors)) + ")"
            for scalar, factors in self._terms
        ) or "0"


class _TensorClasses:
    r"""The quotient set of the multilinear presentation, a private Set engine.

    Finite sums are representatives.  ``reduced_terms`` only applies defining
    relations: zero in a slot vanishes, and sums differing in one slot combine
    there.  It need not produce a complete normal form.  ``evaluate`` is used
    only by the tensor owner's linear classifier, with a multilinear map.
    """

    def __init__(self, scalar_ring, factors, **rest) -> None:
        self._scalar_ring = scalar_ring
        self._factors = tuple(factors)
        super().__init__(**rest)

    def __contains__(self, value):
        return element_parent(value) is self

    def __call__(self, terms):
        return self._element_constructor_(terms)

    def _element_constructor_(self, terms):
        if element_parent(terms) is self:
            return terms
        return self.element_class(self, tuple(terms))

    def reduced_terms(self, terms):
        ring = self._scalar_ring
        kept = []
        for coefficient, values in terms:
            coefficient = ring(coefficient)
            values = tuple(values)
            assert len(values) == len(self._factors), (
                f"{values} is not a pure tensor in {self}: it needs one entry for each of the "
                f"{len(self._factors)} factors"
            )
            values = tuple(module(value) for module, value in zip(self._factors, values, strict=True))
            if (coefficient == ring.zero()) is True or any(
                (value == module.zero()) is True
                for module, value in zip(self._factors, values, strict=True)
            ):
                continue
            kept.append((coefficient, values))
        # Each reduction lowers the number of terms, so this terminates.  No
        # failed comparison is used as an inequality in the quotient.
        for slot, module in enumerate(self._factors):
            reduced = []
            for coefficient, values in kept:
                match_position = next((
                    position for position, (_, old) in enumerate(reduced)
                    if _same_elements(old[:slot] + old[slot + 1:], values[:slot] + values[slot + 1:])
                ), None)
                match match_position:
                    case None:
                        reduced.append((coefficient, values))
                    case position:
                        scalar, old = reduced.pop(position)
                        combined = module.scalar_multiple(scalar, old[slot]) + module.scalar_multiple(coefficient, values[slot])
                        if (combined == module.zero()) is not True:
                            reduced.append((ring.one(), old[:slot] + (combined,) + old[slot + 1:]))
            kept = reduced
        return tuple(kept)

    def zero(self):
        return self(())

    an_element = zero

    def add(self, left, right):
        return self((*self(left)._terms, *self(right)._terms))

    def scale(self, scalar, value):
        return self(tuple((scalar * coefficient, factors) for coefficient, factors in self(value)._terms))

    def pure(self, values):
        return self(((self._scalar_ring.one(), tuple(values)),))

    def evaluate(self, value, codomain, multilinear):
        return sum((
            codomain.scalar_multiple(coefficient, codomain(multilinear(*factors)))
            for coefficient, factors in self(value)._terms
        ), codomain.zero())

    def _repr_(self):
        return "Classes in the multilinear tensor presentation"


class _TensorQuotientModule:
    r"""Universal maps of the tensor quotient; arithmetic belongs to GeneralModules."""

    def pure_tensor(self, *values):
        return self(self.underlying_set().pure(values))

    def _classifier_evaluation(self, codomain, bilinear):
        r"""The map ``x ⊗ y ↦ b(x, y)`` on elements of this quotient."""
        return lambda value: self.underlying_set().evaluate(
            self(value).underlying_element(),
            codomain,
            bilinear,
        )

    def universal_bilinear_map(self):
        r"""The classifier of the balanced pure-tensor map, bilinear by construction."""
        return self.module_category().Mor(self, self)._from_constructed_element_map(
            self._classifier_evaluation(self, lambda left, right: self.pure_tensor(left, right))
        )

    def from_bilinear_map(self, codomain, bilinear):
        r"""Classify the stated R-bilinear evaluation, which kills the relations.

        The callable states the two-variable evaluation.  The resulting Mor
        element's linearity is the proposition ``is_linear(f)`` unless its construction derives
        bilinearity; no finite framing is invented to certify it.
        """
        self._two_factors()
        match codomain in self.module_category():
            case True:
                pass
            case False:
                raise TypeError(
                    f"cannot induce a linear map {self} -> {codomain}: the target must be in "
                    f"{self.module_category()}, but {codomain} is in {codomain.category()}"
                )
        match callable(bilinear):
            case True:
                pass
            case False:
                raise TypeError(
                    f"cannot induce a linear map {self} -> {codomain}: {bilinear!r} is not a "
                    "function of two arguments"
                )
        # A raw Python evaluation does not prove its own bilinearity, so the
        # classifier's linearity decision is the proposition ``is_linear(f)``.
        return self.module_category().Mor(self, codomain).elementwise(
            self._classifier_evaluation(codomain, bilinear)
        )


def _tensor_quotient(factors, *, extra_categories=(), extra_construction_data=None):
    ring = next(iter(factors)).base_ring()
    assert ring in OwnedRings().Commutative(), (
        f"cannot form the tensor product of {tuple(factors)} over {ring}: the tensor product of "
        f"two left modules needs a commutative ring, but {ring} is in {ring.category()}"
    )
    classes = _object_of(
        Sets(), _engine=(Sets(), _TensorClasses, _TensorClass),
        scalar_ring=ring, factors=factors,
    )
    tensor_category = TensorProductModules(ring)
    return _object_of(
        Cat().meet((GeneralModules(ring), tensor_category, *extra_categories)),
        _engine=(tensor_category, _TensorQuotientModule, None),
        base_ring=ring,
        tensor_factors=factors,
        underlying_set=classes,
        addition=classes.add,
        zero=classes.zero(),
        negation=lambda value: classes.scale(-ring.one(), value),
        scalar_action=classes.scale,
        **(extra_construction_data or {}),
    )
