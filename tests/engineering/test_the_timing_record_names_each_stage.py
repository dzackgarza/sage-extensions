r"""The timing record of a call is readable, and the library's logging still logs.

A timing question — which stage of the isotropic orbit row costs the hour — is
answered by reading the record of a run that already happened
(:mod:`sage_extensions.timing`, ``CONTRIBUTING.md`` ENV-03).  That is only true
if the record exists, names the commit and the run it came from, names the
stages in the order the call ran them, and carries a wall time each; so this
makes one stage-timed call on a small lattice and reads the record back off the
file, refusing a name the file does not have.

**What a record's identity is.**  Its run and its stage id.  Every line carries
``id``, unique within the run's file, and ``parent``, the ``id`` of the stage
that encloses it, so a reader tells two records apart and finds a stage's
sub-stages by these two fields and not by a name.  ``input`` is a description
instead: the owner's public description of what was computed — a lattice's ring
and Gram, the description a subgroup was built with, a vector's coordinates in
its lattice's basis, the keyword arguments the call was given — and two
computations may carry one name, which is why the tests below ask for a name to
describe its input and never for it to be unique.

Two more facts are the library's own behaviour rather than the record's.  A
stage around a cached method must not cost the cache its argument
normalization: the same call spelled with its default keyword and without it is
one call, and the walk runs once.  And the logger the record is written through
must not quieten the logger its package already had: a DEBUG record of a child
logger still reaches the run's log file.

Three facts are about the run rather than the library.  A run keeps one record
of itself: ``pytest-xdist`` finishes a session in each worker's process, and the
report log and the JUnit file are the controller's.  Two runs started in the same
second keep two records, because a record's name is its run's.  And a stage's ids
are the file's: one process writes one file, so its ids do not repeat, and a
stage's ``parent`` is the ``id`` of the record that encloses it.

The order asserted is the order the run *wrote* the lines, which is the order
the stages ended: a stage's line carries its wall time, so the outermost one is
written last.
"""

from sage_extensions.all import *


def _small_lattice():
    r"""``L_1 = U + U + <-2>``, rank five, signature ``(2, 3)``, ``A_L = Z/2``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def _cusp_lattice():
    r"""``<-2> + <-2> + U + U``: rank six, and ``O(A_L)`` of order two."""
    return Lattices(ZZ)([[-2, 0], [0, -2]]) + Lattices(ZZ)("U") + Lattices(ZZ)("U")


def _two_cusps():
    r"""Two isotropic lines of one lattice whose reductions have the same Gram."""
    lattice = _cusp_lattice()
    stable = lattice.stable_orthogonal_group()
    vectors = (
        lattice.basis_vector(2),
        lattice.basis_vector(2) + lattice.basis_vector(4),
    )
    return tuple(stable.isotropic_vector_reduction_image(vector) for vector in vectors)


def _record_named(records, stage_name):
    r"""The ``input`` one stage of a record wrote."""
    return next(record["input"] for record in records if record["stage"] == stage_name)


def _hyperbolic_triangle():
    r"""``U + A1``: the triangle Vinberg's algorithm cuts out in three walls."""
    return HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + Lattices(ZZ)("A1"))


def test_a_stage_timed_call_writes_its_stage_records_in_order_with_their_durations():
    r"""One call, four records, each naming the row, the lattice and the subgroup.

    The name is the caller's: the row's rank, the lattice's ring and Gram, and
    the subgroup the row is taken under, which is the description that subgroup
    was constructed with.  Nothing is read off an object and nothing is
    rendered, so the four records say what the run computed.
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
    # The three stages the subgroup's row wraps name the subgroup; the ambient
    # row inside them is the whole group's row, and says so.
    assert _record_named(written.records, "ambient O(L) row").endswith(" under O(L)")
    row_names = tuple(
        record["input"]
        for record in written.records
        if record["stage"] != "ambient O(L) row"
    )
    assert set(row_names) == {row_names[0]}
    assert row_names[0].startswith(
        "the rank-1 subobject row of the rank-5 lattice over Integer Ring of Gram "
    )
    assert " under the subgroup where " in row_names[0]


def test_the_two_rows_of_one_lattice_are_named_apart():
    r"""The ``Õ`` row and the ``Õ⁺`` row of one lattice carry two names.

    ``Õ(L)`` is the discriminant kernel and ``Õ⁺(L)`` its intersection with the
    spinor kernel, and the two rows are different computations of one lattice.
    Each row's name holds the description its subgroup states for itself
    (:meth:`sage_extensions.categories.group.groups.Subgroups.ParentMethods.description`)
    -- the preimage sentence, and the intersection sentence -- which is what a
    reader of the line is told about the group the row is taken under.
    """
    lattice = _small_lattice()
    stable = lattice.stable_orthogonal_group()
    positive = stable.intersection(lattice.O_plus())
    kernel_row = stage_records_of(lambda: stable.isotropic_orbit_representatives(1))
    positive_row = stage_records_of(lambda: positive.isotropic_orbit_representatives(1))

    kernel_name = _record_named(kernel_row.records, "discriminant image")
    positive_name = _record_named(positive_row.records, "discriminant image")

    assert stable.description() in kernel_name
    assert positive.description() in positive_name
    assert kernel_name != positive_name


def test_a_stage_record_carries_the_id_of_the_stage_that_encloses_it():
    r"""Three nested stages, each record carrying its own ``id`` and its parent's.

    A cusp chamber opens the walk of its subgroup, which asks for a point of its
    own, which runs the full group's walk: ``cusp chamber``, then ``controlling
    vector``, then a ``Vinberg walk`` inside it.  So the call's records are three
    levels deep, and each record's ``parent`` is the ``id`` of the record that
    encloses it, which a reader uses to find a stage's sub-stages.
    """
    cusp, _second = _two_cusps()
    written = stage_records_of(lambda: cusp.cusp_chamber(max_decompositions=20))

    identities = tuple(record["id"] for record in written.records)
    assert tuple(sorted(set(identities))) == tuple(sorted(identities))
    assert tuple(
        record["stage"] for record in written.records if record["parent"] is None
    ) == ("cusp chamber",)
    enclosing = {record["id"]: record["parent"] for record in written.records}
    assert all(parent is None or parent in enclosing for parent in enclosing.values())
    chamber = next(
        record["id"] for record in written.records if record["stage"] == "cusp chamber"
    )
    point = next(
        record["id"]
        for record in written.records
        if record["stage"] == "controlling vector"
    )
    assert enclosing[point] == chamber
    assert tuple(
        record["stage"]
        for record in written.records
        if record["parent"] == point
    ) == ("Vinberg walk",)


def test_an_integer_keyword_argument_is_named_not_refused():
    r"""``cusp_chamber(max_decompositions=ZZ(200))`` writes a record naming the bound.

    ``ZZ(200)`` is this library's integer and not Python's, and the keyword
    arguments are written by their own ``repr``, so the bound is in the name and
    no value is refused for its type.
    """
    cusp, _second = _two_cusps()
    written = stage_records_of(lambda: cusp.cusp_chamber(max_decompositions=ZZ(200)))

    assert "max_decompositions=200" in _record_named(written.records, "cusp chamber")
    assert all(record["outcome"] == "returned" for record in written.records)


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
    run = kept_test_run({"test_the_probe.py": "def test_the_probe():\n    assert 1 + 1 == 2\n"})
    kept = run.files

    assert run.probe.exit_status == 0
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
    run = kept_test_run(
        {"test_the_probe.py": "def test_the_probe():\n    assert 1 + 1 == 2\n"},
        "-n", "2",
    )
    kept = run.files

    assert run.probe.exit_status == 0
    assert tuple(entry.kind for entry in kept) == ("junit", "report")
    assert all(entry.stamp == kept[0].stamp for entry in kept)


def test_two_runs_started_together_keep_two_records():
    r"""Two runs begun in one second are two records, each holding its own test.

    The record's name is its run's: the start to the microsecond and the pid of
    the process that kept it.  A stamp to the second is one name for two runs, and
    then the second run's copy lands on the first run's file — one record, holding
    one of the two tests, with nothing to say that the other ever ran.  Both
    probes here are started before either is waited on, so they begin together.
    """
    files, probes = simultaneous_test_runs(
        {"test_the_first_probe.py": "def test_the_first_probe():\n    assert 1 + 1 == 2\n"},
        {"test_the_second_probe.py": "def test_the_second_probe():\n    assert 2 + 2 == 4\n"},
    )

    assert tuple(probe.exit_status for probe in probes) == (0, 0)
    assert tuple(entry.kind for entry in files) == ("junit", "junit", "report", "report")
    assert files[0].stamp != files[1].stamp
    assert files[2].stamp != files[3].stamp
    assert {
        tuple(sorted(
            {
                record["nodeid"] for record in entry.records
                if record.get("when") in ("setup", "call", "teardown")
            }
        ))
        for entry in files
        if entry.kind == "report"
    } == {
        ("test_the_first_probe.py::test_the_first_probe",),
        ("test_the_second_probe.py::test_the_second_probe",),
    }
