r"""The subgroup of ``H <= O(M)`` that extends along a finite-index ``M -> L``.

``M = U(2)`` has basis ``e', f'`` with ``b(e', f') = 2``, and ``j: M -> U``,
``e' |-> 2e``, ``f' |-> f``, preserves the form, with index two.  Then
``M^# = ZZ f'/2 + ZZ e'/2 = ZZ e + ZZ f/2`` contains ``U``, and
``U/M = <e> = <e'/2>`` has order two in ``A_M`` of order four.

- ``H = <s>``, ``s`` the swap ``e' <-> f'``.  Rationally ``s`` sends ``e``
  to ``f/2``, which is not in ``U``, so ``s`` does not extend; in ``A_M`` it
  moves ``e'/2`` to ``f'/2`` and does not stabilize ``U/M``.  The extended
  subgroup is trivial.
- ``H = <-1>``.  ``-1`` preserves ``U`` and extends to ``-1`` on ``U``, so
  the extended subgroup has order two.

These specimens passed final-runtime execution on 2026-10-19.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _index_two_inclusion():
    plane = NamedLattices.U
    e, f = plane.module_generators()[0], plane.module_generators()[1]
    scaled = plane.twist(2)
    inclusion = scaled.Emb(plane)({0: 2 * e, 1: f})
    return plane, scaled, inclusion


def test_the_glue_of_U2_in_U_has_order_two() -> None:
    plane, scaled, inclusion = _index_two_inclusion()
    assert inclusion.index() == 2
    assert scaled.discriminant_group().cardinality() == 4
    assert inclusion.gluing_subgroup().cardinality() == 2


def test_the_swap_of_U2_does_not_extend_to_U() -> None:
    plane, scaled, inclusion = _index_two_inclusion()
    e_prime, f_prime = scaled.module_generators()[0], scaled.module_generators()[1]
    swap = scaled.Aut()({0: f_prime, 1: e_prime})
    assert inclusion.isometry_extends(swap) is False
    swaps = scaled.O().subgroup(Set((swap,)))
    assert inclusion.extended_subgroup(swaps).cardinality() == 1


def test_minus_one_on_U2_extends_to_minus_one_on_U() -> None:
    plane, scaled, inclusion = _index_two_inclusion()
    e, f = plane.module_generators()[0], plane.module_generators()[1]
    negation = scaled.Aut()(lambda label: -scaled.module_generator(label))
    assert inclusion.isometry_extends(negation) is True
    extension = inclusion.isometry_extension(negation)
    assert extension(e) == -e and extension(f) == -f
    signs = scaled.O().subgroup(Set((negation,)))
    assert inclusion.extended_subgroup(signs).cardinality() == 2


def test_public_orthogonal_group_exact_isometry_iterator_is_not_a_generator_claim():
    lattice = Lattices(ZZ)([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, -6, 0], [0, 0, 0, -6]])
    stream = lattice.O().exact_isometry_iterator()
    elements = (next(stream), next(stream), next(stream))
    assert elements[0] != elements[1] and elements[0] != elements[2] and elements[1] != elements[2]
    for element in elements:
        assert element in lattice.O()
        assert all(lattice.b(element(x), element(y)) == lattice.b(x, y)
                   for x in lattice.module_generators() for y in lattice.module_generators())


def test_public_low_witt_fixed_norm_orbit_stream_returns_primitive_exact_vector():
    lattice = Lattices(ZZ)([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, -6, 0], [0, 0, 0, -6]])
    representative = next(lattice.O().exact_vector_orbit_iterator(2, primitive_only=True))
    assert representative.q() == ZZ(2)
    assert representative.content() == ZZ(1)
