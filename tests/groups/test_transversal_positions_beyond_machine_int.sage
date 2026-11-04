r"""Coset positions are read at GAP's index width, not a machine int's.

``GapElement_List.__getitem__`` binds its index with ``cdef int``, so any
position at or beyond ``2**31`` raises ``OverflowError: value too large to
convert to int`` even though it names a real entry.  The Enriques stable-kernel
computation reaches exactly that: the right transversal of ``O(A_N)`` has index
``|O(A_N)| = 46998591897600``, and the Schreier family of a kernel into that
finite group is enumerated over positions in that range.  ``_TransversalCosets``
reads its entries through GAP's ``ELM_LIST``, which takes the index as a GAP
integer.

These tests pin both halves: the helper agrees with Sage's own list access on
every position a machine int can hold, and it answers a position beyond that
bound where the Sage access raises.
"""

from sage.all import libgap

from sage_extensions.categories.group.groups import (
    Groups,
    _gap_list_entry,
)


def test_the_entry_helper_agrees_with_sage_list_access_on_machine_int_positions() -> None:
    r"""Same entries, same zero-based convention, on a list small enough for both."""
    entries = libgap.eval("[ 10, 20, 30, 40 ]")
    for position in range(4):
        assert _gap_list_entry(entries, position) == entries[position]
    # the zero-based convention is the retained one, and it is not off by one
    assert _gap_list_entry(entries, 0) == 10
    assert _gap_list_entry(entries, 3) == 40


def test_a_negative_position_is_refused_by_the_helper() -> None:
    r"""No silent wrap-around: a negative position is not a list position."""
    entries = libgap.eval("[ 10, 20, 30 ]")
    try:
        _gap_list_entry(entries, -1)
    except IndexError:
        pass
    else:
        raise AssertionError("a negative position must be refused")


def test_a_position_beyond_the_machine_int_range_is_read_by_gap() -> None:
    r"""``2**31 + 5`` reads through the helper and raises through ``__getitem__``.

    The list is a compact GAP range of length ``3*10**9``, so the position is
    a genuine one and the memory cost is GAP's, not the test's.
    """
    big = libgap.eval("[ 1 .. 3000000000 ]")
    position = 2**31 + 5
    assert int(_gap_list_entry(big, position)) == position + 1
    try:
        big[position]
    except OverflowError:
        pass
    else:
        raise AssertionError(
            "Sage's list access is expected to raise on this position; if it "
            "no longer does, the helper is still correct but this pin is obsolete"
        )


def test_a_finite_coset_space_still_reads_its_representatives_and_actions() -> None:
    r"""The ordinary coset arithmetic is unchanged: representatives and the action agree with the group law."""
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    cosets = group.left_cosets(subgroup)
    assert int(cosets.cardinality()) == 3
    for point in cosets:
        representative = point.representative()
        assert cosets.coset_of(representative) == point
    for element in group:
        for point in cosets:
            assert cosets.act(element, point) == cosets.coset_of(element * point.representative())


def test_rendering_a_coset_never_computes_a_representative() -> None:
    r"""``repr`` of a coset point is cheap and infallible, so it cannot mask an error.

    A coset's representative needs ``PreImagesRepresentative`` on the transversal.
    When reporting an exception whose message names a coset, that computation ran
    inside ``repr`` and replaced the real error — which is how a ``KeyError``
    about an intersection subgroup was reported as an ``OverflowError``.  The
    rendered form therefore names the position and the subgroup only, and a
    representative that raises must not affect it.
    """
    group = Groups.S(3)
    subgroup = group.subgroup((group((1, 2)),))
    cosets = group.left_cosets(subgroup)
    point = next(iter(cosets))

    rendered = repr(point)
    assert "coset" in rendered, rendered

    original = type(point).representative

    def refusing(self):
        raise RuntimeError("repr must not compute a representative")

    try:
        type(point).representative = refusing
        assert repr(point) == rendered
    finally:
        type(point).representative = original

    # the representative itself still works after rendering
    assert cosets.coset_of(point.representative()) == point
