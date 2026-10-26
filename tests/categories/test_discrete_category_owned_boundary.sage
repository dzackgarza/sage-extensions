r"""Functors between discrete categories."""

from sage_extensions.all import *  # noqa: F401,F403


def test_functors_between_discrete_categories_are_functions_of_their_object_sets() -> None:
    r"""A functor ``Disc(S) -> Disc(T)`` is a function ``S -> T`` (identities go to
    identities), so there are ``|T|^|S| = 3^2 = 9`` of them for ``|S| = 2``,
    ``|T| = 3``; the object-set functor sends ``0 ↦ b``, ``1 ↦ a`` to that function."""
    source = DiscreteCategory(Sets()((0, 1)))
    target = DiscreteCategory(Sets()(("a", "b", "c")))
    functors = Cat().Mor(source, target)
    functor = functors.from_object_map(lambda value: "b" if value == 0 else "a")
    on_objects = ObjectSetFunctor()(Cat().arrow(functor))

    assert functors.objects().cardinality() == 9
    assert on_objects(source.object_set()(0)) == target.object_set()("b")
    assert on_objects(source.object_set()(1)) == target.object_set()("a")
