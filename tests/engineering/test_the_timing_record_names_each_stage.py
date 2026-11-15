r"""The timing record of a stage-timed call is readable, in order, with its wall times.

A timing question — which stage of the isotropic orbit row costs the hour — is
answered by reading the record of a run that already happened
(:mod:`sage_extensions.timing`, ``CONTRIBUTING.md`` ENV-03).  That is only true
if the record exists, names the stages in the order the call ran them, and
carries a wall time each, so this makes one stage-timed call on a small lattice
and reads the records back off the record file.

The lattice is ``L_1 = U + U + <-2>``, whose ``Otilde`` line row the suite
already computes in a second; the call is the subgroup row of
``isotropic_orbit_representatives``, which the ambient row, the discriminant
image and the coset splitting all run inside.

The order asserted is the order the run *wrote* the lines, which is the order
the stages ended: a stage's line carries its wall time, so the outermost one is
written last.
"""

from sage_extensions.all import *


def _small_lattice():
    r"""``L_1 = U + U + <-2>``, rank five, signature ``(2, 3)``, ``A_L = Z/2``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def test_a_stage_timed_call_writes_its_stage_records_in_order_with_their_durations():
    lattice = _small_lattice()
    records = stage_records_of(
        lambda: lattice.stable_orthogonal_group().isotropic_orbit_representatives(1)
    )

    assert tuple(record["stage"] for record in records) == (
        "discriminant image",
        "ambient O(L) row",
        "coset splitting and transport",
        "isotropic orbit representatives",
    )
    assert all(record["outcome"] == "returned" for record in records)
    assert all(record["seconds"] >= 0 for record in records)
    assert all(record["input"] for record in records)


def test_a_run_keeps_its_report_log_and_its_junit_file():
    kept = archived_test_run(
        {
            "tests/.report/run.jsonl": "",
            "test_the_probe.py": "def test_the_probe():\n    assert 1 + 1 == 2\n",
        },
        "--report-log=tests/.report/run.jsonl",
        "--junit-xml=tests/.report/junit.xml",
    )

    assert kept == ("junit", "run")
