r"""Primitive vectors with a prescribed square and complement, one per ``O(T)``-orbit.

The fibre ``{delta in T : delta primitive, delta^2 = d, delta^perp = C}`` is
infinite in an indefinite ``T``, so it is never enumerated.  By Nikulin
(Prop. 1.15.1 and 1.5.1) its ``O(T)``-orbits are the primitive embeddings
``<d> perp C -> T`` of finite index, i.e. the gluing data of the overlattices of
``<d> perp C``, collapsed by ``O(<d>) x O(C)``; ``O(<d>)`` fixes every class of
``A_<d>`` and ``O(C)`` reaches ``A_C`` through ``rho_C: O(C) -> O(q_C)``, so the
collapse is a finite orbit computation on ``A_C`` and no vector of ``T`` is
searched for.

Two specimens.  The definite control is ``A2`` with ``square = 2`` and
complement ``<6>``: there the enumerated fibre is finite and its six vectors are
the six roots, one ``O(A2)``-orbit, reached from the returned vector by two
explicit isometries.  The consumer is the Enriques lattice ``T_En`` with
``square = -2`` and complement ``T_Co``, whose gluing has index two.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a2_control():
    r"""``A2`` with the complement ``<6>`` of one of its roots."""
    lattice = Lattices(ZZ)("A2")
    root = lattice.module_generators()[0]
    complement = lattice.orthogonal_complement(lattice.subobject_on([root]))
    return lattice, root, complement


def test_the_definite_control_agrees_with_the_enumerated_roots() -> None:
    r"""``A2``: one orbit, and the enumerated fibre reduces to it by explicit isometries."""
    lattice, root, complement = _a2_control()

    assert root.q() == ZZ(-2)
    assert complement.module_rank() == 1
    assert int(complement.determinant()) == -6

    # the enumerated fibre, finite because A2 is definite
    fibre = tuple(lattice.vectors_of_square_and_divisibility(ZZ(-2), ZZ(1)))
    assert sum(1 for _vector in fibre) == 6
    assert all(vector.is_primitive() for vector in fibre)

    found = tuple(lattice.vectors_of_square_with_complement(ZZ(-2), complement))
    assert sum(1 for _entry in found) == 1
    delta, isometry = found[0]

    assert delta.q() == ZZ(-2)
    assert delta.is_primitive() is True
    assert (
        lattice.orthogonal_complement(lattice.subobject_on([delta])).is_isometric_to(complement)
        is True
    )

    # the certificate: delta is the image of the <-2> summand's generator, so
    # its preimage in the overlattice has the prescribed square and is primitive
    preimage = isometry.inverse()(delta)
    assert preimage.q() == ZZ(-2)
    assert preimage.is_primitive() is True
    assert isometry.domain().module_rank() == lattice.module_rank()

    # reduced modulo O(A2): the two simple reflections generate the Weyl group,
    # they are isometries, and they carry the returned vector over the whole
    # enumerated fibre, so the fibre is one orbit
    labels = tuple(lattice.module_generating_set())
    first, second = (lattice.module_generator(label) for label in labels)

    def reflection(alpha):
        def image(label):
            vector = lattice.module_generator(label)
            return vector + lattice.b(vector, alpha) * alpha

        return lattice.Aut()(image)

    negation = reflection(first)
    swap = reflection(second)
    def key(vector):
        coordinates = vector.to_vector()
        return tuple(int(coordinates(label)) for label in labels)

    reached = [key(delta)]
    frontier = [delta]
    while frontier:
        current = frontier.pop()
        for isometry_of_lattice in (negation, swap):
            image = isometry_of_lattice(current)
            if key(image) not in reached:
                reached.append(key(image))
                frontier.append(image)
    assert sorted(reached) == sorted(key(vector) for vector in fibre)


def test_the_enriques_gluing_gives_a_vector_of_square_minus_two_with_complement_t_co() -> None:
    r"""The consumer: ``T_En``, ``square = -2``, ``complement = T_Co``, index two."""
    lattice = NamedLattices.TEn
    complement = NamedLattices.Tco
    pair_order = int((Lattices(ZZ)([[-2]]) + complement).discriminant_group().cardinality())
    lattice_order = int(lattice.discriminant_group().cardinality())
    assert pair_order // lattice_order == 4

    found = tuple(lattice.vectors_of_square_with_complement(ZZ(-2), complement))
    assert found

    for delta, isometry in found:
        assert delta.q() == ZZ(-2)
        assert delta.is_primitive() is True
        assert (
            lattice.orthogonal_complement(lattice.subobject_on([delta])).is_isometric_to(complement)
            is True
        )
        preimage = isometry.inverse()(delta)
        assert preimage.q() == ZZ(-2)
        assert preimage.is_primitive() is True
        assert isometry.domain().signature() == lattice.signature()
