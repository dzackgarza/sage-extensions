r"""The line cusps of `Otilde(T_Co)` carry one divided-class partition.

A line cusp is a `Gamma`-orbit of primitive isotropic lines, and an element of
`Gamma = ker rho` acts trivially on `A_L`, so the divided class of a primitive
vector is constant on the orbit: the cusp, not its representative, decides that
class.  The partition of the cusps by divided class is therefore a function of
the lattice and the subgroup, and computing it twice in one process must answer
the same partition.

It does not.  The cusp row is walked with a breadth-first transversal whose
representatives, and the partition they induce, vary between computations; a run
can also raise in the walk's own order assertion.  This test is the witness, and
it is the reason no count that reads a line-cusp key can be trusted yet.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _line_cusp_partition(lattice, subgroup):
    r"""The number of line cusps carrying each divided class pair, as a tuple.

    The class pair of a cusp is `{c, -c}` for the divided class `c` of a
    generator of any line of it, and it is the same for every line of the cusp.
    """
    quotient = subgroup.finite_character_quotient()
    counts = {}
    for cusp in subgroup.cusps(1):
        line = cusp.representative()
        label = next(iter(line.module_generating_set()))
        vector = line.inclusion()(line.module_generator(label))
        divided = lattice.divided_discriminant_class(vector)
        pair = frozenset([divided, -divided])
        counts[pair] = counts.get(pair, 0) + 1
    return quotient, tuple(sorted(counts.values(), reverse=True))


def test_the_line_cusps_of_the_coble_lattice_carry_one_partition():
    lattice = NamedLattices.Tco
    subgroup = lattice.stable_orthogonal_group()
    _quotient, first = _line_cusp_partition(lattice, subgroup)
    subgroup.cusps.clear_cache()
    _quotient, second = _line_cusp_partition(lattice, subgroup)
    assert first == second, (
        f"the line cusps' divided-class partition is not one partition: {first} "
        f"then {second}"
    )
