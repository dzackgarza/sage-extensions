r"""One datum: a finite ordered set's hash is computed once and read after.

A finite ordered set is fixed by its points (the rule of
:class:`FiniteOrderedSets`), so its hash -- the hash of the tuple of its points,
which is what ``__eq__`` compares -- is a datum of the set and not a question the
set answers by rebuilding itself.  A reader does ask it repeatedly: the store
that keeps one product per equal family keys a family by its factors' hashes
(``SET-05``), so every request for a product asks each factor for its hash.

The set below reaches its points through a map, which is how a reader's sets
reach theirs -- an image is enumerated by its source through the map -- so its
enumeration is observable: the map records every point it is asked for.  Asking
for the hash a second time must record nothing new, because there is nothing new
to compute: the points are values and the set is fixed by them.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _image_set_recording_its_enumeration(record):
    r"""The image of $\{0,1,2,3\}$ under $n \mapsto n^2$, recording every ask.

    The points are reached through the map, as the image of a set of classes or
    of pairs is in the plane row; ``record`` collects the source points the map
    is asked about.
    """
    source = FiniteOrderedSets()((0, 1, 2, 3))

    def image(position):
        record.append(int(position))
        return ZZ(int(position) ** 2)

    def preimage(point):
        for position in (0, 1, 2, 3):
            if ZZ(position) ** 2 == point:
                return position
        return None

    return Sets().image_set(image, source, inverse=preimage)


def test_construction_computes_no_point_and_the_first_hash_computes_the_tuple() -> None:
    r"""Building the set asks its map for nothing; the first hash asks for every point."""
    record = []
    points = _image_set_recording_its_enumeration(record)

    assert tuple(record) == ()

    hash(points)

    assert tuple(record) == (0, 1, 2, 3)


def test_the_second_ask_for_a_hash_constructs_nothing() -> None:
    r"""Asked twice, the set answers with the one hash it computed, not a second walk."""
    record = []
    points = _image_set_recording_its_enumeration(record)
    hash(points)
    asked = tuple(record)

    hash(points)

    assert tuple(record) == asked


def test_equal_sets_hash_equally() -> None:
    r"""Two builds of one image are equal sets, so the retained hash agrees with ``==``."""
    left = _image_set_recording_its_enumeration([])
    right = _image_set_recording_its_enumeration([])

    assert left == right
    assert hash(left) == hash(right)
