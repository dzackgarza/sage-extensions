"""Original mathematical acceptance for research issue #388.

Run with ``sage -python tests/research_issue_388_acceptance.py`` from the
repository root.  This entry point deliberately executes the original public
construction assertions against one named checkout; source changes and
parent-only probes do not substitute for these mathematical assertions.
"""

from __future__ import annotations

import os
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]


def load_tests(relative_path: str) -> dict[str, object]:
    path = ROOT / relative_path
    namespace: dict[str, object] = {"__file__": str(path), "__name__": "__issue_388_acceptance__"}
    # The repository's .sage test files rely on Sage's usual test-runner
    # prelude, which imports the public owned API before defining assertions.
    # `exec` does not supply that prelude automatically.
    exec("from sage_extensions.all import *", namespace)
    exec(compile(path.read_text(), str(path), "exec"), namespace)
    return namespace


def run_test(namespace: dict[str, object], name: str, start: float) -> None:
    test = namespace[name]
    assert callable(test), f"acceptance assertion {name} is not callable"
    print(f"BEGIN {name}", flush=True)
    test()
    print(f"PASS {name} elapsed={perf_counter() - start:.2f}s", flush=True)


def main() -> None:
    start = perf_counter()
    print(
        "ISSUE_388_TARGET_REVISION="
        f"{os.environ.get('ISSUE_388_TARGET_REVISION', os.environ.get('GITHUB_SHA', 'local-unpinned'))}",
        flush=True,
    )

    named = load_tests("tests/lattices/test_named_lattice_constructions.sage")
    run_test(named, "test_the_dolgachev_pinkham_dual_lattice_retains_its_metric_form", start)

    hyperbolic = load_tests("tests/lattices/test_hyperbolic_root_lengths_and_vinberg.sage")
    run_test(hyperbolic, "test_hyperbolic_refinement_preserves_both_signature_conventions", start)

    two_elementary = load_tests("tests/lattices/test_two_elementary.sage")
    run_test(two_elementary, "test_two_elementary_catalogue_realizes_requested_invariants", start)
    from sage_extensions.catalogue import TwoElementary

    print("BEGIN TwoElementary.validate (all 75 rows)", flush=True)
    TwoElementary.validate()
    print(f"PASS TwoElementary.validate rows={len(TwoElementary)} elapsed={perf_counter() - start:.2f}s", flush=True)

    sterk = load_tests("tests/lattices/test_sterk_elliptic_population_archive.sage")
    for name in (
        "test_sterk_connected_elliptic_populations_match_the_committed_archive",
        "test_sterk_diagram_vertices_keep_the_zero_based_root_labels",
        "test_sterk_connected_elliptic_subdiagrams_have_the_recorded_types",
    ):
        run_test(sterk, name, start)

    ade = load_tests("tests/schemes/test_ade_pair_boundary_decomposition.sage")
    ade_tests = sorted(
        name for name, value in ade.items()
        if name.startswith("test_") and callable(value)
    )
    for name in ade_tests:
        run_test(ade, name, start)

    toric = load_tests("tests/schemes/test_toric_schemes.sage")
    for name in (
        "test_smooth_full_dimensional_cone_coefficients_are_dual_ray_pairings",
        "test_singular_rank_two_cone_coefficients_reconstruct_hilbert_generators",
        "test_overlap_characters_stay_in_the_selected_face_localization",
    ):
        run_test(toric, name, start)

    print(f"ISSUE_388_ACCEPTANCE=PASS elapsed={perf_counter() - start:.2f}s", flush=True)


if __name__ == "__main__":
    main()
