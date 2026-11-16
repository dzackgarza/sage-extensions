r"""A session file binds its own names, and loading one repairs the scope it loads into.

``from sage_extensions.all import *`` binds the session's names, and a star
import contributes no identifier to the parse's static bound-name scan: in such a
file a name the text binds nowhere may be one the session supplies.  The
upstream research dialect reads an unbound index in ``R = A[x]`` as a request for
a new generator and rewrites the assignment into a declaration.  In a file that
star-imports the session that reading can only be a guess, and the guess is wrong
in both directions: a name the session supplies would be rebuilt as a generator,
and a name the session does not supply would be created for the file rather than
reported.

The two specimen files under ``session_files/`` are what the tests load, because
the dialect's reading of a file is a question about a file: one writes a
subscript whose index is a session name, the other a subscript whose index the
file binds nowhere.  ``load`` is the session's own route into the dialect, so a
test that witnesses both readings also witnesses that route.

Loading also repairs the loading scope: the session's scalar names are written
into it, replacing whatever a script left under those names, which is asserted
here on the object the scope holds afterwards rather than on the name.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_a_subscript_of_a_session_name_builds_the_object_it_names() -> None:
    r"""The loaded set is the set of cardinality ``aleph0``, not a declaration of that name.

    The index is a session name, so the file builds the set of that cardinality
    and binds nothing of its own; the loaded scope holds the set.
    """
    scope: dict[str, object] = {}

    load("tests/foundations/session_files/a_countable_set.sage", scope)

    countable = scope["countable"]
    assert countable.cardinality() == aleph0


def test_a_subscript_of_a_name_the_file_does_not_bind_declares_no_generator() -> None:
    r"""Loading a file whose subscript names nothing new reports the absent name.

    The file star-imports the session, so ``t`` may have been bound by that
    import; the parse cannot know it is new, and a file is not the place to
    invent a binding for it.  Sage's own reading of the subscript reports the
    absent name, which is what the load raises.
    """
    with pytest.raises(NameError):
        load("tests/foundations/session_files/a_subscript_of_an_unwritten_name.sage", {})


def test_loading_repairs_the_scope_with_the_session_rings() -> None:
    r"""A scope that held something else under ``ZZ`` comes back holding the owned ring.

    ``load`` restores the session's scalar names into the scope it loaded into,
    so whatever a script left under one of them is replaced by the session's own
    object: the ring the scope holds afterwards is a principal ideal domain of
    the preamble, and it is the object the session name denotes.
    """
    scope: dict[str, object] = {"ZZ": 0}

    load("tests/foundations/session_files/a_countable_set.sage", scope)

    assert scope["ZZ"] in PrincipalIdealDomains()
    assert scope["ZZ"] == ZZ
