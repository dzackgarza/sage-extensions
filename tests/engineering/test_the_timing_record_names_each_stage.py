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
    assert all(record["input"] for record in written.records)


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
        "-o", "log_file=pytest.log",
        "-o", "log_file_level=DEBUG",
        "-p", "sage_extensions.testing.timing_record",
    )

    assert "a debug record" in run.log

