r"""Canonical comparison morphisms among tensor, symmetric, exterior, and divided powers."""

from sage.arith.misc import factorial

from sage_extensions.categories.algebras.algebras import Algebras


def _constructed_algebra_morphism(
    domain, codomain, evaluator, *, linearity_premises=(), equations=(),
    transported_morphism=None,
):
    r"""Return the constructed algebra map under its retained defining premises.

    The existing algebra-Mor supplier consumes the actual linear maps and
    equations. Empty families express an unconditional canonical construction;
    unresolved premises retain the ordinary evaluator diagnostics. An actual
    ``transported_morphism`` instead retains each law separately when the
    structured source keeps the same module, multiplication and unit.
    """
    if domain.algebra_base_ring() is not codomain.algebra_base_ring():
        raise ValueError(
            f"a morphism of algebras {domain} -> {codomain} needs one base ring, but they are over "
            f"{domain.algebra_base_ring()} and {codomain.algebra_base_ring()}"
        )
    mor = Algebras(domain.algebra_base_ring()).Unital().Mor(
        domain,
        codomain,
    )
    return mor._from_constructed_element_map(
        evaluator, linearity_premises=linearity_premises, equations=equations,
        transported_morphism=transported_morphism,
    )


def _tensor_to_symmetric(module):
    r"""Return the quotient morphism ``T(M) -> Sym(M)``."""
    source = module.tensor_algebra()
    target = module.symmetric_algebra()
    return source.Mor(target)(
        lambda label: target.algebra_generator(label)
    )


def _tensor_to_alternating(module):
    r"""Return the quotient morphism ``T(M) -> Lambda(M)``."""
    source = module.tensor_algebra()
    target = module.exterior_algebra()
    return source.Mor(target)(
        lambda label: target.from_component(
            1,
            target.generating_module().module_generator(label),
        )
    )


def _symmetric_to_divided(module):
    r"""Return ``Sym(M) -> Gamma(M)``, ``x^n |-> n! gamma_n(x)``."""
    source = module.symmetric_algebra()
    target = module.divided_power_algebra()
    return source.Mor(target)(
        lambda label: target.from_component(
            1,
            target.generating_module().module_generator(label),
        )
    )


def _divided_to_symmetric(module):
    r"""Return the factorial comparison over a selected rational coefficient algebra.

    Its formula uses inverses of every factorial, so checking denominators
    only on a requested element cannot establish a map on the whole algebra.
    The retained coefficient tower supplies the rational algebra structure.
    An empty chosen module-generating family instead proves ``M=0``, when
    both algebras consist only of scalars and no factorial inversion is needed.
    """
    from sage.rings.rational_field import QQ as SageQQ
    from sage_extensions.categories.rings.ring_foundation import (
        _own_ring,
        _owned_rationals,
    )

    ring = module.base_ring()
    zero_module = (
        module.has_selected_module_resolution()
        and module.module_generating_set().is_empty() is True
    )
    rational_structure = None
    if not zero_module:
        rationals = _owned_rationals()
        try:
            rational_algebra = ring.as_algebra_over(rationals)
        except (AssertionError, ValueError) as error:
            raise AssertionError(
                f"the comparison Gamma({module}) -> Sym({module}) needs a selected "
                f"rational-algebra structure on {ring} proving that all factorials "
                "are units; no global factorial-invertibility computation is supplied"
            ) from error
        rational_structure = rational_algebra.algebra_structure_morphism()
        assert (
            rational_structure.domain() is rationals
            and rational_structure.codomain() is rational_algebra
        ), "the rational structure map of a commutative algebra retains its exact endpoints"
    source = module.divided_power_algebra()
    target = module.symmetric_algebra()

    def evaluate(element):
        element = source(element)
        result = target.zero()
        for degree, component in element.homogeneous_components().items():
            coordinates = source.graded_piece(degree).framing_morphism().lift(component)
            for label in coordinates.support().domain():
                coefficient = coordinates(label)
                denominator = 1
                monomial = target.one()
                if degree == 1:
                    support = ((label, 1),)
                elif degree == 0:
                    support = ()
                else:
                    support = (
                        (generator_label, label.multiplicity(generator_label))
                        for generator_label in label.support()
                    )
                for generator_label, power in support:
                    denominator *= int(factorial(power))
                    monomial *= target.algebra_generator(generator_label) ** int(power)
                if denominator == 1:
                    inverse = ring.one()
                else:
                    assert rational_structure is not None, (
                        "a nontrivial factorial denominator needs the retained rational structure"
                    )
                    image = rational_structure(rationals(denominator).inverse_of_unit())
                    if rational_algebra is ring:
                        inverse = image
                    else:
                        # as_algebra_over retains the literal original ring
                        # as this module's additive group. Read that datum,
                        # without asking R to invert the denominator again.
                        coefficient_module = rational_algebra.unformed_module()
                        assert coefficient_module.underlying_additive_group() is ring, (
                            "the rational scalar view retains the original coefficient ring"
                        )
                        inverse = coefficient_module(image).underlying_element()
                scalar = coefficient * ring(inverse)
                result += scalar * monomial
        return result

    return _constructed_algebra_morphism(source, target, evaluate)


__all__ = [
]
