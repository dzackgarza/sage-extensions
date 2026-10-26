r"""Maps of modules over the local ring of the affine line at the origin."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_cokernel_of_x_on_the_local_ring_at_the_origin_is_the_residue_field() -> None:
    r"""For $A = \mathbb Q[x]_{(x)}$, $\operatorname{coker}(A \xrightarrow{x} A) = A/\mathfrak m = \mathbb Q$:
    nonzero, cyclic, with annihilator $\mathfrak m = (x)$.

    Source: Atiyah–Macdonald, Introduction to Commutative Algebra, ch. 3 (localization); by hand.
    """
    R = QQ["x"]
    x = R.gen()
    A = R.localization_at_prime(R.ideal(x))
    M = Modules(A)(A)
    multiplication_by_x = M.Mor(M)({0: x * M.module_generator(0)})

    residue_field = multiplication_by_x.cokernel()

    assert not residue_field.is_zero()
    assert residue_field.minimal_number_of_generators() == 1
    assert residue_field.annihilator() == A.maximal_ideal()
    assert multiplication_by_x.is_injective()
