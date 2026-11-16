r"""The torsion placement is claimed by the construction that knows torsion.

``FormModules(R).FinitelyPresented().Torsion()`` is a placement claim, and a
claim is made by the construction that states it -- the discriminant form, a
subquotient of a torsion module, the twist functor -- never refined from a
computed answer (``DEF-03``, ``CAT-04``).  So equipping a finite cokernel with a
form does not place the result in the torsion refinement, however its invariant
factors read: the module is what its construction put it in, and the predicate
:meth:`is_torsion` stays available to whoever asks it.

A claim is trusted, not checked (``OWN-22``: construction is instant, checking is
asked for).  The torsion-form constructor stores the module the claimant named
and the Gram data, and does not read the module's invariant factors to confirm
the claim; a claim that is false is refuted where the claim is stated -- by the
validator of the claim's category, when a caller asks it.

Over $Z$, $5 \cdot 1$ has cokernel $Z/5$ with $b(x,x) = 1/5$, and the zero map
has cokernel $Z$, which is not a torsion module.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _dilation_of_z(scalar):
    r"""Return $Z \xrightarrow{scalar} Z$, the presentation datum of the specimens."""
    free = ZZ.free_module(1)
    (generator,) = free.module_generators()
    return free.Mor(free)({0: scalar * generator})


def _cokernel_of_a_dilation(scalar):
    r"""Return $\operatorname{coker}\bigl(Z \xrightarrow{scalar} Z\bigr)$."""
    return _dilation_of_z(scalar).cokernel()


def _form_values():
    r"""Return $Q/Z$, the value module of a form on a finite integral module."""
    return FractionFieldQuotients(ZZ)(1)


def _torsion_forms():
    r"""The finitely presented torsion modules with a bilinear form: the claim."""
    return BilinearFormModules(ZZ).FinitelyPresented().Torsion()


def test_a_cokernel_form_is_not_placed_in_torsion_by_a_computation() -> None:
    r"""$Z/5$ with $b = 1/5$: a construction that claimed nothing places it nowhere."""
    module = _cokernel_of_a_dilation(ZZ(5))
    values = _form_values()

    form = BilinearFormModules(ZZ)(
        module.bilinear_forms(values)(((values(QQ(1) / QQ(5)),),))
    )

    assert form in FormModules(ZZ).FinitelyPresented()
    assert form not in FormModules(ZZ).FinitelyPresented().Torsion()
    assert form.is_torsion() is True
    assert int(form.cardinality()) == 5


def test_the_torsion_form_constructor_places_the_claim_it_states() -> None:
    r"""The same module and Gram data through the torsion form constructor."""
    module = _cokernel_of_a_dilation(ZZ(5))
    values = _form_values()

    form = _torsion_forms().from_module(
        module,
        ((values(QQ(1) / QQ(5)),),),
        values,
    )

    assert form in FormModules(ZZ).FinitelyPresented().Torsion()
    assert int(form.cardinality()) == 5


def test_a_false_claim_is_trusted_by_the_construction() -> None:
    r"""$\operatorname{coker}(0) = Z$ is not torsion, and the form's constructor says nothing about it.

    The descent validator is asked of the result, and the relations are empty, so
    it holds: what the constructor stores is the caller's module and Gram data.
    """
    module = _cokernel_of_a_dilation(ZZ.zero())
    values = _form_values()

    form = _torsion_forms().from_module(
        module,
        ((values(QQ(1) / QQ(5)),),),
        values,
    )

    form.validate_descent()
    assert form in FormModules(ZZ).FinitelyPresented().Torsion()
    assert form.unformed_module() == module


def test_a_module_that_claims_no_torsion_states_no_refutation_of_one() -> None:
    r"""$\operatorname{coker}(0) = Z$ claims no torsion, and carries no such validator."""
    module = _cokernel_of_a_dilation(ZZ.zero())

    with pytest.raises(AttributeError):
        module.validate_torsion_claim()

    assert module.is_torsion() is False


def test_equipping_a_declared_torsion_module_keeps_its_placement() -> None:
    r"""The generic form constructor reads the module's declared placement.

    $Z/5$ is constructed in ``Modules(Z).FinitelyPresented().Torsion()``, and
    that construction states the module's placement.  Equipping it with a form
    keeps the placement those data already carry; neither the bilinear nor the
    quadratic form constructor reads the invariant factors to discover it.
    """
    module = Modules(ZZ).FinitelyPresented().Torsion()(_dilation_of_z(ZZ(5)))
    values = _form_values()
    gram = ((values(QQ(1) / QQ(5)),),)

    bilinear = FormModules(ZZ)(module.bilinear_forms(values)(gram))
    quadratic = FormModules(ZZ)(module.quadratic_forms(values)(gram))

    assert bilinear in FormModules(ZZ).FinitelyPresented().Torsion()
    assert quadratic in FormModules(ZZ).FinitelyPresented().Torsion()
