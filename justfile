# sage-extensions — the mathematical library behind the research session.
#
# QC delegates to ~/ai-review-ci/justfiles/sage.just. Project-specific recipes
# below are non-QC entry points or narrow repo orchestration.

# ai-review-ci contract variables consumed by doctor and workflow installers.
ai_review_ci_schema_version := "1"
ai_review_ci_profile := "sage"
ai_review_ci_ref := "main"
ai_review_ci_release_channel := "main"
ai_review_ci_workflow_template_version := "1"
ai_review_ci_local_delegation := "global-justfile"
ai_review_ci_default_branch := "main"

# List available recipes
default:
    @just --list

# Development commits inspect staged source syntax only. The repository-owned
# coordinate-ownership scan is retained as an independent CI diagnostic.
test-commit:
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-commit

# No full-tree scan on the publication path.
test-push:
    @just -f ~/ai-review-ci/justfiles/sage.just -d . test-push

# Run CI suites and the repository-owned tensor-ownership detector independently,
# retaining both in one nonblocking findings/burndown report.
test-ci:
    @python3 ~/ai-review-ci/scripts/ci-triage.py sage --caller-check sage-extensions-tensor-boundary tensor-boundary

# The scheduled whole-tree audit includes the tensor-ownership detector.
ambient:
    @python3 ~/ai-review-ci/scripts/ci-triage.py sage --tier ambient --caller-check sage-extensions-tensor-boundary tensor-boundary

# CI-only provision for the repository-specific scanner, not a local hook.
_ci-tensor-tools:
    #!/usr/bin/env bash
    set -euo pipefail
    prefix="$RUNNER_TEMP/sage-extensions-tensor-tools"
    npm install --prefix "$prefix" --no-audit --no-fund @ast-grep/cli@0.41.0
    printf '%s\n' "$prefix/node_modules/.bin" >> "$GITHUB_PATH"

# Detect coordinate conventions written outside the tensor package (OWN-24).
# AST provenance, not identical source-line text, exempts the typed Mor
# transpose. Encoding Smith coordinates as ordinal indices is not a pairing.
# The scan is necessary but not sufficient: semantic ownership needs review.
# scope=staged is an optional focused check; scope=all is the CI diagnostic.
tensor-boundary scope="all":
    #!/usr/bin/env bash
    set -uo pipefail
    case "{{scope}}" in
        all) files=$(git ls-files 'src/sage_extensions/*.py' \
            | grep -v '^src/sage_extensions/tensors/') || exit 1 ;;
        staged) files=$(git diff --cached --name-only --diff-filter=ACMR -- 'src/sage_extensions/*.py' \
            | grep -v '^src/sage_extensions/tensors/')
            if [ -z "$files" ]; then
                echo "tensor-boundary: no staged sage_extensions Python files."
                exit 0
            fi ;;
        *) echo "tensor-boundary scope must be all or staged, not {{scope}}" >&2; exit 2 ;;
    esac
    total=0
    for pattern in '$X.transpose()' '$X.T' '$X.matrix_action_right($$$A)' '$X.matrix_action_left($$$A)' '$X.einsum($$$A)' 'einsum($$$A)' '$X.matmul($$$A)' 'matmul($$$A)' '$X.dot($$$A)' '$X @ $Y'; do
        matches=$(ast-grep run --lang python --pattern "$pattern" --json $files)
        status=$?
        # ast-grep returns 1 for a valid query with zero matches.
        if [ "$status" -gt 1 ]; then
            echo "tensor-boundary scanner failed (status $status) for $pattern" >&2
            exit "$status"
        fi
        if ! findings=$(printf '%s\n' "$matches" | python3 -c '
    import ast, json, pathlib, sys
    for hit in json.load(sys.stdin):
        path = hit["file"]
        line = hit["range"]["start"]["line"] + 1
        source = pathlib.Path(path).read_text()
        tree = ast.parse(source, filename=path)

        # The owned MatrixSpaces.ElementMethods implementation makes product
        # by composing two elements of the module Mor. Its transpose is a Mor
        # element with reversed endpoints, not a Sage-matrix convention.
        if (path == "src/sage_extensions/categories/modules/pure/modules.py"
                and hit["text"] == "product.transpose()"):
            owned_transpose = False
            for method in ast.walk(tree):
                if not isinstance(method, ast.FunctionDef) or method.name != "symmetrized_right_multiplication":
                    continue
                has_mor = any(isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "parameters" for t in n.targets)
                    and ast.unparse(n.value) == "modules.Mor(self.codomain(), self.domain())"
                    for n in method.body)
                for image in method.body:
                    if not isinstance(image, ast.FunctionDef) or image.name != "image":
                        continue
                    has_composition = any(isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "product" for t in n.targets)
                        and ast.unparse(n.value) == "parameters.module_generator(label) * self"
                        for n in image.body)
                    has_call = any(isinstance(n, ast.Call) and n.lineno == line
                        and isinstance(n.func, ast.Attribute) and n.func.attr == "transpose"
                        and isinstance(n.func.value, ast.Name) and n.func.value.id == "product"
                        for n in ast.walk(image))
                    if has_mor and has_composition and has_call:
                        owned_transpose = True
                        break
                if owned_transpose:
                    break
            if owned_transpose:
                continue

        # The three existing @ strides calls encode finite tuples as their
        # mixed-radix ordinal: this is indexing, not a bilinear contraction.
        if (path == "src/sage_extensions/categories/modules/framed/formed/discriminant_modules.py"
                and hit["metaVariables"]["single"].get("Y", {}).get("text") == "strides"):
            ordinal_index = False
            for method in ast.walk(tree):
                if not isinstance(method, ast.FunctionDef) or method.name != "_isotropic_subgroups":
                    continue
                has_strides = any(isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "strides" for t in n.targets)
                    and isinstance(n.value, ast.Call) and ast.unparse(n.value.func) == "numpy.array"
                    for n in method.body)
                if has_strides and method.lineno <= line <= method.end_lineno:
                    ordinal_index = True
                    break
            if ordinal_index:
                continue

        print("{}:{}: {}".format(path, line, hit["lines"].strip()))
    '); then
            echo "tensor-boundary could not classify $pattern" >&2
            exit 1
        fi
        n=$(printf '%s\n' "$findings" | grep -c . || true)
        total=$((total + n))
        printf '%4d  %s\n' "$n" "$pattern"
        if [ "$n" -gt 0 ]; then
            printf '%s\n' "$findings" | head -40
        fi
    done
    if [ "$total" -gt 0 ]; then
        echo "$total suspected coordinate operations outside sage_extensions/tensors/: state the owned pullback, contraction, composition, inverse or application instead."
        exit 1
    fi
    echo "No prohibited syntax detected; categorical ownership still requires source review."


# Run the test suite, or the named tests, under Sage's Python.
[positional-arguments]
test *args:
    PYTHONPATH="$HOME/ai-review-ci/tool-artifacts/pytest_plugins${PYTHONPATH:+:$PYTHONPATH}" \
        "$(just -f ~/ai-review-ci/justfiles/sage.just -d . _sage-python)" -m pytest -p qc_sage_session "$@"

# The suite runs in parallel, one Sage process per worker, and records which
# test ran each line; only lines a passing test ran count as covered.
# Every sage_extensions line and branch no passing test runs, file by file
coverage workers="6":
    #!/usr/bin/env bash
    set -euo pipefail
    qc=~/ai-review-ci/justfiles/sage.just
    # tests/ is the suite for src/; computation scripts elsewhere are not.
    mapfile -t tests < <(just -f "$qc" -d . _sage-test-files; just -f "$qc" -d . _sage-python-test-files)
    mapfile -t tests < <(printf '%s\n' "${tests[@]}" | grep '^tests/')
    out=.tmp/coverage
    mkdir -p "$out"
    for old in "$out"/*.jsonl; do if [ -e "$old" ]; then gio trash "$old"; fi; done
    touch "$out/measured-at"
    # Work stealing rebalances the few long tests across idle workers.
    status=0
    just _coverage-pytest "$out/.coverage" "$out/run.jsonl" -n {{workers}} --dist worksteal "${tests[@]}" || status=$?
    just coverage-report
    echo "pytest exit status: $status"

# Use it while writing tests against a gap the full run reported; it costs
# the named tests, not the suite.
# Add the named tests to the last full run; report the source files they reach
[positional-arguments]
coverage-add +tests:
    #!/usr/bin/env bash
    set -euo pipefail
    out=.tmp/coverage
    if [ ! -e "$out/.coverage" ]; then echo "no full run to add to: run just coverage first"; exit 1; fi
    sage_python="$(just -f ~/ai-review-ci/justfiles/sage.just -d . _sage-python)"
    run="$(date +%s%N)"
    status=0
    # Many tests share out across workers; a few run in one process, sparing the worker startups.
    parallel=(); if [ "$#" -gt 50 ]; then parallel=(-n 6 --dist worksteal); fi
    just _coverage-pytest "$out/.coverage.add-$run" "$out/add-$run.jsonl" "${parallel[@]}" "$@" || status=$?
    # Several sessions may add at once; the lock serializes the merge and the report.
    flock "$out/.lock" "$sage_python" -m coverage combine --keep --append \
        --data-file="$out/.coverage" "$out/.coverage.add-$run"
    flock "$out/.lock" "$sage_python" -m sage_extensions.testing.coverage_gaps \
        --touched-by "$out/.coverage.add-$run"
    gio trash "$out/.coverage.add-$run"
    echo "pytest exit status: $status"

# The stored data records which tests ran each source file, so after an edit
# only those tests, and the edited test files, run again.
# Remeasure what edits since the last measurement reach, then report
coverage-update:
    #!/usr/bin/env bash
    set -euo pipefail
    out=.tmp/coverage
    if [ ! -e "$out/.coverage" ]; then echo "nothing measured yet: run just coverage first"; exit 1; fi
    sage_python="$(just -f ~/ai-review-ci/justfiles/sage.just -d . _sage-python)"
    mapfile -t tests < <(flock "$out/.lock" "$sage_python" -m sage_extensions.testing.coverage_gaps --select-affected)
    # A purged file whose lines only the import runs is remeasured by collection alone.
    if [ "${#tests[@]}" -eq 0 ]; then
        just coverage-add --collect-only "$(git ls-files 'tests/**/test_*.sage' | head -n 1)" > /dev/null
        just coverage-report
        exit 0
    fi
    echo "rerunning ${#tests[@]} tests reached by the edits"
    just coverage-add "${tests[@]}"

# The coverage recorded so far, for all of sage_extensions or for the source paths matching globs such as '*/schemes/*'
[positional-arguments]
coverage-report *include:
    #!/usr/bin/env bash
    set -euo pipefail
    select=(); if [ "$#" -gt 0 ]; then select=(--include "$@"); fi
    "$(just -f ~/ai-review-ci/justfiles/sage.just -d . _sage-python)" -m sage_extensions.testing.coverage_gaps "${select[@]}"

# The specification subtrees are red until sage_extensions meets them, so a
# failing suite still yields its coverage; the caller reports the exit status.
# No per-test timeout: its SIGALRM inside Cython ends the whole run (TRAPS.md),
# and coverage tracing changes runtime materially. The measurement-only flag
# keeps timing output without applying baselines gathered without tracing.
# One-line tracebacks keep failure reports from computing owned reprs.
[positional-arguments]
_coverage-pytest data log *args:
    #!/usr/bin/env bash
    set -euo pipefail
    export PYTHONPATH="$HOME/ai-review-ci/tool-artifacts/pytest_plugins${PYTHONPATH:+:$PYTHONPATH}"
    export COVERAGE_FILE="$1"
    log="$2"
    shift 2
    "$(just -f ~/ai-review-ci/justfiles/sage.just -d . _sage-python)" -m pytest -p qc_sage_session \
        -q --no-time-gates --timeout=0 --tb=line --report-log="$log" \
        --cov=sage_extensions --cov-branch --cov-context=test --cov-report= \
        "$@"

# Check that the proof surface stays inside the mathematical universe.
# Policies: CONTRIBUTING.md DEV-37 (a test stays inside the universe) and
# DEV-38 (assert the object, not a chosen presentation).
#
# tests/engineering/ is the cordon for tests that prove no mathematics.
# ast-grep matches the syntax tree, so `== (0, 2)` is found wherever it is
# written -- across line breaks, and never inside a string or a docstring.
test-universe:
    #!/usr/bin/env bash
    set -uo pipefail
    files=$(git ls-files 'tests/*.py' 'tests/**/*.py' | grep -v '^tests/engineering/')
    if [ -z "$files" ]; then echo "No mathematical tests to check."; exit 0; fi
    total=0
    count() { ast-grep run --lang python --pattern "$1" --json $files 2>/dev/null \
        | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))'; }
    show()  { ast-grep run --lang python --pattern "$1" $files 2>/dev/null | head -"$2"; }
    check() {
        local policy="$1" why="$2"; shift 2
        local n=0 p
        for p in "$@"; do n=$((n + $(count "$p"))); done
        total=$((total + n))
        printf '%-7s %4d  %s\n' "$policy" "$n" "$why"
        [ "$n" -gt 0 ] && for p in "$@"; do show "$p" 4; done
        return 0
    }
    echo "Checking $(echo "$files" | wc -l) mathematical test files."
    echo
    check DEV-37 'extraction constructor: ask the object, not a Python container' \
        'tuple($$$A)' 'list($$$A)' 'set($$$A)' 'frozenset($$$A)' 'sorted($$$A)'
    check DEV-37 'len() where cardinality() is the mathematical operation' \
        'len($$$A)'
    check DEV-37 'compared against a Python tuple or list display' \
        '$X == ($A, $$$B)' '$X == [$$$B]' '$X != ($A, $$$B)' '$X != [$$$B]'
    check DEV-40 'extraction accessor: state the claim about the owned elements' \
        '$X.to_tuple()' '$X.to_list()' '$X.tolist()' '$X.list()'
    echo
    if [ "$total" -gt 0 ]; then
        echo "$total findings.  Extraction is strictly weaker than comparing the"
        echo "objects: it passes whether or not their own equality is implemented."
        exit 1
    fi
    echo "The proof surface stays inside the universe."

# Lint the test tree against the session standard (sage_extensions.testing.test_lint).
# With no paths it lints every test.
test-lint *paths:
    "$(just -f ~/ai-review-ci/justfiles/sage.just -d . _sage-python)" \
        -m sage_extensions.testing.test_lint {{paths}}
