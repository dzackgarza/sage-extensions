r"""The Mathieu ``M12`` automorphism group retained from the archive.

The *Atlas of Finite Groups* lists ``|M12| = 95040`` and outer automorphism
multiplicity ``2``.  Since ``M12`` is simple and centerless, conjugation
identifies ``M12`` with its inner automorphism subgroup, so the full
automorphism group has order ``190080`` and the inner subgroup has index two.
"""

from sage_extensions.all import *


def test_m12_inner_automorphisms_have_index_two_in_the_full_automorphism_group() -> None:
    group = Groups.Mathieu(12)
    conjugation = group.conjugation_morphism()
    automorphisms = group.Aut()

    assert group.order() == 95040
    assert conjugation.kernel().order() == 1
    assert conjugation.image().order() == 95040
    assert automorphisms.order() == 190080
    assert automorphisms.order() == 2 * conjugation.image().order()
