r"""S3/H is the three-point action for H=Stab(1), a nonnormal subgroup.

A3 acts transitively. H fixes the first coset and exchanges the other
two. Coset transporters must give these decisions and inverse witnesses.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("transitive", (True, False), ids=("alternating", "stabilizer"))
def test_subgroup_transporters_on_nonnormal_left_cosets(transitive):
    group = Groups.S(3)
    subgroup = group.subgroup((group((2, 3)),))
    acting = group.subgroup((group((1, 2, 3)),)) if transitive else subgroup
    inclusion = acting.inclusion()
    representatives = (group.one(), group((1, 2)), group((1, 3)))
    for source in representatives:
        for target in representatives:
            witness = FiniteGSets(acting).transporter_on_left_cosets(subgroup, source, target, inclusion)
            expected = transitive or ((source(1) == 1) == (target(1) == 1))
            if not expected:
                assert witness is None
            else:
                lifted = inclusion(witness)
                assert ~target*lifted*source in subgroup
                assert ~source*(~lifted)*target in subgroup
