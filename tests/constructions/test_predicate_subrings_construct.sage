r"""The rationals contain the predicate-defined subring of elements with denominator one."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_predicate_subring_retains_ambient_predicate_and_inclusion() -> None:
    integers = QQ.predicate_subring(
        lambda element: element.denominator() == 1,
        "the denominator is one",
    )
    predicate = integers.defining_predicate()
    inclusion = integers.inclusion()

    assert integers in PredicateSubrings()
    assert integers.ambient_ring() is QQ
    assert predicate(QQ(3))
    assert not predicate(QQ(1) / 2)
    assert integers.zero() in integers
    assert integers.one() in integers
    assert inclusion.domain() is integers
    assert inclusion.codomain() is QQ
    assert inclusion(integers.one()) == QQ.one()

