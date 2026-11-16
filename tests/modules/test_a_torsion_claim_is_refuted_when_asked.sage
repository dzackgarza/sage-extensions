r"""A claimed torsion placement is refuted when the caller asks, and only then.

``validate_torsion_claim`` is a validator (``OWN-22``) on a module with a chosen
finite presentation: over a principal ideal domain the cokernel of the
presenting morphism is torsion exactly when that morphism becomes surjective
over the fraction field, and the validator refutes the claim when it is false.
Construction passes ``check=False``, so nothing is refuted until a caller asks,
and asking is ``check=True`` or the strict-checking flag.

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


def test_construction_does_not_refute_the_claim() -> None:
    r"""The zero map's cokernel is $Z$: the module reports it, and nothing raised."""
    module = _endomorphism_of_z(ZZ.zero()).cokernel()

    assert module.is_torsion() is False
    assert tuple(module.invariant_factors()) == (ZZ(0),)


def test_a_false_torsion_claim_is_refuted_when_the_caller_checks() -> None:
    r"""The same module, with the validator asked for."""
    module = _endomorphism_of_z(ZZ.zero()).cokernel()

    with pytest.raises(ValueError):
        module.validate_torsion_claim()


def test_a_true_torsion_claim_survives_the_check() -> None:
    r"""The cokernel of $3 \cdot 1$ is $Z/3$, and its invariant factor is $3$."""
    module = _endomorphism_of_z(ZZ(3)).cokernel()

    module.validate_torsion_claim()
    assert tuple(module.invariant_factors()) == (ZZ(3),)
