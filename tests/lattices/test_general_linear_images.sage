r"""The images in the isotropic stabilizer action generate GL_k(Z).

Surjection modulo 2 is checked against |GL_3(F_2)| = 168 and |GL_4(F_2)| = 20160, and modulo 3
against |GL_2(F_3)| = 48. Determinant -1 occurs because of the sign change.
"""

from sage_extensions.all import *
from sage.matrix.constructor import matrix as sage_matrix
from sage.matrix.special import identity_matrix as sage_identity
from sage.modules.free_module_element import vector as sage_vector
from sage.rings.finite_rings.finite_field_constructor import GF as SageGF
from sage.rings.integer_ring import ZZ as SageZZ
from sage_extensions.categories.isotropic_parabolics import general_linear_images


def _order(k, p):
    frame = tuple(sage_identity(SageZZ, int(k)).rows())
    field = SageGF(int(p))
    letters = [sage_matrix(field, [list(v) for v in images]) for images in general_linear_images(frame)]
    one = sage_identity(field, int(k))
    one.set_immutable()
    known = set([one])
    frontier = [one]
    while frontier:
        current = frontier.pop()
        for letter in letters:
            image = current * letter
            image.set_immutable()
            if image not in known:
                known.add(image)
                frontier.append(image)
    return len(known)


def test_images_surject_onto_general_linear_groups_over_finite_fields():
    assert _order(3, 2) == int(168)
    assert _order(4, 2) == int(20160)
    assert _order(2, 3) == int(48)


def test_rank_one_is_the_sign_change():
    v = sage_vector(SageZZ, [SageZZ(int(1))])
    assert general_linear_images((v,)) == ((-v,),)
