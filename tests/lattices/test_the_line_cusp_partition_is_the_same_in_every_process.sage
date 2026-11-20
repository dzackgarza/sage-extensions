r"""The line cusps of `Otilde(T_Co)` carry one divided-class partition.

A line cusp is a `Gamma`-orbit of primitive isotropic lines, and `Gamma = ker rho`
acts trivially on `A_L`, so the divided class of a primitive vector is constant on
the orbit: the cusp -- and not the representative its walk happened to spell --
decides that class.  The multiplicities of the classes over the cusps are
therefore a function of the lattice and the subgroup, and two processes must
answer the same list.

They do not.  The walk's lifts are spelled in the ambient generating family
`O(L).group_generators()`, which is not canonical: it has 358 elements in one
process and 336 in another, so the same coset is spelled by a different word, its
lift is a different isometry, and the cusps the row yields are a different set of
representatives.  The multiplicities move with them.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def partitioned_line_cusps():
    r"""The multiplicities of the line cusps' divided classes, largest first.

    Each cusp contributes the class pair `{c, -c}` of its representative's
    divided class `c`, which the orbit fixes; the answer is a list of integers and
    so can be carried back from a fresh process.
    """
    lattice = NamedLattices.Tco
    subgroup = lattice.stable_orthogonal_group()
    counts = {}
    for cusp in subgroup.cusps(1):
        line = cusp.representative()
        label = next(iter(line.module_generating_set()))
        vector = line.inclusion()(line.module_generator(label))
        divided = lattice.divided_discriminant_class(vector)
        pair = frozenset([divided, -divided])
        counts[pair] = counts.get(pair, 0) + 1
    return sorted(counts.values(), reverse=True)


@pytest.mark.timeout(1200)
def test_the_line_cusp_partition_does_not_depend_on_the_process():
    first, second = in_fresh_processes(partitioned_line_cusps, [1, 2])
    assert first == second, (
        f"the line cusps' divided-class partition depends on the process: "
        f"{first[:12]} then {second[:12]}"
    )
