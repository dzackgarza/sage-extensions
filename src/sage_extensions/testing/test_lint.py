r"""Lint the test tree against the session standard.

A test is an end-to-end mathematical workflow typed into a session: every
name comes from ``from sage_extensions.all import *``, objects are
built through the top-level category of their kind applied to their data, and
the assertions are mathematical facts (``TODO.md``,
``test-suite-mathematical-assertions``; research's ``tests/constructions/CONTRIBUTING.md``).
Guidelines are ignored or misread; this bounces the observable violations.

The checks read each file's syntax tree, and resolve the names it uses against
the live session namespace and the file's own bindings; they do not match
text. Rules, each with a code:

- ``TL01`` an explicit session import, or an import other than the session, ``pytest`` or ``__future__``;
- ``TL02`` a private attribute (``x._y``) or an underscored imported name;
- ``TL03`` introspection: ``getattr``, ``isinstance``, ``type``, ``vars``,
  ``__dict__``, ``__class__``, and the like;
- ``TL04`` ``try``/``except``: exceptions as control flow;
- ``TL05`` mocks and patches (``monkeypatch``, ``mocker``, ``unittest.mock``);
- ``TL06`` masking: ``skip``, ``skipif``, ``xfail``, ``importorskip``;
- ``TL07`` representation, not mathematics: ``repr``, ``str``, ``print``,
  ``latex``, f-strings or string literals compared in an assertion, and
  ``pytest.raises(match=...)``;
- ``TL08`` construction below the kind: a chosen-datum or implementation
  category (``Framed...``, ``...WithChosen...``, ``Owned...``) or a bypass
  constructor named anywhere, or a property refinement (free, finitely
  generated, enumerated, ordered, ...) or an axiom of a category called to
  construct an object;
- ``TL09`` a test with no assertion, or an assertion that holds of anything
  (a constant, ``is not None``);
- ``TL10`` ``len``: a length assumes finiteness; ask for a cardinality;
- ``TL11`` the banned spellings ``Hom``, ``gens``, ``generators``, ``dual``;
- ``TL12`` an engine reached directly (``libgap``, ``pari``, ``gap``, ``.sage()``);
- ``TL13`` a name that is neither bound in the file, a session name, nor an
  allowed builtin: the test reaches outside the session;
- ``TL14`` a test file with no test.

Run ``python -m sage_extensions.testing.test_lint [paths]``, or ``just
test-lint``. As a pytest plugin (loaded from ``pyproject.toml``) it lints the
collected files once collection is final and ends the run red on any finding;
``--no-test-lint`` lifts it for a one-off triage run.
"""

from __future__ import annotations

import ast
import builtins
import runpy
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest

SESSION_MODULE = "sage_extensions.all"
ALLOWED_IMPORTS = frozenset({SESSION_MODULE, "pytest", "__future__"})

INTROSPECTION_CALLS = frozenset({
    "getattr", "hasattr", "setattr", "delattr", "isinstance", "issubclass", "type",
    "vars", "dir", "id", "callable", "globals", "locals", "super", "eval", "exec",
    "compile", "__import__",
})
INTROSPECTION_ATTRIBUTES = frozenset({
    "__dict__", "__class__", "__mro__", "__name__", "__qualname__", "__module__",
    "__bases__", "__subclasses__", "__wrapped__", "__code__", "__globals__",
})
REPRESENTATION_CALLS = frozenset({"repr", "str", "print", "latex", "ascii", "format", "ascii_art", "unicode_art"})
MOCK_NAMES = frozenset({"monkeypatch", "mocker", "mock", "patch", "MagicMock", "Mock"})
MASKING_MARKERS = frozenset({"skip", "skipif", "xfail", "importorskip"})
ENGINE_NAMES = frozenset({"libgap", "pari", "gap", "macaulay2", "singular", "maxima", "gp", "sage"})
ENGINE_METHODS = frozenset({"sage", "_sage_", "_libgap_", "_gap_", "_pari_", "_magma_"})
BANNED_SPELLINGS = {
    "Hom": "Mor",
    "gens": "group_generators, module_generators or algebra_generators",
    "generators": "group_generators, module_generators or algebra_generators",
    "dual": "dual_module, dual_lattice or dual_group",
}
# As a bare name only these are spellings; a variable named ``dual`` can name the dual numbers.
BANNED_BARE_NAMES = frozenset({"Hom", "generators"})
BYPASS_CONSTRUCTORS = frozenset({
    "finite_ordered_set", "finite_ordinal_set", "indexed_family", "finite_family",
    "finite_indexed_family", "finite_indexed_family_from_values",
})
PROPERTY_REFINEMENTS = frozenset({
    "FreeModules", "FinitelyGeneratedModules", "FinitelyPresentedModules",
    "FinitelyPresentedTorsionModules", "TorsionModules", "ProjectiveModules",
    "VectorSpaces", "ModulesOverCommutativeRings", "GeneralModules", "FreeFormModules",
    "EnumeratedSets", "TotallyOrderedSets",
    "EnumeratedByNaturals", "EnumeratedByIntegers", "FunctionEnumeratedSets",
    "PredicateSubgroups", "PredicateSubrings", "OrderedRings", "FinitePowerSets",
})
DISPLAY_METHODS = frozenset({"_repr_", "_latex_", "__repr__", "__str__", "__format__", "_ascii_art_", "_unicode_art_"})
FLAGGED_ELSEWHERE = (
    INTROSPECTION_CALLS | REPRESENTATION_CALLS | MOCK_NAMES | BYPASS_CONSTRUCTORS
    | frozenset(BANNED_SPELLINGS) | frozenset({"len"})
)


def _allowed_builtins() -> frozenset[str]:
    r"""The builtins a test may name, read at lint time.

    A directory's ``conftest.py`` binds the session abbreviations its tests use
    as builtins, so the set is read after the conftests have run.
    """
    return frozenset(
        name for name in dir(builtins)
        if not name.startswith("_")
        and name not in INTROSPECTION_CALLS | REPRESENTATION_CALLS | {"len", "open", "input", "breakpoint", "exit", "quit"}
    )


def _is_choice_category(name: str) -> bool:
    r"""A category of objects carrying a chosen datum, or an implementation class."""
    return name.startswith(("Owned", "Framed")) or "WithChosen" in name


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.code} {self.message}"


def _axiom_names() -> frozenset[str]:
    from sage.categories.category_with_axiom import all_axioms

    return frozenset(all_axioms)


def _bound_names(tree: ast.Module) -> set[str]:
    r"""Every name the file binds anywhere: definitions, assignments, parameters, imports, loop targets."""
    bound: set[str] = set()
    for node in ast.walk(tree):
        match node:
            case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
                bound.add(node.name)
            case ast.Name(ctx=ast.Store() | ast.Del()):
                bound.add(node.id)
            case ast.arg():
                bound.add(node.arg)
            case ast.alias():
                bound.add((node.asname or node.name).split(".")[0])
            case ast.ExceptHandler(name=str() as name):
                bound.add(name)
            case ast.MatchAs(name=str() as name) | ast.MatchStar(name=str() as name):
                bound.add(name)
            case ast.Call(func=ast.Name(id="var"), args=[ast.Constant(value=str() as names), *_]):
                # Sage's ``var`` binds the names it lists in the session's
                # namespace; the dialect lowers ``f(t) = ...`` through it.
                bound.update(names.replace(",", " ").split())
    return bound


def _call_name(node: ast.expr) -> str | None:
    match node:
        case ast.Name(id=name):
            return name
        case ast.Attribute(attr=name):
            return name
    return None


def _root_name(node: ast.expr) -> str | None:
    while True:
        match node:
            case ast.Call(func=inner) | ast.Attribute(value=inner) | ast.Subscript(value=inner):
                node = inner
            case ast.Name(id=name):
                return name
            case _:
                return None


def _is_trivial_assertion(test: ast.expr) -> bool:
    match test:
        case ast.Constant():
            return True
        case ast.Compare(ops=[ast.IsNot()], comparators=[ast.Constant(value=None)]):
            return True
    return False


def _is_display(node: ast.expr) -> bool:
    r"""An f-string, or a call rendering an object as text.

    A string literal is not a display: strings are legitimate points of a set.
    """
    match node:
        case ast.JoinedStr():
            return True
        case ast.Call(func=ast.Name(id=name)) if name in REPRESENTATION_CALLS:
            return True
        case ast.Call(func=ast.Attribute(attr=name)) if name in DISPLAY_METHODS:
            return True
    return False


def _asserting_functions(tree: ast.Module) -> set[str]:
    r"""The module-level functions that assert, directly or through another such function."""
    functions = {
        node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    def asserts_directly(function: ast.AST) -> bool:
        return any(
            isinstance(sub, ast.Assert) or (isinstance(sub, ast.Call) and _call_name(sub.func) == "raises")
            for sub in ast.walk(function)
        )

    def calls(function: ast.AST) -> set[str]:
        return {
            sub.func.id for sub in ast.walk(function)
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id in functions
        }

    asserting = {name for name, function in functions.items() if asserts_directly(function)}
    added = asserting
    while added:
        added = {name for name, function in functions.items() if name not in asserting and calls(function) & asserting}
        asserting |= added
    return asserting


def lint_file(path: Path, session_names: frozenset[str], axioms: frozenset[str]) -> list[Finding]:
    source = _python_source(path)
    tree = ast.parse(source, filename=str(path))
    shown = str(path)
    findings: list[Finding] = []
    allowed_builtins = _allowed_builtins()

    def flag(node: ast.AST, code: str, message: str) -> None:
        findings.append(Finding(shown, getattr(node, "lineno", 1), code, message))

    tests = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]
    if not tests:
        flag(tree, "TL14", "a test file with no test")
    bound = _bound_names(tree)

    for node in ast.walk(tree):
        match node:
            case ast.Import(names=names):
                for alias in names:
                    if alias.name not in ALLOWED_IMPORTS:
                        flag(node, "TL01", f"import {alias.name}: take every name from the session")
            case ast.ImportFrom(module=module, names=names):
                if (
                    module == SESSION_MODULE
                    and not (len(names) == 1 and names[0].name == "*")
                ):
                    flag(node, "TL01", "import the complete session with from sage_extensions.all import *")
                elif module not in ALLOWED_IMPORTS:
                    flag(node, "TL01", f"from {module} import ...: take every name from the session")
                for alias in names:
                    if alias.name.startswith("_"):
                        flag(node, "TL02", f"imports the private name {alias.name}")
                    if module == "pytest" and alias.name in MOCK_NAMES | MASKING_MARKERS:
                        flag(node, "TL05", f"imports pytest.{alias.name}")
            case ast.Attribute(attr=attr):
                if attr in INTROSPECTION_ATTRIBUTES:
                    flag(node, "TL03", f"reads {attr}: introspection is not mathematics")
                elif attr in ENGINE_METHODS:
                    flag(node, "TL12", f".{attr}: reaches the engine object")
                elif attr.startswith("_") and not (attr.startswith("__") and attr.endswith("__")):
                    flag(node, "TL02", f"private attribute .{attr}")
                if attr in MASKING_MARKERS and _root_name(node) == "pytest":
                    flag(node, "TL06", f"pytest {attr}: masking")
                if attr in BANNED_SPELLINGS:
                    flag(node, "TL11", f".{attr}: write {BANNED_SPELLINGS[attr]}")
            case ast.Try() | ast.TryStar():
                flag(node, "TL04", "try/except: expected failures are asserted with pytest.raises")
            case ast.Assert(test=test):
                if _is_trivial_assertion(test):
                    flag(node, "TL09", "an assertion that holds of anything")
                if isinstance(test, ast.Compare) and any(_is_display(side) for side in (test.left, *test.comparators)):
                    flag(node, "TL07", "compares a rendering: assert the mathematical object, not its display")
            case ast.Call(func=func, keywords=keywords):
                name = _call_name(func)
                if isinstance(func, ast.Name) and name in INTROSPECTION_CALLS:
                    flag(node, "TL03", f"{name}(): introspection is not mathematics")
                if isinstance(func, ast.Name) and name in REPRESENTATION_CALLS:
                    flag(node, "TL07", f"{name}(): a representation, not a mathematical value")
                if isinstance(func, ast.Name) and name == "len":
                    flag(node, "TL10", "len(): ask for a cardinality")
                if name == "raises" and any(keyword.arg == "match" for keyword in keywords):
                    flag(node, "TL07", "pytest.raises(match=...): matches an error message")
                if isinstance(func, ast.Call):
                    constructor = _call_name(func.func)
                    if constructor in PROPERTY_REFINEMENTS:
                        flag(node, "TL08", f"constructs through {constructor}: construct through the top-level category of the kind")
                    if isinstance(func.func, ast.Attribute) and func.func.attr in axioms:
                        flag(node, "TL08", f"constructs through the axiom {func.func.attr}(): construct through the top-level category of the kind")
            case ast.Name(id=name, ctx=ast.Load()):
                if name in MOCK_NAMES:
                    flag(node, "TL05", f"{name}: mocks prove nothing about the real objects")
                if name in ENGINE_NAMES and name not in bound:
                    flag(node, "TL12", f"{name}: reaches an engine directly")
                if name in BANNED_BARE_NAMES:
                    flag(node, "TL11", f"{name}: write {BANNED_SPELLINGS[name]}")
                if name in BYPASS_CONSTRUCTORS or (_is_choice_category(name) and name in session_names):
                    flag(node, "TL08", f"{name}: a chosen-datum or implementation construction; construct through the top-level category of the kind")
                if name not in bound | session_names | allowed_builtins | ENGINE_NAMES | FLAGGED_ELSEWHERE:
                    flag(node, "TL13", f"{name} is not a session name")

    asserting = _asserting_functions(tree)
    for test in tests:
        for argument in test.args.args:
            if argument.arg in MOCK_NAMES:
                flag(test, "TL05", f"{test.name} takes the {argument.arg} fixture")
        if test.name not in asserting:
            flag(test, "TL09", f"{test.name} asserts nothing")
    return sorted(set(findings))


def _session_names() -> frozenset[str]:
    r"""The names a test resolves: Sage's script namespace, then the session star import.

    The global QC's collector (``qc_sage_session`` in ``ai-review-ci``) runs a
    ``.sage`` test with ``sage.all_cmdline`` in scope; the file's first line
    imports the session.
    """
    import sage.all_cmdline

    session = __import__(SESSION_MODULE, fromlist=["*"])
    return frozenset(
        name for namespace in (vars(sage.all_cmdline), vars(session)) for name in namespace if not name.startswith("_")
    )


def _python_source(path: Path) -> str:
    r"""The file as Python: a ``.sage`` test lowered as the QC collector lowers it.

    That is ``sage.repl.preparse.preparse_file`` after the session is imported,
    which installs the research dialect in its place.
    """
    source = path.read_text()
    if path.suffix != ".sage":
        return source
    __import__(SESSION_MODULE)
    from sage.repl import preparse

    return preparse.preparse_file(source)



def lint(paths: list[Path]) -> list[Finding]:
    session_names = _session_names()
    axioms = _axiom_names()
    return [finding for path in paths for finding in lint_file(path, session_names, axioms)]


def _run_conftests(files: list[Path]) -> None:
    r"""Run each ``conftest.py`` above the linted files, as pytest would before collecting them.

    The ``pythonpath`` of ``[tool.pytest.ini_options]`` goes on ``sys.path`` first,
    because the conftests import from it.
    """
    options = tomllib.loads(Path("pyproject.toml").read_text())["tool"]["pytest"]["ini_options"]
    sys.path[:0] = [str(Path(entry).resolve()) for entry in options.get("pythonpath", [])]
    conftests = sorted({
        directory / "conftest.py"
        for file in files
        for directory in file.resolve().parents
        if (directory / "conftest.py").is_file()
    })
    for conftest in conftests:
        runpy.run_path(str(conftest))


def main(arguments: list[str]) -> int:
    named = [Path(argument) for argument in arguments]
    if named:
        files = [file for path in named for file in (sorted([*path.rglob("test_*.py"), *path.rglob("test_*.sage")]) if path.is_dir() else [path])]
    else:
        files = [file for file in sorted([*Path("tests").rglob("test_*.py"), *Path("tests").rglob("test_*.sage")])]
    _run_conftests(files)
    findings = lint(files)
    for finding in findings:
        print(finding)
    codes = sorted({finding.code for finding in findings})
    print(f"{len(files)} files, {len(findings)} findings" + (f" ({', '.join(codes)})" if codes else ""))
    return 1 if findings else 0


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--no-test-lint",
        action="store_true",
        help="one-off triage run: do not end the run on test-lint findings",
    )


@pytest.hookimpl(trylast=True)
def pytest_collection_finish(session: pytest.Session) -> None:
    if session.config.getoption("no_test_lint"):
        return
    files = sorted({
        Path(item.path).relative_to(session.config.rootpath)
        for item in session.items
        if Path(item.path).suffix in {".py", ".sage"}
    })
    findings = lint([file for file in files])
    if findings:
        shown = "\n".join(str(finding) for finding in findings[:50])
        more = f"\n... and {len(findings) - 50} more" if len(findings) > 50 else ""
        pytest.exit(
            f"test lint: {len(findings)} findings (run just test-lint for all)\n{shown}{more}",
            returncode=pytest.ExitCode.TESTS_FAILED,
        )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
