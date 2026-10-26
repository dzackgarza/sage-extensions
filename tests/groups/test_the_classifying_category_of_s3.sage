r"""The one-object category $BS_3$, whose arrows are the elements of $S_3$.

$BG$ has one object $*$ and $\mathrm{Mor}(*, *) = G$, with composition the
group law, identity the unit and every arrow invertible.  So in $BS_3$ the
arrow $(1\,2)$ composed with itself is the identity, the inverse of
$(1\,2\,3)$ is $(1\,3\,2)$, and composing $(1\,2)$ with $(1\,2\,3)$ gives
the arrow of their product.  This is the definition of $BG$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_composition_in_b_s3_is_the_group_law_of_s3() -> None:
    group = Groups.S(3)
    classifying = group.classifying_category()
    point = classifying.object()
    arrows = classifying.Mor(point, point)
    transposition = arrows(group((1, 2)))
    three_cycle = arrows(group((1, 2, 3)))

    assert classifying.an_object() is point
    assert transposition * three_cycle == arrows(group((1, 2)) * group((1, 2, 3)))
    assert (transposition * three_cycle).group_element() == group((1, 2)) * group((1, 2, 3))
    assert transposition * transposition == arrows.identity()
    assert ~three_cycle == arrows(group((1, 3, 2)))
    assert transposition != three_cycle
