r"""S3 acts transitively on three letters and fixes a fourth letter.

A transporter exists exactly when the endpoints lie in the same orbit.
Its inverse carries the target back to the source.
"""

from sage_extensions.all import *


def test_exact_transporters_in_the_three_letter_and_fixed_orbits():
    group = Groups.S(3)

    def action(element, point):
        return point if point == 4 else element(point)

    for source in (ZZ(1), ZZ(2), ZZ(3), ZZ(4)):
        for target in (ZZ(1), ZZ(2), ZZ(3), ZZ(4)):
            witness = FiniteGSets(group).transporter_from_finite_orbit(source, target, action)
            if (source == 4) != (target == 4):
                assert witness is None
            else:
                assert action(witness, source) == target
                assert action(~witness, target) == source
