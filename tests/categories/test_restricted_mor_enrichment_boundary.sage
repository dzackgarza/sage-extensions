r"""Derivations of a polynomial ring into a free module."""

from sage_extensions.all import *  # noqa: F401,F403


def test_derivation_determined_by_x_to_e_obeys_the_leibniz_rule() -> None:
    r"""For ``D: Q[x] -> Q[x] e`` with ``D(x) = e``: ``D(x^2) = 2x e`` and ``D(x^3 + 1) = 3x^2 e``.

    ``Der_Q(Q[x], M) = M`` by ``D |-> D(x)``, so ``D`` is ``f |-> f' e``.
    """
    ring = QQ['x']
    x = ring('x')
    target = Modules(ring)(ring**1)
    (e,) = target.basis()
    derivations = ring.derivations(target)
    derivation = derivations({x: e})

    assert derivation(x**2) == 2 * x * e
    assert derivation(x**3 + 1) == 3 * x**2 * e
    assert derivation(ring.one()) == target.zero()
    assert derivation((x + 1) * (x - 1)) == (x + 1) * derivation(x - 1) + (x - 1) * derivation(x + 1)
