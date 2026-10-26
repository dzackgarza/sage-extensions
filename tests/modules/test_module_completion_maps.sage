r"""$x$-adic completion of finitely generated $\mathbb Q[x]$-modules.

For a Noetherian ring $A$ and ideal $I$, $M \mapsto \hat M = \hat A \otimes_A M$
is exact on finitely generated modules (Atiyah–Macdonald, *Introduction to
Commutative Algebra*, 10.12 and 10.13), so completion preserves injectivity,
kernels and cokernels of maps between them.
"""

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(R, a):
    return Modules(R)(R.quotient_ring(R.ideal(a)))


def test_multiplication_by_x_on_q_x_stays_injective_on_q_x_completed() -> None:
    """x is a nonzerodivisor of QQ[[x]]. Source: Atiyah–Macdonald 10.14 (completion is flat)."""
    R = QQ["x"]
    x = R.gen()
    M = R**1
    multiplication = M.End()({0: x * M.module_generator(0)})
    assert multiplication.is_injective()

    completed = multiplication.adic_completion(R.ideal(x))
    assert completed.domain().base_ring().residue_field() == QQ
    assert completed.is_injective()
    assert completed.kernel().is_zero()
    assert not completed.is_surjective()


def test_the_cokernel_of_x_on_q_x_completed_is_the_residue_field() -> None:
    """QQ[[x]] / x QQ[[x]] = QQ, of rank 1 over the residue field. Source: Atiyah–Macdonald 10.15."""
    R = QQ["x"]
    x = R.gen()
    M = R**1
    completed = M.End()({0: x * M.module_generator(0)}).adic_completion(R.ideal(x))
    completion = completed.domain().base_ring()
    cokernel = completed.cokernel()

    assert not cokernel.is_zero()
    assert cokernel.annihilator() == completion.maximal_ideal()
    assert cokernel.base_change(completion.residue_map()).module_rank() == 1


def test_multiplication_by_x_on_q_x_mod_x3_keeps_its_kernel_after_completion() -> None:
    """ker(x on QQ[x]/(x^3)) = (x^2)/(x^3) != 0, and completion is exact. Source: Atiyah–Macdonald 10.12."""
    R = QQ["x"]
    x = R.gen()
    M = cyclic(R, x**3)
    multiplication = M.End()({0: x * M.module_generator(0)})
    assert not multiplication.is_injective()
    assert multiplication.kernel().minimal_number_of_generators() == 1

    completed = multiplication.adic_completion(R.ideal(x))
    assert not completed.is_injective()
    assert completed.kernel().minimal_number_of_generators() == 1


def test_q_x_mod_x4_is_already_x_adically_complete_and_projects_to_q_x_mod_x3() -> None:
    r"""$x^4 M = 0$, so $M \to \hat M$ is an isomorphism, and $M \to \hat M \to M/x^3M$ is the quotient map:
    it kills $x^3 g$ and not $x^2 g$.

    Source: Atiyah–Macdonald 10.3 (completion of a module with an eventually zero filtration).
    """
    R = QQ["x"]
    x = R.gen()
    M = cyclic(R, x**4)
    g = M.module_generator(0)
    completion = M.adic_completion(R.ideal(x)).base_ring()
    unit = M.completion_unit(completion)
    projection = M.adic_module_projection(completion, 3)

    assert unit.is_isomorphism()
    assert projection(unit(x**3 * g)) == projection.codomain().zero()
    assert projection(unit(x**2 * g)) != projection.codomain().zero()
