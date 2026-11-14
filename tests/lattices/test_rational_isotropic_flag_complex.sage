r"""The quotient flag complex of nU.

nU has one orbit of each flag type, because a primitive null flag has an
adapted hyperbolic basis. Forgetting terms of a chain satisfies d_i d_j = d_{j-1} d_i.
"""

from sage_extensions.all import *


def _terms(flag):
    return tuple(frozenset(term.inclusion()(point) for point in term.module_generators()) for term in flag.terms())


def test_complete_flags_of_three_hyperbolic_planes_have_consistent_faces():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    complex_ = RationalIsotropicFlagComplex(ambient.O())
    complete = FlagType((1, 2, 3))
    orbits = tuple(complex_.simplex_orbits(complete))
    assert len(orbits) == 1
    flag = orbits[0]
    assert tuple(flag.face(0).flag_type().dimensions) == (2, 3)
    assert tuple(flag.face(2).flag_type().dimensions) == (1, 2)
    for i, j in ((0, 1), (0, 2), (1, 2)):
        assert flag.face(j).face(i).flag_type() == flag.face(i).face(j - 1).flag_type()
        assert tuple(int(t.module_rank()) for t in flag.face(j).face(i).terms()) == tuple(int(t.module_rank()) for t in flag.face(i).face(j - 1).terms())
    representative, witness = complex_.face_map(flag, 1)
    face = flag.face(1)
    for source, target in zip(face.terms(), representative.terms(), strict=True):
        assert all(target.inclusion().is_in_image(witness(source.inclusion()(point))) for point in source.module_generators())
    assert complex_.incidence_multiplicity(complete, 1, representative) == 1
    for generator in complex_.face_stabilizer_image(flag, 1):
        for term in flag.face(1).terms():
            assert all(term.inclusion().is_in_image(generator(term.inclusion()(point))) for point in term.module_generators())
