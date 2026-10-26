r"""Algebras regarded as modules over their scalars."""

from sage_extensions.all import *  # noqa: F401,F403


def test_presented_pid_algebra_flatness_uses_the_exact_scalar_kernel() -> None:
    r"""``QQ[t][x,y]/(xy - t)`` is a torsion-free, hence flat, ``QQ[t]``-module
    (flat = torsion-free over a PID); ``QQ[t][z,w]/(t)`` is ``t``-torsion and not flat."""
    parameter = QQ.polynomial_ring("t")
    t = parameter.algebra_generator("t")
    presentation = parameter.polynomial_ring(("x", "y"))
    x = presentation.algebra_generator("x")
    y = presentation.algebra_generator("y")
    family = (presentation).quotient_by_relations((x * y - t,))

    assert family in Modules(parameter)
    assert family.is_integral_domain()
    assert family.is_torsion_free()
    assert family.is_flat()

    killed_presentation = parameter.polynomial_ring(("z", "w"))
    killed = (killed_presentation).quotient_by_relations((t,))
    assert killed.is_integral_domain()
    assert not killed.is_torsion_free()
    assert not killed.is_flat()


def test_two_ramifies_in_the_gaussian_integers() -> None:
    r"""In ``ZZ[i]``: ``(1 + i)(1 - i) = 2`` and ``(1 + i)^2 = 2i``, so
    ``2 = -i (1 + i)^2`` with ``-i`` a unit; ``ZZ[i]`` is free of rank 2 over ``ZZ``."""
    gaussian = QuadraticField(-1, "I").ring_of_integers()
    i = gaussian.gen(1)

    assert i * i == -1
    assert (1 + i) * (1 - i) == 2
    assert (1 + i) ** 2 == 2 * i
    assert -i * (1 + i) ** 2 == 2
    assert gaussian.module_rank() == 2
