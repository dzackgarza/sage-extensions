r"""The torsion placement is claimed by the construction that knows torsion.

``FormModules(R).FinitelyPresented().Torsion()`` is a placement claim, and a
claim is made by the construction that states it -- the discriminant form, a
subquotient of a torsion module, the twist functor -- never refined from a
computed answer (``DEF-03``, ``CAT-04``).  So equipping a finite cokernel with a
form does not place the result in the torsion refinement, however its invariant
factors read: the module is what its construction put it in, and the predicate
:meth:`is_torsion` is available to anyone who asks.

The same rule governs construction time (``OWN-22``, "Construction is
instant"): a torsion-form constructor stores its claim and its Gram data, and
the relation matrix that would confirm the claim is materialized by the first
request that needs it, never by the construction.  The refutation of a false
claim is the validator of the category the claim was made in, so a module that
claimed nothing carries none.

Over $Z$, $5 \cdot 1$ has cokernel $Z/5$ with $b(x,x) = 1/5$, and the zero map
has cokernel $Z$, which is not a torsion module.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _cokernel_of_a_dilation(scalar):
    r"""Return $\operatorname{coker}\bigl(Z \xrightarrow{scalar} Z\bigr)$."""
    free = ZZ.free_module(1)
    (generator,) = free.module_generators()
    return free.Mor(free)({0: scalar * generator}).cokernel()


def _form_values():
    r"""Return $Q/Z$, the value module of a form on a finite integral module."""
    return FractionFieldQuotients(ZZ)(1)


def test_a_cokernel_form_is_not_placed_in_torsion_by_a_computation() -> None:
    r"""$Z/5$ with $b = 1/5$: a construction that claimed nothing places it nowhere."""
    module = _cokernel_of_a_dilation(ZZ(5))
    values = _form_values()
    gram = ((values(QQ(1) / QQ(5)),),)

    def equip():
        return BilinearFormModules(ZZ)(module.bilinear_forms(values)(gram))

    form, constructed, requested = construction_work_of(
        equip,
        lambda formed: formed.cardinality(),
    )

    assert form in FormModules(ZZ).FinitelyPresented()
    assert form not in FormModules(ZZ).FinitelyPresented().Torsion()
    assert constructed == 0
    assert requested > 0
    assert int(form.cardinality()) == 5


def test_the_torsion_form_constructor_states_the_claim_itself() -> None:
    r"""The same module and Gram data through the torsion form constructor."""
    module = _cokernel_of_a_dilation(ZZ(5))
    values = _form_values()
    gram = ((values(QQ(1) / QQ(5)),),)

    def claim():
        return BilinearFormModules(ZZ).FinitelyPresented().Torsion().from_module(
            module,
            gram,
            values,
        )

    form, constructed, requested = construction_work_of(
        claim,
        lambda formed: formed.cardinality(),
    )

    assert form in FormModules(ZZ).FinitelyPresented().Torsion()
    assert constructed == 0
    assert requested > 0
    assert int(form.cardinality()) == 5


def test_a_module_that_claims_no_torsion_states_no_refutation_of_one() -> None:
    r"""$\operatorname{coker}(0) = Z$ claims no torsion, and carries no such validator."""
    module = _cokernel_of_a_dilation(ZZ.zero())

    with pytest.raises(AttributeError):
        module.validate_torsion_claim()

    assert module.is_torsion() is False
