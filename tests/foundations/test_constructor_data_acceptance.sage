r"""Two multiplications on one module give two different algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def _multiplication(module, square_of_x):
    one = module.module_generator("one")
    x = module.module_generator("x")
    return BilinearMap(
        module,
        module,
        module,
        {
            ("one", "one"): one,
            ("one", "x"): x,
            ("x", "one"): x,
            ("x", "x"): square_of_x,
        },
    )


def test_x_squared_zero_gives_the_dual_numbers_and_x_squared_x_splits() -> None:
    r"""On $\mathbb{Q}\langle 1, x\rangle$: $x^2 = 0$ gives $\mathbb{Q}[x]/(x^2)$; $x^2 = x$ gives $\mathbb{Q} \times \mathbb{Q}$.

    In the second algebra $x$ and $1 - x$ are orthogonal idempotents; in the
    first, $x$ is a nonzero nilpotent, so the two algebras are not isomorphic.
    """
    module = Modules(QQ)(Sets()(("one", "x")))
    dual_numbers = Algebras(QQ)(module, _multiplication(module, module.zero()))
    split = Algebras(QQ)(module, _multiplication(module, module.module_generator("x")))

    x = dual_numbers.module_generator("x")
    assert x * x == dual_numbers.zero()
    assert x != dual_numbers.zero()

    e = split.module_generator("x")
    f = split.one() - e
    assert e * e == e
    assert f * f == f
    assert e * f == split.zero()
    assert not dual_numbers.is_isomorphic(split)
