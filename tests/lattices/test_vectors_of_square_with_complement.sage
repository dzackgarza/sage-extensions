r"""Primitive vectors with a prescribed square and complement, one per ``O(T)``-orbit.

The fibre ``{delta in T : delta primitive, delta^2 = d, delta^perp = C}`` is
infinite in an indefinite ``T``, so it is never enumerated.  By Nikulin
(Prop. 1.15.1 and 1.5.1) its ``O(T)``-orbits are the primitive embeddings
``<d> perp C -> T`` of finite index, i.e. the gluing data of the overlattices of
``<d> perp C``, collapsed by ``O(<d>) x O(C)``.

Each test below decides one item of the issue's acceptance on the smallest
input that decides it.  The definite control is ``A2``, whose cardinality is
card `0012`: the operation's orbit count at square ``-2`` is the card's ``O``
row at norm two, and the enumerated fibre is what that count reduces.  The
second definite control is ``<-2> perp <-2>``, whose complement ``<-2>`` has a
discriminant form of order two, where negating a class is the identity: the
collapse by ``O(C) = {+-1}`` is the identity there and the answer is still one
orbit.  The consumer is the Enriques lattice ``T_En`` with ``square = -2`` and
complement ``T_Co`` (Dolgachev--Kondo, Izv. Math. 77:3 (2013), section 3
equation (3.6), printed p. 513), whose gluing has index two.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a2_control():
    r"""``A2`` with the complement ``<6>`` of one of its roots."""
    lattice = Lattices(ZZ)("A2")
    root = lattice.module_generators()[0]
    complement = lattice.orthogonal_complement(lattice.subobject_on([root]))
    return lattice, root, complement


def _coordinates(vector, labels):
    r"""The coordinates of ``vector`` along the module generators ``labels``."""
    coordinates = vector.to_vector()
    return tuple(int(coordinates(label)) for label in labels)


def test_the_certificate_is_an_isometry_of_an_even_overlattice_of_the_prescribed_index() -> None:
    r"""Item 1: the vector, its square, its complement, and the certificate's index.

    The index the acceptance states is ``|A_<d> perp A_C|^(1/2) / |A_T|^(1/2)``,
    read here from the two cardinalities the library computes, and the
    certificate has to be an isometry of an even lattice whose own discriminant
    group makes exactly that index: ``|A_L| * index^2 = |A_<d> perp C|``.
    """
    lattice, _root, complement = _a2_control()
    pair_order = int((Lattices(ZZ)([[-2]]) + complement).discriminant_group().cardinality())
    lattice_order = int(lattice.discriminant_group().cardinality())
    assert pair_order % lattice_order == 0
    index_squared = pair_order // lattice_order
    assert ZZ(index_squared).is_square() is True
    index = ZZ(index_squared).sqrt()

    found = tuple(lattice.vectors_of_square_with_complement(ZZ(-2), complement))
    assert sum(1 for _entry in found) == 1
    delta, isometry = found[0]

    assert delta.q() == ZZ(-2)
    assert lattice.subobject_on([delta]).is_primitive() is True
    assert complement.is_isometric_to(lattice.orthogonal_complement(lattice.subobject_on([delta]))) is True

    overlattice = isometry.domain()
    assert isometry.codomain() is lattice
    assert overlattice.is_even() is True
    assert int(overlattice.discriminant_group().cardinality()) * index**2 == pair_order

    # the overlattice's <d> generator, which the isometry carries to delta
    preimage = isometry.inverse()(delta)
    assert preimage.q() == ZZ(-2)
    assert overlattice.subobject_on([preimage]).is_primitive() is True


def test_the_definite_control_agrees_with_the_card_row_of_its_orbits() -> None:
    r"""Item 2: the orbit count at square ``-2`` is card `0012`'s ``O`` count at norm two.

    The card's ``A2`` is the positive definite form ``[[2, -1], [-1, 2]]`` and
    this library's is the same form negated, so the card's ``z`` row, whose
    entries are the norms ``1, 2, 3, 4``, is the row of the squares
    ``-1, -2, -3, -4``.  The six roots the enumeration returns are the fibre
    that count reduces, and the two simple reflections of ``A2`` carry the
    returned vector over all of them.
    """
    lattice, _root, complement = _a2_control()
    row = card("primitive_orbit_series", "0012")["rows"]["O"]

    found = tuple(lattice.vectors_of_square_with_complement(ZZ(-2), complement))
    assert sum(1 for _entry in found) == row["z"][1]
    delta, _isometry = found[0]

    fibre = tuple(lattice.vectors_of_square_and_divisibility(ZZ(-2), ZZ(1)))
    assert fibre
    labels = tuple(lattice.module_generating_set())
    first, second = (lattice.module_generator(label) for label in labels)

    def reflection(alpha):
        def image(label):
            vector = lattice.module_generator(label)
            return vector + lattice.b(vector, alpha) * alpha

        return lattice.Aut()(image)

    reached = [delta]
    frontier = [delta]
    while frontier:
        current = frontier.pop()
        for isometry_of_lattice in (reflection(first), reflection(second)):
            image = isometry_of_lattice(current)
            if _coordinates(image, labels) not in [_coordinates(vector, labels) for vector in reached]:
                reached.append(image)
                frontier.append(image)
    assert sorted(_coordinates(vector, labels) for vector in reached) == sorted(
        _coordinates(vector, labels) for vector in fibre
    )


def test_a_rank_one_complement_of_order_two_collapses_by_its_own_negation() -> None:
    r"""Item 2 on ``<-2> perp <-2>``: the complement's negation is the identity.

    ``A_<2>`` has order two, so the only class it carries is its own negation
    and the collapse by ``O(<6>) = {+-1}`` -- which is ``rho_C(O(C))`` for a
    rank one ``C`` -- is the identity.  The enumerated fibre is four vectors and
    the transposition of the two summands, a genuine isometry of ``<-2> perp
    <-2>``, carries the returned vector over all of them, so the fibre is one
    orbit and the operation returns one vector.
    """
    lattice = Lattices(ZZ)([[-2, 0], [0, -2]])
    complement = Lattices(ZZ)([[-2]])
    assert int(complement.discriminant_quadratic_form().cardinality()) == 2

    found = tuple(lattice.vectors_of_square_with_complement(ZZ(-2), complement))
    assert sum(1 for _entry in found) == 1
    delta, _isometry = found[0]
    assert delta.q() == ZZ(-2)
    assert complement.is_isometric_to(lattice.orthogonal_complement(lattice.subobject_on([delta]))) is True

    labels = tuple(lattice.module_generating_set())
    first, second = (lattice.module_generator(label) for label in labels)

    def transposition(label):
        return second if label == labels[0] else first

    transpose = lattice.Aut()(transposition)
    reached = (delta, -delta, transpose(delta), -transpose(delta))
    fibre = tuple(lattice.vectors_of_square_and_divisibility(ZZ(-2), delta.div()))
    assert sorted(_coordinates(vector, labels) for vector in reached) == sorted(
        _coordinates(vector, labels) for vector in fibre
    )


def test_the_enriques_gluing_gives_a_vector_of_square_minus_two_with_complement_t_co() -> None:
    r"""Item 3: the consumer specimen, ``T_En`` with ``square = -2`` and complement ``T_Co``.

    ``< -2 > perp T_Co`` sits in ``T_En`` with index two, so the gluing is one
    index-two overlattice and the acceptance asks for at least one orbit.  Each
    returned vector is the certificate's image, and its complement is ``T_Co``.
    """
    lattice = NamedLattices.TEn
    complement = NamedLattices.Tco
    pair_order = int((Lattices(ZZ)([[-2]]) + complement).discriminant_group().cardinality())
    lattice_order = int(lattice.discriminant_group().cardinality())
    assert pair_order % lattice_order == 0
    assert ZZ(pair_order // lattice_order).is_square() is True
    index = ZZ(pair_order // lattice_order).sqrt()

    found = tuple(lattice.vectors_of_square_with_complement(ZZ(-2), complement))
    assert found

    for delta, isometry in found:
        assert delta.q() == ZZ(-2)
        assert lattice.subobject_on([delta]).is_primitive() is True
        assert complement.is_isometric_to(lattice.orthogonal_complement(lattice.subobject_on([delta]))) is True
        assert isometry.domain().signature() == lattice.signature()
        assert int(isometry.domain().discriminant_group().cardinality()) * index**2 == pair_order
        preimage = isometry.inverse()(delta)
        assert preimage.q() == ZZ(-2)
        assert isometry.domain().subobject_on([preimage]).is_primitive() is True
