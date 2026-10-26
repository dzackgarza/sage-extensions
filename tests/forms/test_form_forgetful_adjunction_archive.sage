r"""The free bilinear and free quadratic forms on a module.

The left adjoint of the forgetful functor from bilinear-form modules to modules
equips $M$ with the identity of $M \otimes M$; the left adjoint for quadratic
forms equips $M$ with the identity of the divided square $\Gamma^2 M$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_free_bilinear_form_on_the_plane_takes_values_in_its_tensor_square() -> None:
    r"""For $M = \mathbb{Z}^2$, $M \otimes M$ is free of rank $4$ and $e_0 \otimes e_1 \ne e_1 \otimes e_0$.

    Source: Bourbaki, *Algebra* II §3.7 (tensor product of free modules).
    """
    plane = ZZ.free_module(2)
    adjunction = Modules(ZZ).free_bilinear_form_adjunction()
    free = adjunction.left_adjoint()(plane)
    e0, e1 = free.module_generator(0), free.module_generator(1)

    assert free.value_module().module_rank() == 4
    assert free.b(e0, e1) != free.b(e1, e0)
    assert free.b(e0 + e1, e0) == free.b(e0, e0) + free.b(e1, e0)
    assert adjunction.right_adjoint()(free).module_rank() == 2


def test_the_free_quadratic_form_on_the_plane_takes_values_in_its_divided_square() -> None:
    r"""For $M = \mathbb{Z}^2$, $\Gamma^2 M$ is free of rank $3$ on $\gamma_2(e_0), \gamma_2(e_1), e_0 e_1$.

    The universal quadratic map $x \mapsto \gamma_2(x)$ has polarization
    $\gamma_2(x+y) - \gamma_2(x) - \gamma_2(y) = xy \ne 0$ and satisfies
    $\gamma_2(2x) = 4\gamma_2(x)$.  Source: Roby, *Lois polynômes et lois
    formelles* (1963), §IV; Bourbaki, *Algebra* IV §5 Ex. 8.
    """
    plane = ZZ.free_module(2)
    adjunction = Modules(ZZ).free_quadratic_form_adjunction()
    free = adjunction.left_adjoint()(plane)
    e0, e1 = free.module_generator(0), free.module_generator(1)
    polarization = free.q(e0 + e1) - free.q(e0) - free.q(e1)

    assert free.value_module().module_rank() == 3
    assert free.q(2 * e0) == 4 * free.q(e0)
    assert polarization != free.value_module().zero()
    assert polarization == free.b(e0, e1)
