r"""The timing record of a call is readable, and the library's logging still logs.

A timing question — which stage of the isotropic orbit row costs the hour — is
answered by reading the record of a run that already happened
(:mod:`sage_extensions.timing`, ``CONTRIBUTING.md`` ENV-03).  That is only true
if the record exists, names the commit and the run it came from, names the
stages in the order the call ran them, and carries a wall time each; so this
makes one stage-timed call on a small lattice and reads the record back off the
file, refusing a name the file does not have.

Two more facts are the library's own behaviour rather than the record's.  A
stage around a cached method must not cost the cache its argument
normalization: the same call spelled with its default keyword and without it is
one call, and the walk runs once.  And the logger the record is written through
must not quieten the logger its package already had: a DEBUG record of a child
logger still reaches the run's log file.

Two facts are about the run rather than the library.  A run keeps one record of
itself: ``pytest-xdist`` finishes a session in each worker's process, and the
report log and the JUnit file are the controller's.  And a stage names its input
without rendering it, because a rendering of a lattice is an invariant computed
for a log line.

The order asserted is the order the run *wrote* the lines, which is the order
the stages ended: a stage's line carries its wall time, so the outermost one is
written last.
"""

from sage_extensions.all import *


def _small_lattice():
    r"""``L_1 = U + U + <-2>``, rank five, signature ``(2, 3)``, ``A_L = Z/2``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def _hyperbolic_triangle():
    r"""``U + A1``: the triangle Vinberg's algorithm cuts out in three walls."""
    return HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("A1"))


def test_a_stage_timed_call_writes_its_stage_records_in_order_with_their_durations():
    r"""One call, four records, each naming the lattice by its rank and nothing computed.

    The lattice display states the signature, and reading it off the form is a
    congruence diagonalization: an invariant computed for a log line.  A stage
    names its input instead, so the four records carry the rank of the lattice
    the row was computed for, as the lattice states it.
    """
    lattice = _small_lattice()
    written = stage_records_of(
        lambda: lattice.stable_orthogonal_group().isotropic_orbit_representatives(1)
    )

    assert written.kind == "stages"
    assert written.suffix == "jsonl"
    assert written.commit == written.head[:12]
    assert all(record["commit"] == written.head for record in written.records)
    assert all(record["run"] == written.stamp for record in written.records)
    assert tuple(record["stage"] for record in written.records) == (
        "discriminant image",
        "ambient O(L) row",
        "coset splitting and transport",
        "isotropic orbit representatives",
    )
    assert all(record["outcome"] == "returned" for record in written.records)
    assert all(record["seconds"] >= 0 for record in written.records)
    assert tuple(record["input"] for record in written.records) == (
        "Integral lattice of rank 5",
    ) * 4


def test_the_vinberg_walk_runs_once_however_its_callers_spell_the_default_keyword():
    r"""Two callers, one walk: ``vinberg_simple_roots()`` names ``admits_root=None``.

    ``is_reflective()`` passes the same three arguments and no
    ``admits_root`` at all, so the two calls are one call — unless the stage
    the cached method carries has replaced its signature with
    ``(*arguments, **keywords)``, which is what the record counts here.
    """
    lattice = _hyperbolic_triangle()

    def walk_both_ways():
        lattice.vinberg_simple_roots()
        return lattice.is_reflective()

    written = stage_records_of(walk_both_ways)

    assert tuple(record["stage"] for record in written.records) == ("Vinberg walk",)


def test_a_debug_record_of_a_child_logger_reaches_the_run_log():
    r"""The package logger keeps the level and the propagation it had.

    ``tests/.report/pytest.log`` records DEBUG lines, and the library's own
    loggers write at that level; a library that sets its package logger to INFO
    and stops it propagating takes those lines out of the run's log, which is
    the only place a run's diagnostic record lives.
    """
    run = probe_run(
        {
            "test_the_probe.py": (
                "import logging\n"
                "\n"
                "\n"
                "def test_the_probe():\n"
                "    logging.getLogger('sage_extensions.categories.probe').debug('a debug record')\n"
                "    assert True\n"
            ),
        },
        "-o", "log_file_level=DEBUG",
        "-p", "sage_extensions.testing.timing_record",
    )

    assert "a debug record" in run.log


def test_a_run_keeps_the_files_its_own_options_name():
    r"""The plugin keeps what the run's options named, under this run's name.

    The probe run asks for a JUnit file of its own and is given its report log
    by ``probe_run``; both appear in the record directory named by the commit
    and by one start stamp, and the report log keeps the lines the run wrote.
    """
    kept = kept_test_run({"test_the_probe.py": "def test_the_probe():\n    assert 1 + 1 == 2\n"})

    assert tuple(entry.kind for entry in kept) == ("junit", "report")
    assert tuple(entry.suffix for entry in kept) == ("xml", "jsonl")
    assert all(entry.commit == entry.head[:12] for entry in kept)
    assert all(entry.stamp == kept[0].stamp for entry in kept)
    assert kept[1].records


def test_a_parallel_run_keeps_one_record():
    r"""``-n 2`` finishes a session in each worker, and keeps the run's record once.

    ``pytest-xdist`` runs the session hooks in every worker's own process, under
    a start stamp of its own, while the report log and the JUnit file are the
    controller's alone.  A worker that kept a copy too would file the
    controller's half-written log under a second name and fail on a JUnit file
    the run has not written — an assertion ``xdist`` swallows, leaving a green
    run beside a directory of records that are not runs.  One record, whatever
    the number of workers.
    """
    kept = kept_test_run(
        {"test_the_probe.py": "def test_the_probe():\n    assert 1 + 1 == 2\n"},
        "-n", "2",
    )

    assert tuple(entry.kind for entry in kept) == ("junit", "report")
    assert all(entry.stamp == kept[0].stamp for entry in kept)
