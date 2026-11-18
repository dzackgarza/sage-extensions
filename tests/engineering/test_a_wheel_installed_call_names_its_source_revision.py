r"""A wheel-installed library's timed call records its own revision where its owner keeps state.

A consumer installs the package as a wheel and calls a timed public orbit row —
the lattice database's certify jobs do, in the Sage image, where the package is
a directory of ``site-packages`` (:mod:`sage_extensions.timing`).  A record has
to answer two questions there, and neither may be answered by the consumer: which
revision of this library produced it, and where it is written.

**The revision is the wheel's.**  A package that is not a checkout has no git to
ask, so the revision it states is the one its build recorded beside it, and a
record naming the consumer's own commit — ``LATTICEDB_REVISION`` in that job —
would attribute this library's wall times to another repository's code.  The
revision read back here is checked against this checkout's commit, read by git
on the test side, and against the commit of the consumer tree the wheel was
installed into: the record names the first and not the second.

**The directory is the owner's.**  A checkout keeps its records in ``.timings/``
at its root.  An installation has no such root, so the records go to the
running user's own state directory, ``$XDG_STATE_HOME`` or ``~/.local/state``,
under ``sage-extensions/timings``: the place the XDG Base Directory Specification
sets aside for a program's state, and the same directory whatever the process
was started from — never the working directory, and never a path inside the
installed package.

The call is the smallest row that is still the reported operation: one
stage-timed ``isotropic_orbit_representatives(1)`` on ``L_1 = U + U + <-2>``,
whose discriminant kernel has one line orbit.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_timed_orbit_call_from_an_installed_wheel_names_the_revision_it_was_built_from():
    r"""Four stages, one revision, and a record directory its owner can find.

    The run imports the library from the installed wheel alone, states nothing
    about where its records go, and returns the row: one line orbit under the
    discriminant kernel of ``L_1``.  The record it leaves names the revision the
    wheel was built from — this checkout's commit — in every line, and sits in
    the record directory of the user running it,
    ``<home>/.local/state/sage-extensions/timings``, and never under the wheel or
    under the directory the call was made from.
    """
    written = installed_wheel_record()

    assert written.cardinality == 1
    assert written.directory_parts == (".local", "state", "sage-extensions", "timings")
    assert written.commit == written.revision
    assert written.commit != written.consumer
    assert all(record["commit"] == written.revision for record in written.records)
    assert tuple(record["stage"] for record in written.records) == (
        "discriminant image",
        "ambient O(L) row",
        "coset splitting and transport",
        "isotropic orbit representatives",
    )
    assert all(record["outcome"] == "returned" for record in written.records)
