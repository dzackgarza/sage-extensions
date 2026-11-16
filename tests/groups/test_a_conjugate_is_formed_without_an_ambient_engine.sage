r"""A conjugate is formed from its pair, and its engine is realized when it is asked.

$O(U)$ of the hyperbolic plane is an infinite matrix group: the library selects
no group engine for it, so no conjugation in it is computed by one.  The action
is defined all the same, because a conjugate is the pair (subgroup, element),
which the construction states and the engine representation realizes only when
an operation asks for it.  Conjugating by an element and then by its inverse is
therefore the identity on the subgroup, and both answers are formed without an
engine.

An engine realized at construction instead refuses the whole operation:
$O(U)$ of an indefinite lattice is not the definite integral group an engine is
selected for.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_conjugate_is_formed_without_an_ambient_engine() -> None:
    r"""$g^{-1}.(g.H) = H$ in $O(U)$, whose isometries no engine realizes."""
    plane = Lattices(ZZ)("U")
    isometries = plane.O()
    labels = plane.module_generating_set()
    first, second = plane.module_generators()
    swap = isometries({labels[0]: second, labels[1]: first})
    reflection = isometries({labels[0]: -first, labels[1]: second})
    subgroup = isometries.subgroup((reflection,))

    conjugate = isometries.conjugate_subgroup(swap, subgroup)

    assert isometries.conjugate_subgroup(~swap, conjugate) is subgroup
    assert conjugate.conjugated_subgroup() is subgroup
    assert conjugate.conjugator() == swap
