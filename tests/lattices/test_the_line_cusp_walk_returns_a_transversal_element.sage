r"""The line-cusp walk of `Otilde(T_Co)` returns a transversal, or says it cannot.

`_iter_splitting_isometries_in_im_rho_from_image` walks the `im rho`-orbit of a
point and carries, beside every point it reaches, the engine element that carries
the start to it.  The check that this element really does carry the start is an
assertion, not a fallback:

    reached = generator * reached_element
    if setwise_action(point, reached) != image:
        reached = reached_element * generator
        assert setwise_action(point, reached) == image, (
            "the orbit walk's transversal element does not carry the start to the
            reached point"
        )

On `Otilde(T_Co)` the assertion fires, and not always: a process either walks the
527 line cusps or raises there.  That is a separate defect from the partition's
dependence on the process -- it is the walk losing its own invariant -- and it is
red-tested on its own so a repair of the partition cannot hide it.

The witness is the cusp count in fresh processes: a process that raises fails the
test with its own stderr, and one that walks answers 527, the double-coset count
of Dutour Sikiric--Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def line_cusp_count():
    r"""The number of line cusps of `Otilde(T_Co)`, as an integer."""
    lattice = NamedLattices.Tco
    subgroup = lattice.stable_orthogonal_group()
    return int(sum(1 for _ in subgroup.cusps(1)))


@pytest.mark.timeout(1200)
def test_the_line_cusp_walk_returns_a_transversal_in_every_process():
    counts = in_fresh_processes(line_cusp_count, [1, 2, 3, 4])
    assert counts == (527, 527, 527, 527), (
        f"the line-cusp walk did not answer the double-coset count in every "
        f"process: {counts}"
    )
