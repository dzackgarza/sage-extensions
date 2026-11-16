r"""A session file's two subscript readings, and the scope a load repairs.

``from sage_extensions.all import *`` binds the session's names, and a star import
contributes no identifier to the parse's static bound-name scan: in such a file an
index the file binds nowhere may still be a name the session supplies.  The two
specimen files under ``session_files/`` are what the tests load, because the
dialect's reading of a file is a question about a file: one writes an index that is
a session name, the other an index the file binds nowhere and that names nothing
the session publishes.

``load`` is the session's own route into the dialect, so a test that witnesses both
readings also witnesses that route.

Loading also repairs the loading scope: the session's scalar names are written
into it, replacing whatever a script left under those names, which is asserted
here on the object the scope holds afterwards rather than on the name.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_subscript_of_a_session_name_builds_the_object_it_names() -> None:
    r"""The loaded set is the set of cardinality ``aleph0``, not a declaration of that name.

    The index is a session name, so the file builds the set of that cardinality
    and binds nothing of its own; the loaded scope holds the set.
    """
    scope = {}

    load("tests/foundations/session_files/a_countable_set.sage", scope)

    countable = scope["countable"]
    assert countable.cardinality() == aleph0


def test_a_subscript_of_a_name_the_file_binds_nowhere_declares_a_generator() -> None:
    r"""A session file's unwritten subscript declares the generators it writes.

    The session publishes no ``t``, so ``QQ[t]`` in a file that binds ``t``
    nowhere is the polynomial ring written as it is written: the loaded scope
    holds the ring over ``QQ`` and ``t`` as its generator.
    """
    scope = {}

    load("tests/foundations/session_files/a_subscript_of_an_unwritten_name.sage", scope)

    declared = scope["declared"]
    assert declared in Rings()
    assert declared.base_ring() == QQ
    assert scope["t"] in declared
    assert scope["t"].parent() is declared


def test_loading_repairs_the_scope_with_the_session_rings() -> None:
    r"""A scope that held something else under ``ZZ`` comes back holding the owned ring.

    ``load`` restores the session's scalar names into the scope it loaded into,
    so whatever a script left under one of them is replaced by the session's own
    object: the ring the scope holds afterwards is a principal ideal domain of
    the preamble, and it is the object the session name denotes.
    """
    scope = {"ZZ": 0}

    load("tests/foundations/session_files/a_countable_set.sage", scope)

    assert scope["ZZ"] in PrincipalIdealDomains()
    assert scope["ZZ"] == ZZ
