r"""A conjugate subgroup conjugates its own subgroups.

A conjugate of a subgroup is a subgroup like any other: it conjugates the
subgroups it has by the same operation every group supplies.  The conjugate
kind states the pair it was built from, and that datum is an attribute of the
object; it is not the name of the operation that builds the next conjugate.

$S_3$ conjugated by $(1\,2\,3)$ carries $\langle(1\,2)\rangle$ to
$\langle(2\,3)\rangle$, a subgroup of order two whose nonidentity element is
$(2\,3)$.  Conjugating the trivial subgroup of it by that element answers the
trivial subgroup.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_conjugate_conjugates_a_subgroup_of_its_own() -> None:
    r"""$(2\,3)$ carries the trivial subgroup of $\langle(2\,3)\rangle$ to itself."""
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    conjugate = group.conjugate_subgroup(group((1, 2, 3)), subgroup)
    inner = group((2, 3))
    trivial = conjugate.subgroup(())

    assert inner in conjugate
    transported = conjugate.conjugate_subgroup(inner, trivial)
    assert transported.order() == 1
    assert group.one() in transported
