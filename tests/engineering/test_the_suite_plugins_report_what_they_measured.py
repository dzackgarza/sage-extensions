r"""The suite's plugins report what they measured, and the run still runs its tests.

``pyproject.toml`` loads ``sage_extensions.testing.suite_budget`` and
``sage_extensions.testing.test_lint`` into every run of ``tests/``.  Each ended
the run from its own hook, before the first selected test ran: a collection
over its ceiling, or one lint finding anywhere in the tree, produced a run that
reported that and none of the tests those commands had selected.  These ask for
the counts a reader wants instead.

The ceilings are ini settings, so the gate here is breached by stating a
ceiling of zero seconds in the probe's own configuration, not by making a
collection slow: the illustration holds whatever the host's speed.
"""


def test_a_collection_over_its_ceiling_still_runs_the_selected_tests():
    tree = {"test_the_first_probe.py": "def test_the_first_probe():\n    assert 1 + 1 == 2\n"}

    run = probe_run(
        tree,
        "-p", "sage_extensions.testing.suite_budget",
        "-o", "time_gate_collection_ceiling=0",
    )

    assert run.outcomes == {"test_the_first_probe.py::test_the_first_probe": "passed"}
    assert run.exit_status == 1
    assert "collection took" in run.transcript
    assert "the measured ceiling is 0 s" in run.transcript


def test_a_lint_finding_fails_the_tests_of_the_file_that_holds_it():
    tree = {
        "test_a_probe_that_keeps_the_standard.py": (
            "def test_a_probe_that_keeps_the_standard():\n    assert 1 + 1 == 2\n"
        ),
        "test_a_probe_that_ignores_the_standard.py": (
            "def test_a_probe_that_ignores_the_standard():\n    assert True\n"
        ),
    }

    run = probe_run(tree, "-p", "sage_extensions.testing.test_lint")

    assert run.outcomes == {
        "test_a_probe_that_keeps_the_standard.py::test_a_probe_that_keeps_the_standard": "passed",
        "test_a_probe_that_ignores_the_standard.py::test_a_probe_that_ignores_the_standard": "failed",
    }
    assert run.exit_status == 1
    assert any(
        "test_a_probe_that_ignores_the_standard.py" in message and "TL09" in message
        for message in run.messages
    )
