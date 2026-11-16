r"""A claimed torsion placement is refuted when the caller asks, and only then.

A caller claims torsion by constructing in
``Modules(R).FinitelyPresented().Torsion()``; nothing computes at that
construction (``OWN-22``), and the claim's validator refutes it when the
constructor is asked to check or the validator is called by hand.  Over a
principal ideal domain the cokernel of the presenting morphism is torsion
exactly when that morphism becomes surjective over the fraction field.

The zero map $Z \to Z$ has cokernel $Z$, which is not torsion; $3 \cdot 1$ has
cokernel $Z/3$, which is.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _endomorphism_of_z(scalar):
    r"""The map $Z \to Z$ of multiplication by ``scalar``."""
    free = ZZ.free_module(1)
    (generator,) = free.module_generators()
    return free.Mor(free)({0: scalar * generator})


def _torsion_modules():
    r"""The finitely presented torsion modules over $Z$: the claim's category."""
    return Modules(ZZ).FinitelyPresented().Torsion()


def test_construction_does_not_refute_the_claim() -> None:
    r"""The zero map presents $Z$: the claim stands until it is checked."""
    module = _torsion_modules()(_endomorphism_of_z(ZZ.zero()))

    assert module in _torsion_modules()
    assert tuple(module.invariant_factors()) == (ZZ(0),)


def test_a_false_torsion_claim_is_refuted_when_checked() -> None:
    r"""The same claim, asked for: the relation matrix leaves a free summand."""
    presentation = _endomorphism_of_z(ZZ.zero())

    with pytest.raises(ValueError):
        _torsion_modules()(presentation, check=True)

    with pytest.raises(ValueError):
        _torsion_modules()(presentation).validate_torsion_claim()


def test_a_true_torsion_claim_survives_the_check() -> None:
    r"""The cokernel of $3 \cdot 1$ is $Z/3$, and its claim is not refuted."""
    module = _torsion_modules()(_endomorphism_of_z(ZZ(3)), check=True)

    assert module in _torsion_modules()
    assert tuple(module.invariant_factors()) == (ZZ(3),)


def test_the_claim_is_settled_by_the_modules_own_torsion_decision() -> None:
    r"""The validator asks the presented module owner; it reads no relation images itself."""
    module = _torsion_modules()(_endomorphism_of_z(ZZ(3)))

    assert relation_image_reads_of(module, module.validate_torsion_claim) == 0
