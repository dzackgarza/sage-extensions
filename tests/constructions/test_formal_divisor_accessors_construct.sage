r"""Formal divisors expose their support and textual representations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_formal_divisor_components_and_representations() -> None:
    group = FormalDivisorGroups(ZZ)(("p", "q"))
    divisor = (
        ZZ(2) * group.module_generator("p")
        - group.module_generator("q")
    )

    assert group.components(divisor).cardinality() == cardinal(2)
    assert "p" in group.divisor_repr(divisor)
    assert "q" in group.divisor_repr(divisor)
    assert "p" in group.divisor_latex(divisor)
    assert "q" in group.divisor_latex(divisor)
