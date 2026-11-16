"""The declared category graph, read from source without importing it.

This is the tool ``just category-graph`` runs, taken from where it was already
maintained: ``src/dzack_research/utilities/category_graph.py`` of
``dzackgarza/research`` at commit ``d62f344542``, whose ``_default_root``
already read ``sage_extensions``.  It is ported, not rewritten -- the views,
their names and their algorithms are that module's -- and
``docs/architecture-inspection.md`` describes them here.

The live survey answers what a session *does*.  This module answers what the
source *says*: which categories exist, and what each one declares as its
supercategories.  It parses the tree with :mod:`ast`, so it reports on a
preamble that does not currently import, which is exactly when the
declarations most need reading.

A ``super_categories()`` return value is a mathematical claim -- that every
object of this category is an object of those -- and this is the surface that
makes each claim legible beside every other one.
"""

from __future__ import annotations

import importlib.util
import argparse
import ast
import json
import re
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from functools import cache
from graphlib import TopologicalSorter
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable

    from sage.graphs.digraph import DiGraph
    from sage.graphs.graph import Graph

CATEGORY_BASES: frozenset[str] = frozenset(
    {
        "Category",
        "CategoryWithAxiom",
        "CategoricalHomset",
        "HomCategoryConstruction",
        "OwnedCategory",
        "OwnedCategoryBase",
        "OwnedCategoryOverBaseRing",
        "OwnedParameterizedCategory",
    }
)

DECLARATIONS = ("super_categories", "extra_super_categories")


def _vertex(base: str, axioms: tuple[str, ...]) -> str:
    """The graph vertex of a category with axioms: ``Base.Axiom1.Axiom2``, sorted.

    Sage's ``Base().A().B()`` is the join of ``Base.A`` and ``Base.B``, one
    category whichever order the axioms are applied in.
    """
    return ".".join((base, *sorted(axioms)))


@dataclass(frozen=True)
class Supercategory:
    """One declared supercategory, and where its name comes from."""

    expression: str
    head: str
    resolved: str  # the head with any import alias followed back to its name
    origin: str  # "owned", "sage", or "expression"
    axioms: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()  # category-valued arguments, as vertices

    @property
    def vertex(self) -> str:
        head = self.resolved
        if self.parameters:
            head = f"{head}({', '.join(self.parameters)})"
        return _vertex(head, self.axioms)


@dataclass(frozen=True)
class CategoryDeclaration:
    """One category class and the supercategories its source declares."""

    name: str
    qualified_name: str
    path: str
    line: int
    bases: tuple[str, ...]
    summary: str
    declares: bool
    abstract: bool
    supercategories: tuple[Supercategory, ...] = field(default_factory=tuple)
    axiom_of: str = ""  # for a nested axiom class, the category it refines
    nested_in: str = ""  # for a nested construction such as ``_MorCategory``, the vertex enclosing it
    parameter: str = ""  # source symbol distinguishing the optional-parameter branch
    object_methods: tuple[
        str, ...
    ] = ()  # the methods its ``ParentMethods`` installs on objects

    @property
    def vertex(self) -> str:
        if self.nested_in:
            return f"{self.nested_in}::{self.name}"
        if self.parameter:
            return self.qualified_name
        if not self.axiom_of:
            return self.name
        return _vertex(self.axiom_of, tuple(self.qualified_name.split(".")[1:]))

    @property
    def heads(self) -> tuple[str, ...]:
        """The category names alone, with each declaration's arguments dropped."""
        return tuple(declared.head for declared in self.supercategories)

    @property
    def sage_supercategories(self) -> tuple[Supercategory, ...]:
        """The declared supercategories whose names are Sage's, not this tree's."""
        return tuple(d for d in self.supercategories if d.origin == "sage")


def _head(expression: str) -> str:
    """Return the name a supercategory expression applies or refers to."""
    stripped = _without_axioms(expression).split("(", 1)[0]
    return stripped.rsplit(".", 1)[-1].strip()


def _axiom_calls(expression: str) -> tuple[ast.expr, tuple[str, ...]]:
    """Split ``Base(R).A().B()`` into the base expression and its axiom names.

    An axiom is applied as a capitalised zero-argument method (Sage's
    ``with_axiom`` accessors); anything else ends the chain.
    """
    try:
        node: ast.expr = ast.parse(expression, mode="eval").body
    except SyntaxError:
        return ast.Name(id=expression), ()
    axioms: list[str] = []
    while (
        isinstance(node, ast.Call)
        and not node.args
        and not node.keywords
        and isinstance(node.func, ast.Attribute)
        and node.func.attr[:1].isupper()
    ):
        axioms.append(node.func.attr)
        node = node.func.value
    return node, tuple(reversed(axioms))


def _without_axioms(expression: str) -> str:
    base, _ = _axiom_calls(expression)
    return ast.unparse(base)


def _axioms(expression: str) -> tuple[str, ...]:
    _, axioms = _axiom_calls(expression)
    return axioms


def _category_parameters(
    expression: str, imported: dict[str, tuple[str, str]], known: set[str]
) -> tuple[str, ...]:
    """The arguments of a declaration that are themselves categories, as vertices.

    ``GObjects(G, Sets())`` and ``DirectSumObjects(Lattices(R))`` are
    constructions on a category (`CAT-20`): one category per parameter, each
    declaring that parameter.  The parameter is the vertex of the argument,
    with its axioms, so ``DirectSumObjects(Modules(R).FinitelyGenerated())``
    is a vertex of its own.
    """
    base, _ = _axiom_calls(expression)
    if not isinstance(base, ast.Call):
        return ()
    parameters: list[str] = []
    for argument in base.args:
        text = ast.unparse(argument)
        head = _resolved(_head(text), imported)
        if head in known:
            parameters.append(_vertex(head, _axioms(text)))
    return tuple(parameters)


def _summary(node: ast.ClassDef) -> str:
    text = ast.get_docstring(node) or ""
    return text.strip().split("\n", 1)[0]


def _is_abstract(node: ast.FunctionDef) -> bool:
    for decorator in node.decorator_list:
        if _head(ast.unparse(decorator)) == "abstract_method":
            return True
    return False


def _returned_supercategories(node: ast.FunctionDef) -> tuple[str, ...]:
    """Collect every expression this declaration returns as a supercategory."""
    found: list[str] = []
    for statement in ast.walk(node):
        if not isinstance(statement, ast.Return) or statement.value is None:
            continue
        found.extend(_return_expressions(statement.value))
    return tuple(found)


def _return_expressions(value: ast.expr) -> tuple[str, ...]:
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        return tuple(ast.unparse(item) for item in value.elts)
    return (ast.unparse(value),)


def _optional_parameter_supercategories(
    node: ast.ClassDef, declaration: ast.FunctionDef
) -> tuple[str, tuple[str, ...], tuple[str, ...]] | None:
    """Separate supercategory declarations for absent and supplied parameters.

    The source must explicitly branch on an optional constructor parameter
    read from its accessor.  Other conditional returns retain the ordinary
    source graph's union semantics.
    """
    constructors = [
        method
        for method in node.body
        if isinstance(method, ast.FunctionDef) and method.name == "__init__"
    ]
    body = [
        statement for statement in declaration.body
        if not (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
        )
    ]
    if len(constructors) != 1 or len(body) != 3:
        return None
    assignment, branch, parameterized_return = body
    match assignment, branch, parameterized_return:
        case (
            ast.Assign(
                targets=[ast.Name(id=parameter)],
                value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="self"), attr=accessor),
                    args=[],
                    keywords=[],
                ),
            ),
            ast.If(
                test=ast.Compare(
                    left=ast.Name(id=condition),
                    ops=[ast.Is()],
                    comparators=[ast.Constant(value=None)],
                ),
                body=[ast.Return(value=unparameterized)],
                orelse=[],
            ),
            ast.Return(value=parameterized),
        ) if parameter == accessor == condition:
            constructor = constructors[0]
            defaults = dict(
                zip(
                    (
                        arg.arg
                        for arg in constructor.args.args[
                            len(constructor.args.args) - len(constructor.args.defaults) :
                        ]
                    ),
                    constructor.args.defaults,
                    strict=True,
                )
            )
            default = defaults.get(parameter)
            if not isinstance(default, ast.Constant) or default.value is not None:
                return None
            return parameter, _return_expressions(unparameterized), _return_expressions(parameterized)
    return None


def _imported_names(tree: ast.Module) -> dict[str, tuple[str, str]]:
    """Map each imported name to the module and the name it was imported as.

    A name bound by ``import X as Y`` is the same category as ``X``; resolving
    ``Y`` back to ``X`` is what keeps an alias from reading as a category that
    nothing defines.
    """
    origins: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                origins[alias.asname or alias.name] = (node.module, alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                origins[bound] = (alias.name, alias.name.split(".")[-1])
    return origins


def _module_level_names(tree: ast.Module) -> set[str]:
    """Names a module binds besides its classes: factories and rebindings.

    ``def FiniteSets()`` returning a category, and ``OwnedAbelianGroups =
    AbelianGroups``, both define a category name as surely as a ``class``
    statement does.
    """
    bound: set[str] = set()
    for statement in tree.body:
        if isinstance(statement, ast.FunctionDef):
            bound.add(statement.name)
        elif isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    bound.add(target.id)
    return bound


def _declarations(node: ast.ClassDef) -> list[ast.FunctionDef]:
    """The methods declaring supercategories: ``super_categories`` and, on an
    axiom class, ``extra_super_categories`` (Sage adds the rest itself)."""
    return [
        statement
        for statement in node.body
        if isinstance(statement, ast.FunctionDef) and statement.name in DECLARATIONS
    ]


def _container_methods(node: ast.ClassDef, container: str) -> dict[str, ast.FunctionDef]:
    """The methods a category installs through one of its ``*Methods`` classes."""
    for statement in node.body:
        if isinstance(statement, ast.ClassDef) and statement.name == container:
            return {
                method.name: method
                for method in statement.body
                if isinstance(method, ast.FunctionDef)
            }
    return {}


def _object_methods(node: ast.ClassDef) -> dict[str, ast.FunctionDef]:
    """The methods a category installs on its objects: its ``ParentMethods`` body."""
    return _container_methods(node, "ParentMethods")


def _factories(trees: list[ast.Module]) -> dict[str, str]:
    """Module-level functions whose whole body returns one category expression.

    ``def FiniteSets(): return Sets().Finite()`` names the category
    ``Sets.Finite``; a declaration of ``FiniteSets()`` declares that vertex.
    A name defined twice is left unresolved.
    """
    found: dict[str, list[str]] = {}
    for tree in trees:
        for statement in tree.body:
            if not isinstance(statement, ast.FunctionDef) or statement.args.args:
                continue
            body = [
                s
                for s in statement.body
                if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
            ]
            match body:
                case [ast.Return(value=ast.Call() as value)]:
                    found.setdefault(statement.name, []).append(ast.unparse(value))
    return {
        name: expressions[0]
        for name, expressions in found.items()
        if len(expressions) == 1
    }


def _unfold(
    expression: str, factories: dict[str, str], imported: dict[str, tuple[str, str]]
) -> str:
    """The expression with a factory call replaced by the category it returns."""
    base, axioms = _axiom_calls(expression)
    match base:
        case ast.Call(func=ast.Name(id=name), args=[], keywords=[]) if (
            _resolved(name, imported) in factories
        ):
            return factories[_resolved(name, imported)] + "".join(
                f".{axiom}()" for axiom in axioms
            )
    return expression


def _protected(names: tuple[str, ...]) -> bool:
    return any(name.startswith("_") for name in names)


def _is_category(node: ast.ClassDef, known: set[str]) -> bool:
    for base in node.bases:
        if _head(ast.unparse(base)) in CATEGORY_BASES | known:
            return True
    return False


def _resolved(head: str, imported: dict[str, tuple[str, str]]) -> str:
    """Follow ``import X as Y`` back, so an alias names the category it aliases."""
    binding = imported.get(head)
    return binding[1] if binding is not None else head


def _origin(head: str, imported: dict[str, tuple[str, str]], known: set[str]) -> str:
    """Say where a declared supercategory's name comes from."""
    binding = imported.get(head)
    if binding is not None and binding[0].split(".")[0] == "sage":
        return "sage"
    if head in known or (binding is not None and binding[1] in known):
        return "owned"
    if binding is not None:
        return "owned"
    return "expression"


def read_tree(root: Path) -> list[CategoryDeclaration]:
    """Read every category declared under ``root``, in source order per file."""
    sources = sorted(root.rglob("*.py"))
    assert root.is_dir() and sources, f"No Python source tree at {root}"
    parsed: list[tuple[Path, ast.Module]] = []
    for path in sources:
        parsed.append(
            (path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
        )

    known: set[str] = set()
    # Close the declared Python inheritance chain independently of file order.
    previous: set[str] | None = None
    while previous != known:
        previous = known.copy()
        for _, tree in parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and _is_category(node, known):
                    known.add(node.name)
    category_classes = set(known)
    # A category name is also bound by a factory function or a rebinding, so
    # those count as defined when a declaration names them.
    for _, tree in parsed:
        known |= _module_level_names(tree)
    factories = _factories([tree for _, tree in parsed])

    declarations: list[CategoryDeclaration] = []
    for path, tree in parsed:
        imported = _imported_names(tree)
        for scope, node in _classes(tree):
            if not _is_category(node, known):
                continue
            declaring = _declarations(node)
            split = (
                _optional_parameter_supercategories(node, declaring[0])
                if len(declaring) == 1 and declaring[0].name == "super_categories"
                else None
            )
            variants = (
                [("", split[1]), (split[0], split[2])]
                if split is not None
                else [
                    (
                        "",
                        tuple(
                            expression
                            for declaration in declaring
                            for expression in _returned_supercategories(declaration)
                        ),
                    )
                ]
            )
            for parameter, expressions in variants:
                declarations.append(
                    CategoryDeclaration(
                        name=node.name,
                        qualified_name=".".join((*scope, node.name))
                        + (f"({parameter})" if parameter else ""),
                        path=str(path),
                        line=node.lineno,
                        bases=tuple(_head(ast.unparse(base)) for base in node.bases),
                        summary=_summary(node),
                        declares=bool(declaring),
                        abstract=any(_is_abstract(d) for d in declaring),
                        supercategories=tuple(
                            Supercategory(
                                expression=expression,
                                head=_head(unfolded),
                                resolved=_resolved(_head(unfolded), imported),
                                origin=_origin(_head(unfolded), imported, known),
                                axioms=_axioms(unfolded),
                                parameters=_category_parameters(
                                    unfolded, imported, category_classes
                                ),
                            )
                            for expression in expressions
                            for unfolded in (_unfold(expression, factories, imported),)
                        ),
                        # A class nested in a category is that category with the
                        # axioms the nesting names; a protected nested class is a
                        # construction on it, such as its Mor category, and refines
                        # nothing.
                        axiom_of=scope[0]
                        if scope
                        and scope[0] in known
                        and not _protected((*scope[1:], node.name))
                        else "",
                        nested_in=_vertex(scope[0], scope[1:])
                        if scope
                        and scope[0] in known
                        and _protected((*scope[1:], node.name))
                        else "",
                        parameter=parameter,
                        object_methods=tuple(_object_methods(node)),
                    )
                )
    return declarations


def _classes(
    tree: ast.Module,
) -> list[tuple[tuple[str, ...], ast.ClassDef]]:
    """Every class in the module, each with the class names enclosing it."""
    found: list[tuple[tuple[str, ...], ast.ClassDef]] = []

    def walk(body: list[ast.stmt], scope: tuple[str, ...]) -> None:
        for statement in body:
            if isinstance(statement, ast.ClassDef):
                found.append((scope, statement))
                walk(statement.body, (*scope, statement.name))

    walk(tree.body, ())
    return found


def render_table(declarations: list[CategoryDeclaration]) -> str:
    lines = [
        f"{len(declarations)} categories declared under the parsed tree.",
        "",
        "Each row is what the source says: the category, and the supercategories",
        "its `super_categories()` returns.  A row with no declaration inherits",
        "one; a row marked `abstract` requires its subcategories to supply one.",
        "",
    ]
    width = max((len(d.qualified_name) for d in declarations), default=0)
    for declaration in sorted(declarations, key=lambda d: d.qualified_name):
        if declaration.abstract:
            stated = "<abstract>"
        elif not declaration.declares:
            stated = "<inherited>"
        elif not declaration.supercategories:
            stated = "<none returned>"
        else:
            stated = ", ".join(d.expression for d in declaration.supercategories)
        lines.append(f"{declaration.qualified_name:<{width}}  {stated}")
    return "\n".join(lines) + "\n"


def render_by_supercategory(declarations: list[CategoryDeclaration]) -> str:
    """Group the tree the other way round: each supercategory, and who claims it."""
    claimants: dict[str, list[str]] = {}
    for declaration in declarations:
        for head in declaration.heads:
            claimants.setdefault(head, []).append(declaration.qualified_name)
    lines = [
        "Every declared supercategory, and the categories declaring it.",
        "",
        "Read a large group as one mathematical claim made many times: each",
        "member asserts that its objects are objects of the heading.",
        "",
    ]
    for head in sorted(claimants, key=lambda h: (-len(claimants[h]), h)):
        members = sorted(claimants[head])
        lines.append(f"{head}  ({len(members)})")
        for member in members:
            lines.append(f"    {member}")
        lines.append("")
    return "\n".join(lines)


def render_foreign(declarations: list[CategoryDeclaration]) -> str:
    """Owned categories that declare a Sage category as a supercategory.

    The preamble owns its categories outright, so each row places an owned
    category's objects inside a category this tree does not define, and the
    claim can only be read in Sage's source.
    """
    rows = [d for d in declarations if d.sage_supercategories]
    lines = [
        f"{len(rows)} owned categories declare a supercategory whose name is Sage's.",
        "",
    ]
    for declaration in sorted(rows, key=lambda d: d.qualified_name):
        foreign = ", ".join(s.expression for s in declaration.sage_supercategories)
        lines.append(f"{declaration.qualified_name}")
        lines.append(f"    declares  {foreign}")
        lines.append(f"    at        {declaration.path}:{declaration.line}")
        lines.append("")
    return "\n".join(lines)


def _defined_names(declarations: list[CategoryDeclaration]) -> set[str]:
    """Every category name the parsed tree binds, aliases and factories included."""
    roots = {Path(d.path).parent for d in declarations}
    bound: set[str] = set()
    for root in roots:
        for path in root.glob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, OSError):
                continue
            bound |= _module_level_names(tree)
    return bound


def render_audit(declarations: list[CategoryDeclaration]) -> str:
    """The mechanically checkable defects in the declared graph.

    None of these needs a reading of what the objects are.  A name declared as
    a supercategory that nothing defines is a missing category; a declaration
    computed from a local variable is an edge this graph cannot state; a cycle
    is a contradiction outright.  What a declaration *means* is read by a
    mathematician against the category's own definition, not decided here.
    """
    declared = (
        {d.name for d in declarations}
        | {d.qualified_name for d in declarations}
        | _defined_names(declarations)
    )

    missing: dict[str, list[str]] = {}
    unstated: dict[str, list[str]] = {}
    for declaration in declarations:
        for supercategory in declaration.supercategories:
            if supercategory.origin == "expression":
                if supercategory.resolved not in declared:
                    unstated.setdefault(supercategory.expression, []).append(
                        declaration.qualified_name
                    )
            elif (
                supercategory.origin == "owned"
                and supercategory.resolved not in declared
            ):
                missing.setdefault(supercategory.resolved, []).append(
                    declaration.qualified_name
                )

    # A category declaring its own name over other data (`Modules(R)` declaring
    # `Modules(S)`) is a restriction-of-scalars edge, ruled out on 2026-09-16
    # because Sage applies every axiom along it; reported apart from cycles
    # because it is a loop on the name, not on the objects.
    recursive = sorted(
        {d.name for d in declarations if not d.parameter and d.name in d.heads}
    )
    # A strongly connected component with more than one category is a set of
    # categories each declared to lie under the others.
    declared_edges = _declared_edges(declarations)
    cycles = [
        ", ".join(sorted(_name(vertex) for vertex in component))
        for component in _digraph(
            _vertices(declarations, declared_edges), declared_edges
        ).strongly_connected_components()
        if len(component) > 1
    ]

    lines = [
        "Mechanically checkable defects in the declared category graph.",
        "",
        f"## Named as a supercategory, defined nowhere ({len(missing)})",
        "",
    ]
    for head in sorted(missing, key=lambda h: (-len(missing[h]), h)):
        lines.append(f"{head}  <- {', '.join(sorted(missing[head]))}")
    lines += [
        "",
        f"## Declared from a local expression, so the edge is not stated ({len(unstated)})",
        "",
    ]
    for expression in sorted(unstated):
        lines.append(f"{expression}  <- {', '.join(sorted(unstated[expression]))}")
    lines += [
        "",
        f"## Declared on its own name, with other data ({len(recursive)})",
        "",
        "A restriction-of-scalars edge, which Sage applies every axiom along;",
        "restriction is a functor, never a declaration (AGENTS.md, Red flags).",
        "",
    ]
    lines.extend(recursive or ["none"])
    lines += ["", f"## Cycles among distinct categories ({len(cycles)})", ""]
    lines.extend(cycles or ["none"])
    return "\n".join(lines) + "\n"


def _declared_edges(
    declarations: list[CategoryDeclaration],
) -> set[tuple[str, str]]:
    """Edges between categories this tree defines, class self-declarations dropped.

    An axiom category ``Base.A.B`` is the join of ``Base.A`` and ``Base.B``
    (Sage's axiom semantics), so every axiom vertex, declared or merely named,
    also declares each vertex with one axiom fewer.
    """
    names = {d.name for d in declarations}
    # A construction whose own declaration is its parameter (``return
    # [self.base_category()]``) declares nothing the reader can name at the
    # class; each instance ``H(P)`` declares ``P``.
    parameterized = {
        d.name
        for d in declarations
        if d.supercategories
        and all(s.origin == "expression" for s in d.supercategories)
    }
    edges = {
        (d.vertex, supercategory.vertex)
        for d in declarations
        for supercategory in d.supercategories
        if supercategory.resolved in names and supercategory.vertex != d.vertex
    }
    edges |= {
        (supercategory.vertex, parameter)
        for d in declarations
        for supercategory in d.supercategories
        if supercategory.resolved in parameterized
        for parameter in supercategory.parameters
    }
    return edges


def _axiom_edges(
    declarations: list[CategoryDeclaration], declared: set[tuple[str, str]]
) -> set[tuple[str, str]]:
    """The edges Sage's join supplies, computed rather than written.

    Each axiom vertex declares every vertex with one axiom fewer, down to the
    base; and for a written ``X.S -> Y.T``, ``X.S+U`` declares ``Y.T+V`` where
    ``V`` is the part of ``U`` that ``Y`` or a category above it defines
    (``CategoryWithAxiom.super_categories`` applies the axiom to every
    supercategory of the base, and ``_with_axiom_as_tuple`` walks upward to
    the nearest category defining it).  A written edge on a join class,
    ``Schemes.QuasiAffine.FiniteType -> Schemes.QuasiProjective``, therefore
    reaches every join that includes those axioms.
    """
    nested: dict[str, set[str]] = {}
    for d in declarations:
        if d.axiom_of:
            nested.setdefault(d.axiom_of, set()).update(d.qualified_name.split(".")[1:])
    above: dict[str, set[str]] = {}
    written: dict[str, set[tuple[frozenset[str], str, frozenset[str]]]] = {}
    for below, over in declared:
        below_base, *below_axioms = below.split(".")
        over_base, *over_axioms = over.split(".")
        written.setdefault(below_base, set()).add(
            (frozenset(below_axioms), over_base, frozenset(over_axioms))
        )
        if not below_axioms and not over_axioms:
            above.setdefault(below, set()).add(over)

    # Axioms a base can apply: its own nested ones and those of every category
    # above it, closed by iteration until nothing changes.
    defined: dict[str, set[str]] = {b: set(a) for b, a in nested.items()}
    changed = True
    while changed:
        changed = False
        for base, overs in above.items():
            gathered = set(defined.get(base, set()))
            for over in overs:
                gathered |= defined.get(over, set())
            if gathered != defined.get(base, set()):
                defined[base] = gathered
                changed = True

    pending = {v for edge in declared for v in edge if "." in v} | {
        d.vertex for d in declarations if d.axiom_of
    }
    edges: set[tuple[str, str]] = set()
    while pending:
        vertex = pending.pop()
        base, *axioms = vertex.split(".")
        targets = [
            _vertex(base, tuple(a for a in axioms if a != dropped))
            for dropped in axioms
        ]
        for stated, over, written_over_axioms in written.get(base, ()):
            if not stated <= set(axioms):
                continue
            carried = {
                a for a in axioms if a not in stated and a in defined.get(over, ())
            }
            target_axioms = tuple(written_over_axioms | carried)
            if target_axioms and (stated or carried):
                targets.append(_vertex(over, target_axioms))
        for target in targets:
            if (vertex, target) not in edges:
                edges.add((vertex, target))
                if "." in target:
                    pending.add(target)
    return edges


def _all_edges(declarations: list[CategoryDeclaration]) -> set[tuple[str, str]]:
    declared = _declared_edges(declarations)
    return declared | _axiom_edges(declarations, declared)


def _base_of(vertex: str) -> str:
    return vertex.split(".", 1)[0]


def _vertices(
    declarations: list[CategoryDeclaration], edges: set[tuple[str, str]]
) -> set[str]:
    """The 0-cells of the graph: each declared category, and each name an edge reaches.

    ``AGENTS.md`` makes the declared graph a 0-cell per category and a 1-cell
    per declaration, so a cell does not depend on an edge.  Two kinds have none:
    a declaration whose only supercategory is an expression the reader cannot
    place (``Sliced(base)`` declares ``base``), and an axiom vertex a
    declaration only names (``Aliased`` declares ``FinitePaths.Connected``).
    Neither is an edge, and both are cells.
    """
    return {d.vertex for d in declarations} | {v for a, b in edges for v in (a, b)}


def _graph(vertices: set[str], edges: set[tuple[str, str]]) -> Graph:
    from sage.graphs.graph import Graph

    return Graph([sorted(vertices), sorted(edges)], format="vertices_and_edges")


def _name(vertex: Hashable) -> str:
    """A vertex of a graph built here, which is a category name.

    Sage types a vertex as any hashable object; ``_graph`` and ``_digraph``
    build every graph on the names ``_vertices`` and ``_all_edges`` give.
    """
    assert isinstance(vertex, str)
    return vertex


def _digraph(vertices: set[str], edges: set[tuple[str, str]]) -> DiGraph:
    from sage.graphs.digraph import DiGraph

    return DiGraph([sorted(vertices), sorted(edges)], format="vertices_and_edges")


def _shortcuts(declarations: list[CategoryDeclaration]) -> list[tuple[str, str]]:
    """Written declarations a longer path already gives.

    The reduction runs over the written and the computed edges together, so a
    computed edge parallel to a written path is never reported: Sage's join
    drops it itself.
    """
    declared = _declared_edges(declarations)
    edges = _all_edges(declarations)
    reduction = set(
        _digraph(_vertices(declarations, edges), edges)
        .transitive_reduction()
        .edges(labels=False)
    )
    return sorted(edge for edge in declared if edge not in reduction)


def _chains_above(directed: DiGraph) -> dict[str, int]:
    """The longest chain of declarations above each category.

    ``level_sets()`` of the reversed graph puts a category in level ``k`` when
    its longest path to a maximal category has ``k`` declarations (Sage's
    ``DiGraph.level_sets``, linear time).  ``longest_path()`` is a MILP by
    default; see sage-extensions ``TRAPS.md``.
    """
    return {
        _name(vertex): level
        for level, vertices in enumerate(directed.reverse().level_sets())
        for vertex in vertices
    }


def _in_cyclic_order(graph: Graph, cycle: list[str]) -> list[str]:
    """Order a cycle's vertices around it.

    Sage's ``minimum_cycle_basis`` returns each cycle as a vertex set, not in
    cyclic order (``sage.graphs.base.boost_graph.min_cycle_basis``).
    """
    induced = graph.subgraph(cycle).cycle_basis()
    return (
        [_name(vertex) for vertex in induced[0]] if len(induced) == 1 else sorted(cycle)
    )


def _minimum_cycle_basis(graph: Graph) -> list[list[str]]:
    """Sage's default minimum cycle basis takes integer vertices only; relabel.

    Wall time on the declared graph is in sage-extensions ``TRAPS.md``.
    """
    relabelled = graph.copy()
    names = relabelled.relabel(return_map=True)
    back = {integer: _name(name) for name, integer in names.items()}
    return [
        _in_cyclic_order(graph, [back[v] for v in cycle])
        for cycle in relabelled.minimum_cycle_basis()
    ]


def _blocks(graph: Graph) -> list[list[str]]:
    """The 2-connected blocks holding at least one cycle, largest first.

    The cycle space is the direct sum of the blocks' cycle spaces, so every
    generator lies inside one block.  A near-tree has only small blocks.
    """
    blocks, _ = graph.blocks_and_cut_vertices()
    return sorted(
        (sorted(_name(vertex) for vertex in b) for b in blocks if len(b) >= 3),
        key=len,
        reverse=True,
    )


def render_shape(declarations: list[CategoryDeclaration]) -> str:
    """Breadth, depth and shortcuts.  The intended shape is deep and narrow."""
    edges = _all_edges(declarations)
    vertices = _vertices(declarations, edges)
    directed = _digraph(vertices, edges)
    breadth = {
        _name(vertex): d for vertex, d in directed.in_degree(labels=True).items()
    }
    depth = _chains_above(directed)

    lines = [
        "The declared graph as numbers.  Intended shape: near-tree, deep and narrow.",
        "",
        (
            f"categories {directed.order()}   declarations {directed.size()}   pieces {_graph(vertices, edges).connected_components_number()}"
        ),
        f"longest chain of declarations = {max(depth.values(), default=0)}",
        "",
        "## Breadth: categories declared directly by the most others",
        "",
        "Each count is the number of unfactored declarations into that node,",
        "unless every claimant's own definition places it one step below.",
        "",
    ]
    for name in sorted(breadth, key=lambda n: (-breadth[n], n))[:15]:
        if breadth[name]:
            lines.append(f"{breadth[name]:5d}  {name}")

    histogram: dict[int, int] = {}
    for value in depth.values():
        histogram[value] = histogram.get(value, 0) + 1
    lines += ["", "## Depth: longest chain above each category", ""]
    for value in sorted(histogram):
        lines.append(f"  depth {value:2d}: {histogram[value]:4d} categories")

    pieces = sorted(
        (
            [_name(vertex) for vertex in piece]
            for piece in _graph(vertices, edges).connected_components(sort=True)
        ),
        key=len,
        reverse=True,
    )
    lines += [
        "",
        f"## Pieces apart from the largest ({len(pieces) - 1})",
        "",
        "A category here declares nothing the tree defines, or only categories",
        "that declare nothing the tree defines.",
        "",
    ]
    lines.extend(f"{len(piece):5d}  {', '.join(piece)}" for piece in pieces[1:])

    shortcuts = _shortcuts(declarations)
    lines += [
        "",
        f"## Shortcut declarations, dropped by the transitive reduction ({len(shortcuts)})",
        "",
    ]
    lines.extend(f"{below} -> {above}" for below, above in shortcuts)
    return "\n".join(lines) + "\n"


def render_cells(declarations: list[CategoryDeclaration]) -> str:
    r"""Graph homology and cycle witnesses for inspection, not coherence verdicts."""
    from sage.topology.simplicial_complex import SimplicialComplex

    edges = _all_edges(declarations)
    vertices = _vertices(declarations, edges)
    graph = _graph(vertices, edges)
    homology = SimplicialComplex(
        [[vertex] for vertex in sorted(vertices)] + [list(edge) for edge in sorted(edges)]
    ).homology(reduced=False)
    blocks = _blocks(graph)
    shortcuts = _shortcuts(declarations)
    dropped = {frozenset(edge) for edge in shortcuts}

    def through_a_shortcut(cycle: list[str]) -> bool:
        return any(
            frozenset(pair) in dropped for pair in zip(cycle, cycle[1:] + cycle[:1])
        )

    written = {frozenset(edge) for edge in _declared_edges(declarations)}

    def is_axiom_join(cycle: list[str]) -> bool:
        # Inside one base every route is an inclusion of axiom subcategories,
        # and a cycle with at most one written edge closes through edges Sage
        # computes; either way the two routes are the same functor.
        one_base = len({_base_of(v) for v in cycle}) == 1
        written_edges = sum(
            frozenset(pair) in written for pair in zip(cycle, cycle[1:] + cycle[:1])
        )
        return one_base or written_edges <= 1

    lines = [
        "Homology of the declaration graph.",
        "This is the one-dimensional undirected complex, not the category nerve.",
        "Cycles do not by themselves establish missing functors or failed coherence.",
        "",
        f"  0-cells {graph.order()}    1-cells {graph.size()}    2-cells 0",
        f"  H_0 = {homology[0]}    H_1 = {homology[1]}    H_n = 0, n >= 2",
        "",
        f"## 2-connected blocks with a cycle ({len(blocks)}), by size",
        "",
        "Every generator lies inside one block.  A near-tree has only small",
        "blocks; a large block is the region where declarations form a mesh.",
        "",
    ]
    lines.extend(f"{len(block):5d}  {', '.join(block)}" for block in blocks)
    lines += ["", f"## Killed by deleting one declaration ({len(shortcuts)})", ""]
    lines.extend(f"{below} -> {above}" for below, above in shortcuts)

    for block in blocks:
        basis = _minimum_cycle_basis(graph.subgraph(block))
        joins = [c for c in basis if is_axiom_join(c)]
        remaining = [
            c for c in basis if not is_axiom_join(c) and not through_a_shortcut(c)
        ]
        lines += [
            "",
            f"## Computed axiom joins, in the block of {len(block)} ({len(joins)})",
            "",
        ]
        lines.extend(
            " -> ".join(c + c[:1]) for c in sorted(joins, key=lambda c: (len(c), c))
        )
        lines += [
            "",
            f"## Other cycle witnesses for review, in the block of {len(block)} ({len(remaining)})",
            "",
        ]
        lines.extend(
            " -> ".join(c + c[:1]) for c in sorted(remaining, key=lambda c: (len(c), c))
        )
    return "\n".join(lines) + "\n"


def render_dot(declarations: list[CategoryDeclaration]) -> str:
    """The literal declared graph, one edge per declared supercategory."""
    declared = {d.qualified_name for d in declarations} | {d.name for d in declarations}
    lines = [
        "digraph declared_categories {",
        "  rankdir=BT;",
        '  node [shape=box, fontname="Inter"];',
    ]
    for declaration in sorted(declarations, key=lambda d: d.qualified_name):
        for supercategory in declaration.supercategories:
            head = supercategory.head
            style = "" if head in declared else ' [style=dashed, color="#b45309"]'
            target = supercategory.vertex if head in declared else head
            lines.append(f'  "{declaration.qualified_name}" -> "{target}"{style};')
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_json(declarations: list[CategoryDeclaration]) -> str:
    payload = [
        {
            "name": d.name,
            "qualified_name": d.qualified_name,
            "vertex": d.vertex,
            "parameter": d.parameter,
            "axiom_of": d.axiom_of,
            "source": f"{d.path}:{d.line}",
            "bases": list(d.bases),
            "summary": d.summary,
            "declares": d.declares,
            "abstract": d.abstract,
            "supercategories": [
                {
                    "expression": s.expression,
                    "head": s.head,
                    "resolved": s.resolved,
                    "origin": s.origin,
                    "vertex": s.vertex,
                    "axioms": list(s.axioms),
                    "parameters": list(s.parameters),
                }
                for s in d.supercategories
            ],
            "heads": list(d.heads),
        }
        for d in sorted(declarations, key=lambda d: d.qualified_name)
    ]
    return json.dumps(payload, indent=1) + "\n"


@dataclass(frozen=True)
class Dispatch:
    """How an object operation reaches an answer, read from its owner's body.

    ``hooks`` are the protected methods the body calls on ``self``; a category
    below the owner that defines one, or the operation itself, supplies a
    route.  ``branches`` are the memberships the body matches on, each a set of
    vertices an object must lie under together; ``conditional`` marks a branch
    whose guard also tests something other than membership.  ``asserts`` marks
    a body that ends in an assertion when no hook or branch answers; a body
    without one answers on every inheriting category.  An abstract operation
    has neither: every inheriting category must define it.
    """

    operation: str
    owner: str
    source: str
    abstract: bool
    asserts: bool
    hooks: tuple[str, ...]
    branches: tuple[tuple[frozenset[str], bool], ...]


@cache
def _parsed(path: str) -> ast.Module:
    return ast.parse(Path(path).read_text(encoding="utf-8"))


def _construction_axioms(
    declarations: list[CategoryDeclaration], axiom_names: set[str]
) -> dict[str, tuple[str, ...]]:
    """The constructions on a category or an object, and the property axioms each names.

    A construction declares only categories computed from its parameters,
    or another construction: a slice ``C/X`` declares ``C``.  An axiom it
    names is one it can place on the objects it builds.
    """
    names: set[str] = set()
    while True:
        grown = names | {
            d.name
            for d in declarations
            if d.supercategories
            and all(
                s.origin == "expression" or s.resolved in names
                for s in d.supercategories
            )
        }
        if grown == names:
            break
        names = grown
    found: dict[str, tuple[str, ...]] = {}
    for d in declarations:
        if d.name not in names:
            continue
        node, _ = _class_at(d)
        # Only the category's declared supercategories place properties on
        # every object.  An unrelated object method referring to an affine
        # scheme does not make an atlas or a divisor group an affine scheme.
        placement_methods = tuple(
            member for member in node.body
            if isinstance(member, ast.FunctionDef)
            and member.name in {"super_categories", "extra_super_categories"}
        )
        found[d.name] = tuple(
            sorted(
                {
                    n.func.attr
                    for method in placement_methods
                    for n in ast.walk(method)
                    if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr in axiom_names
                }
            )
        )
    return found


def _class_at(
    declaration: CategoryDeclaration,
) -> tuple[ast.ClassDef, dict[str, tuple[str, str]]]:
    tree = _parsed(declaration.path)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.lineno == declaration.line:
            return node, _imported_names(tree)
    raise AssertionError(f"no class at {declaration.path}:{declaration.line}")


def _membership(
    node: ast.expr, imported: dict[str, tuple[str, str]], factories: dict[str, str]
) -> str | None:
    """The vertex ``X`` of a guard ``self in X``, or nothing for any other test."""
    match node:
        case ast.Compare(
            left=ast.Name(id="self"), ops=[ast.In()], comparators=[category]
        ):
            text = _unfold(ast.unparse(category), factories, imported)
            return _vertex(_resolved(_head(text), imported), _axioms(text))
    return None


_THE_OBJECT = ast.Name(id="self")
"""The guard of a body reached without a branch: it is about the object."""


def _hook_called(node: ast.AST) -> str | None:
    """The name ``_x`` when ``node`` is a call ``self._x(...)`` of a protected method of the object."""
    match node:
        case ast.Call(func=ast.Attribute(value=ast.Name(id="self"), attr=attr)) if (
            attr.startswith("_") and not attr.startswith("__")
        ):
            return attr
    return None


def _about_the_object(test: ast.expr, hooked: set[str]) -> bool:
    """Whether an assertion tests the object itself or what one of its hooks returned.

    ``assert ring in IntegralDomains()`` states a hypothesis on a parameter,
    not the absence of a route for the object.
    """
    names = {node.id for node in ast.walk(test) if isinstance(node, ast.Name)}
    return "self" in names or bool(names & hooked)


def _ends_in_assertion(
    body: list[ast.stmt], hooked: set[str], guard: ast.expr = _THE_OBJECT
) -> bool:
    """Whether the statement reached when every earlier branch falls through asserts about the object.

    A precondition such as ``assert other in Sets()`` opens a body and is not
    this; the last statement, an assertion just before a final ``return``, the
    last case of a final ``match`` and the ``else`` of a final ``if`` are.  A
    ``raise`` is judged by the guard that reaches it, so the last case of
    ``match ring:`` states a hypothesis on the ring.
    """
    match body[-2:]:
        case [ast.Assert(test=test), ast.Return()]:
            return _about_the_object(test, hooked)
    match body[-1]:
        case ast.Assert(test=test):
            return _about_the_object(test, hooked)
        case ast.Raise():
            return _about_the_object(guard, hooked)
        case ast.Match(subject=subject, cases=cases):
            guards = [case.guard for case in cases if case.guard is not None]
            return _ends_in_assertion(
                cases[-1].body, hooked, ast.Tuple(elts=[subject, *guards])
            )
        case ast.If(test=test, orelse=orelse) if orelse:
            return _ends_in_assertion(orelse, hooked, test)
    return False


def _dispatch(
    declaration: CategoryDeclaration, operation: str, factories: dict[str, str]
) -> Dispatch:
    node, imported = _class_at(declaration)
    method = _object_methods(node)[operation]
    hooks = sorted(
        {hook for node in ast.walk(method) if (hook := _hook_called(node)) is not None}
    )
    branches: list[tuple[frozenset[str], bool]] = []
    consumed: set[int] = set()
    for test in ast.walk(method):
        if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
            found = {
                vertex
                for value in test.values
                if (vertex := _membership(value, imported, factories)) is not None
            }
            consumed.update(id(value) for value in test.values)
            if found:
                branches.append((frozenset(found), len(found) < len(test.values)))
    for test in ast.walk(method):
        if (
            isinstance(test, ast.Compare)
            and id(test) not in consumed
            and (vertex := _membership(test, imported, factories)) is not None
        ):
            branches.append((frozenset({vertex}), False))
    return Dispatch(
        operation=operation,
        owner=declaration.vertex,
        source=f"{declaration.path}:{method.lineno}",
        abstract=_is_abstract(method),
        asserts=_ends_in_assertion(
            method.body,
            {
                target.id
                for assignment in ast.walk(method)
                if isinstance(assignment, ast.Assign)
                and any(
                    _hook_called(node) is not None
                    for node in ast.walk(assignment.value)
                )
                for target in assignment.targets
                if isinstance(target, ast.Name)
            },
        ),
        hooks=tuple(hooks),
        branches=tuple(dict.fromkeys(branches)),
    )


def _up_sets(declarations: list[CategoryDeclaration]) -> dict[str, set[str]]:
    """Every vertex above each vertex, strictly, along declared and axiom edges."""
    edges = _all_edges(declarations)
    vertices = _vertices(declarations, edges)
    supers = {v: {b for a, b in edges if a == v} for v in vertices}
    above: dict[str, set[str]] = {}
    for vertex in TopologicalSorter(supers).static_order():
        above[vertex] = set(supers[vertex])
        for parent in supers[vertex]:
            above[vertex].update(above[parent])
    return above


def _realization_methods(
    declarations: list[CategoryDeclaration],
) -> dict[str, list[str]]:
    """Methods of the classes that are not categories, by method name."""
    found: dict[str, list[str]] = {}
    for path in sorted({Path(d.path) for d in declarations}):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        categories = {d.line for d in declarations if Path(d.path) == path}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.lineno not in categories
                and node.name != "ParentMethods"
            ):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        found.setdefault(method.name, []).append(
                            f"{node.name} {path}:{method.lineno}"
                        )
    return found


def render_routes(
    declarations: list[CategoryDeclaration], operations: list[str]
) -> str:
    """Each category that inherits an object operation, and what answers it there.

    An operation is placed where it is defined; whether it answers on the
    objects of a category below is a separate fact.  The owner's body reaches
    an answer through protected hooks, through branches on membership, or, for
    an abstract operation, through an override.  A category below the owner
    with none of these in its up-set inherits the operation with only the
    owner's assertion.  Without ``--operation`` the view lists only operations
    whose body asserts; an abstract operation is a contract on the classes
    that realize objects, and is listed when it is named.
    A construction declaring only its parameter (``SliceCategory(C, X)``
    declares ``C``) inherits every operation of every category it is applied
    to, so it is listed under every operation.

    This is a source reading.  A realization class outside the category graph
    may supply a hook for its own objects; those classes are listed, and they
    route only the objects they construct.
    """
    above = _up_sets(declarations)
    by_vertex = {d.vertex: d for d in declarations}
    parameterized = {
        d.vertex
        for d in declarations
        if d.supercategories
        and all(s.origin == "expression" for s in d.supercategories)
    }
    on_parameter = {v for v in above if v in parameterized or above[v] & parameterized}
    realizations = _realization_methods(declarations)
    factories = _factories(
        [
            ast.parse(path.read_text(encoding="utf-8"))
            for path in sorted({Path(d.path) for d in declarations})
        ]
    )

    definers: dict[str, list[str]] = {}
    for d in declarations:
        for name in d.object_methods:
            if not name.startswith("_"):
                definers.setdefault(name, []).append(d.vertex)
    selected = operations or sorted(definers)
    unknown = [name for name in selected if name not in definers]
    assert not unknown, f"no category defines the object operation(s) {unknown!r}"

    reports: list[tuple[int, list[str]]] = []
    for name in selected:
        owners = [
            v
            for v in definers[name]
            if not any(other in above.get(v, set()) for other in definers[name])
        ]
        for owner in sorted(owners):
            dispatch = _dispatch(by_vertex[owner], name, factories)
            if not (dispatch.abstract or dispatch.asserts):
                if operations:
                    reports.append(
                        (
                            0,
                            [
                                f"## {name}, introduced by {owner} ({dispatch.source})",
                                "",
                                "its body answers on every inheriting category; it ends in no assertion",
                            ],
                        )
                    )
                continue
            if dispatch.abstract and not operations:
                continue
            supplies = {name, *dispatch.hooks}
            inheritors = sorted(v for v in above if owner in above[v]) + sorted(
                v for v in on_parameter if owner not in above[v] and v != owner
            )
            routes: dict[str, str] = {}
            for vertex in inheritors:
                reach = above[vertex] | {vertex}
                providers = sorted(
                    w
                    for w in reach
                    if w != owner
                    and w in by_vertex
                    and supplies & set(by_vertex[w].object_methods)
                    and (owner in above[w] or w in on_parameter)
                )
                taken = [
                    " and ".join(sorted(members))
                    + (" (with a further condition)" if conditional else "")
                    for members, conditional in dispatch.branches
                    if members <= reach
                ]
                routes[vertex] = "; ".join(
                    [
                        *(f"defined at {w}" for w in providers),
                        *(f"branch on {t}" for t in taken),
                    ]
                )
            fallback = {vertex for vertex, route in routes.items() if not route}
            topmost = sorted(
                vertex for vertex in fallback if not (above[vertex] & fallback)
            )
            definitions = sorted(
                {
                    w
                    for vertex in inheritors
                    for w in [vertex]
                    if w in by_vertex and supplies & set(by_vertex[w].object_methods)
                }
            )
            lines = [
                f"## {name}, defined at {owner} ({dispatch.source})",
                "",
                "abstract: every inheriting category must define it"
                if dispatch.abstract
                else f"its hooks: {', '.join(dispatch.hooks) or 'none'}",
                f"its branches: {'; '.join(dict.fromkeys(' and '.join(sorted(m)) for m, _ in dispatch.branches)) or 'none'}",
                f"categories below it that define {name} or a hook: {', '.join(definitions) or 'none'}",
            ]
            hooked = sorted(
                {entry for hook in supplies for entry in realizations.get(hook, [])}
            )
            if hooked:
                lines += [
                    f"realization classes defining {name} or a hook, for the objects they construct:",
                    *(f"  {entry}" for entry in hooked),
                ]
            lines += [
                "",
                f"### Topmost categories whose objects reach the fallback assertion ({len(topmost)})",
                "",
                "An override or a functor to an answering category at one of these covers the categories below it.",
                "",
            ]
            lines += [
                f"{vertex}{'  [a construction on its parameter category]' if vertex in on_parameter else ''}"
                f"  ({sum(1 for other in fallback if vertex in above[other])} below it also reach it)"
                for vertex in topmost
            ] or ["none"]
            if operations:
                lines += [
                    "",
                    f"### Categories answered, and how ({len(routes) - len(fallback)})",
                    "",
                ]
                lines += [
                    f"{vertex}  <- {route}"
                    for vertex, route in sorted(routes.items())
                    if route
                ] or ["none"]
            reports.append((len(topmost), lines))
    header = [
        "Object operations whose definition ends in a fallback assertion, read from source.",
        "Each section names where the operation is defined and overridden, then the",
        "topmost categories whose objects reach that fallback: no override, hook",
        "definition or case of the definition applies anywhere above them.",
        "",
    ]
    body = [
        line
        for _, lines in sorted(reports, key=lambda r: -r[0])
        for line in [*lines, ""]
    ]
    return "\n".join(header + body)


def _construction_sites(
    root: Path, factories: dict[str, str], trees: dict[Path, ast.Module] | None = None
) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """Every function that builds an object with ``_object_of``, and what it places on that object.

    Each site gives its location, the category it places the object in when
    no guard applies, and the pairs (property of an input, category added to
    the result) read from guards ``x in P`` whose branch places the result
    in a further category.
    """
    sites = []
    if trees is None:
        trees = {
            path: ast.parse(path.read_text(encoding="utf-8"))
            for path in sorted(root.rglob("*.py"))
        }
    for path, tree in trees.items():
        imported = _imported_names(tree)

        def vertex_of(
            node: ast.expr, imported: dict[str, tuple[str, str]] = imported
        ) -> str:
            text = _unfold(ast.unparse(node), factories, imported)
            return _vertex(_resolved(_head(text), imported), _axioms(text))

        def placed(statements: list[ast.stmt]) -> list[str]:
            found = []
            for statement in statements:
                # A nested guard has its own hypotheses.  Its placement is
                # not a consequence of an enclosing, weaker guard alone.
                if isinstance(statement, (ast.If, ast.Match, ast.For, ast.While)):
                    continue
                for node in ast.walk(statement):
                    match node:
                        case ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="placements"), attr="append"
                            ),
                            args=[category],
                        ):
                            found.append(vertex_of(category))
                        case ast.Assign(
                            targets=[ast.Name(id="placement")], value=category
                        ):
                            found.append(vertex_of(category))
            return found

        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef):
                continue
            calls = [
                node
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_object_of"
            ]
            if not calls:
                continue
            guarded: list[tuple[ast.expr, list[ast.stmt]]] = []
            for node in ast.walk(function):
                match node:
                    case ast.If(test=test, body=body):
                        guarded.append((test, body))
                    case ast.match_case(guard=guard, body=body) if guard is not None:
                        guarded.append((guard, body))
            pairs = []
            for test, body in guarded:
                # Do not turn one conjunct of a compound guard into a
                # sufficient hypothesis (enumerated factors alone never
                # make their Cartesian product finite).
                inputs = (
                    [vertex_of(test.comparators[0])]
                    if isinstance(test, ast.Compare)
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.In)
                    and isinstance(test.left, ast.Name)
                    else []
                )
                for result in placed(body):
                    pairs.extend((source, result) for source in inputs)
            default = ", ".join(
                sorted({ast.unparse(call.args[0]) for call in calls if call.args})
            )
            sites.append(
                (
                    f"{path}:{function.lineno} {function.name}",
                    default,
                    list(dict.fromkeys(pairs)),
                )
            )
    return sites


def render_properties(declarations: list[CategoryDeclaration], root: Path) -> str:
    """For each property axiom: the categories under it, and the construction sites that place results under it.

    A viewer for auditing by hand. It lists what the source declares and places and
    judges nothing: whether a result belongs under a property is for the reader.
    """
    above = _up_sets(declarations)
    by_vertex = {d.vertex: d for d in declarations}
    factories = _factories(
        [
            ast.parse(path.read_text(encoding="utf-8"))
            for path in sorted(root.rglob("*.py"))
        ]
    )
    sites = _construction_sites(root, factories)
    axiom_vertices = sorted(
        v
        for v in above
        if "." in v
        and "::" not in v
        and len(v.split(".")) == 2
        and v.split(".")[0] in by_vertex
    )
    reports: list[tuple[int, list[str]]] = []
    for axiom_vertex in axiom_vertices:
        below = sorted(v for v in above if axiom_vertex in above[v])
        propagating = sorted(
            {
                (site, source, result)
                for site, _, pairs in sites
                for source, result in pairs
                if result == axiom_vertex
            }
        )
        lines = [
            f"## {axiom_vertex}",
            "",
            f"### Categories under {axiom_vertex} ({len(below)})",
            "",
            ", ".join(below) or "none",
        ]
        lines += [
            "",
            f"### Construction sites placing their result in {axiom_vertex} from a property of an input ({len(propagating)})",
            "",
        ]
        lines += [f"{site}: input in {source}" for site, source, _ in propagating] or [
            "none"
        ]
        reports.append((len(below), lines))
    axiom_names = {v.split(".")[1] for v in axiom_vertices}
    construction_axioms = _construction_axioms(declarations, axiom_names)
    constructions = [
        f"{d.vertex}  ({d.path}:{d.line}) declares {', '.join(s.expression for s in d.supercategories)}; "
        f"places {', '.join(construction_axioms[d.name]) or 'no property axiom'}"
        for d in sorted(declarations, key=lambda d: d.vertex)
        if d.name in construction_axioms
    ]
    constructions_section = [
        "## Constructions on a category or an object, and the property axioms they place on their objects",
        "",
        "A slice, subobject or quotient of a finite object is finite. A construction that names",
        "no property axiom puts every object it builds in the categories it declares, whatever",
        "properties its base object has.",
        "",
        *constructions,
        "",
    ]
    stating = {site for site, _, pairs in sites if pairs}
    silent = [
        f"{site}: places in {default or 'a computed category'}"
        for site, default, pairs in sites
        if site not in stating
    ]
    lines = [
        "## Construction sites that place their result by no property of their input",
        "",
        "A subset, quotient, product or image of a finite set is finite; a site listed here",
        "places what it builds in the same category whatever its inputs are.",
        "",
        *silent,
    ]
    header = [
        "Property axioms, the categories under them, and the construction sites that place results under them, read from source.",
        "",
    ]
    body = [
        line
        for _, lines_ in sorted(reports, key=lambda r: -r[0])
        for line in [*lines_, ""]
    ]
    return "\n".join([*header, *body, *constructions_section, *lines, ""])


def _returns(function: ast.FunctionDef) -> list[ast.expr]:
    """The returned expressions of ``function``, not of the functions nested in it."""
    found: list[ast.expr] = []
    pending: list[ast.AST] = list(function.body)
    while pending:
        node = pending.pop()
        match node:
            case ast.FunctionDef() | ast.Lambda() | ast.ClassDef():
                continue
            case ast.Return(value=value) if value is not None:
                found.append(value)
        pending.extend(ast.iter_child_nodes(node))
    return found


def _signature(function: ast.FunctionDef) -> str:
    names = [a.arg for a in function.args.args[1:]] + [
        a.arg for a in function.args.kwonlyargs
    ]
    return ", ".join(names)


def render_constructions(
    declarations: list[CategoryDeclaration],
    root: Path,
    selected: list[str],
    inferred: dict[str, dict[str, dict[str, str]]],
) -> str:
    """Each operation on the objects of a category that builds an object, and where the result is placed.

    The route is followed through the source: a module function, a method of
    the same object, a method of a category, an application of a category to
    data, ``_object_of`` and ``_with_structure``.  The lines state what the
    source places; whether that placement is the mathematics is for the
    reader.  A subset of a finite set placed only in ``Sets/X`` reads as
    wrong at sight, beside a subset placed in ``Sets.Finite`` when ``X`` is.
    """
    trees = {
        path: ast.parse(path.read_text(encoding="utf-8"))
        for path in sorted(root.rglob("*.py"))
    }
    factories = _factories(list(trees.values()))
    # The import base is the first ancestor outside the package's
    # __init__.py chain, which is src/ for src/sage_extensions; a root that is
    # not a package is read two levels down from where it lies.
    source_root = root.parent
    while (source_root / "__init__.py").exists():
        source_root = source_root.parent
    if not (root / "__init__.py").exists():
        source_root = root.parents[1]
    module_paths = {
        ".".join(path.relative_to(source_root).with_suffix("").parts): path
        for path in trees
    }
    imports = {path: _imported_names(tree) for path, tree in trees.items()}
    by_name = {d.name: d for d in declarations if not d.axiom_of and not d.nested_in}
    classes = {name: _class_at(d)[0] for name, d in by_name.items()}
    sites = {
        site: (default, pairs)
        for site, default, pairs in _construction_sites(root, factories, trees)
    }
    above = _up_sets(declarations)
    construction_axioms = _construction_axioms(
        declarations,
        {v.split(".")[1] for v in above if v.count(".") == 1 and "::" not in v},
    )

    def category_class(expression: ast.expr) -> str | None:
        head = _head(ast.unparse(expression))
        head = factories.get(head, head)
        head = _head(head)
        return head if head in classes else None

    def class_method(name: str, method: str) -> ast.FunctionDef | None:
        for statement in classes[name].body:
            if isinstance(statement, ast.FunctionDef) and statement.name == method:
                return statement
        return None

    def placed_by(expression: ast.expr) -> str:
        r"""What applying the category ``expression`` places its result in, read from its class."""
        match expression:
            case ast.Call(func=ast.Attribute(value=owner, attr=method)) if (
                name := category_class(owner)
            ) and (found := class_method(name, method)):
                returned = _returns(found)
                if returned:
                    return placed_by(returned[0])
        name = category_class(expression)
        if name is None:
            return ast.unparse(expression)
        d = by_name[name]
        declared = ", ".join(s.expression for s in d.supercategories) or "nothing"
        stated = f"{name}, which declares {declared}"
        if name in construction_axioms:
            axioms = construction_axioms[name]
            stated += "; it places " + (
                ", ".join(axioms)
                if axioms
                else "no property of its parameters or base object"
            )
        return stated

    def module_function(name: str, path: Path) -> tuple[ast.FunctionDef, Path] | None:
        r"""The module-level function ``name`` means in ``path``: defined there, or imported."""
        for statement in trees[path].body:
            if isinstance(statement, ast.FunctionDef) and statement.name == name:
                return statement, path
        if name in imports[path]:
            module, original = imports[path][name]
            target = module_paths.get(module)
            if target is not None:
                for statement in trees[target].body:
                    if isinstance(statement, ast.FunctionDef) and statement.name == original:
                        return statement, target
        return None

    def inherited_method(
        owner: str, container: str, name: str
    ) -> tuple[ast.FunctionDef, Path, str, dict[str, ast.FunctionDef]] | None:
        r"""The method ``name`` that ``owner``'s objects inherit through ``container``."""
        vertex = by_name[owner].vertex if owner in by_name else owner
        for ancestor in sorted(above.get(vertex, set())):
            if ancestor in classes:
                found = _container_methods(classes[ancestor], container)
                if name in found:
                    return found[name], Path(by_name[ancestor].path), ancestor, found
        return None

    def assigned(function: ast.FunctionDef, variable: str) -> ast.expr | None:
        r"""The last value bound to the local ``variable`` in ``function``'s own body."""
        value: ast.expr | None = None
        for node in ast.walk(function):
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == variable
                for target in node.targets
            ):
                value = node.value
        return value

    def trace(
        function: ast.FunctionDef,
        path: Path,
        owner: str,
        methods: dict[str, ast.FunctionDef],
        depth: int,
        container: str = "ParentMethods",
    ) -> list[str]:
        site = f"{path}:{function.lineno} {function.name}"
        if site in sites:
            default, pairs = sites[site]
            stated = "; ".join(
                f"{result} when an input is in {source}" for source, result in pairs
            )
            return [
                f"placed in {default if default and not default.isidentifier() else 'a category computed in the body'}"
                + (
                    f"; {stated}"
                    if stated
                    else "; no property of an input changes the placement"
                )
            ]
        outcomes: list[str] = []
        pending = list(_returns(function))
        seen_locals: set[str] = set()
        while pending:
            value = pending.pop(0)
            match value:
                case ast.Constant(value=bool()) | ast.Compare() | ast.UnaryOp(
                    op=ast.Not()
                ) | ast.BoolOp():
                    outcomes.append("a truth value, not an object")
                case ast.Constant(value=None):
                    outcomes.append("None, not an object")
                case ast.Name(id="self"):
                    outcomes.append(f"the input itself, in {owner}")
                case ast.Name(id=variable) if variable not in seen_locals and (
                    bound := assigned(function, variable)
                ) is not None:
                    seen_locals.add(variable)
                    pending.append(bound)
                case ast.Call(
                    func=ast.Attribute(attr="_with_structure"),
                    args=[ast.Tuple(elts=elts), *_],
                ):
                    added = ", ".join(
                        owner if ast.unparse(e) == "self" else ast.unparse(e)
                        for e in elts
                    )
                    outcomes.append(
                        f"the input object, placed also in {added}; no property of the input changes the placement"
                    )
                case (
                    ast.Call(func=ast.Call() as category)
                    | ast.Call(
                        func=ast.Attribute(value=ast.Call() as category, attr="object")
                    )
                ) if category_class(category.func):
                    outcomes.append(
                        f"an object of {ast.unparse(category)}, that is of {placed_by(category)}"
                    )
                case ast.Call(func=ast.Name(id=name)) if depth and (
                    callee := module_function(name, path)
                ):
                    outcomes.extend(
                        trace(callee[0], callee[1], owner, methods, depth - 1, container)
                    )
                case ast.Call(
                    func=ast.Attribute(value=ast.Name(id="self"), attr=name)
                ) if depth and name in methods:
                    outcomes.extend(
                        trace(methods[name], path, owner, methods, depth - 1, container)
                    )
                case ast.Call(
                    func=ast.Attribute(value=ast.Name(id="self"), attr=name)
                ) if depth and (inherited := inherited_method(owner, container, name)):
                    found, found_path, ancestor, found_methods = inherited
                    outcomes.extend(
                        trace(found, found_path, ancestor, found_methods, depth - 1, container)
                    )
                case ast.Call(func=ast.Attribute(value=receiver, attr=name)) if (
                    depth
                    and (cls := category_class(receiver))
                    and (found := class_method(cls, name))
                ):
                    outcomes.extend(
                        trace(found, Path(by_name[cls].path), cls, methods, depth - 1)
                    )
        return list(dict.fromkeys(outcomes))

    lines = [
        "Every public operation a category gives its objects, elements and morphisms, and the category the source places its result in.",
        "",
    ]
    containers = (
        ("ParentMethods", "Objects X", "X"),
        ("ElementMethods", "Elements x of objects", "x"),
        ("MorphismMethods", "Morphisms f", "f"),
    )
    for d in sorted(by_name.values(), key=lambda d: d.name):
        if selected and not any(fnmatchcase(d.name, p) for p in selected):
            continue
        node, _ = _class_at(d)
        kind = (
            " (a construction on a category or an object)"
            if d.name in construction_axioms
            else ""
        )
        for container, subject, symbol in containers:
            methods = _container_methods(node, container)
            rows = []
            for name, method in methods.items():
                if name.startswith("_"):
                    continue
                at_runtime = inferred.get(d.name, {}).get(container, {}).get(name)
                outcomes = trace(method, Path(d.path), d.name, methods, 4, container) or [
                    f"{at_runtime}, read from the returned value's class"
                    if at_runtime
                    else "not resolved from the source, and not inferred at runtime (it needs arguments or "
                    "its category has no example object); it returns "
                    + ("; ".join(ast.unparse(v) for v in _returns(method)) or "nothing")
                ]
                rows.append(
                    f"  {symbol}.{name}({_signature(method)})  ->  " + "  |  ".join(outcomes)
                )
            if rows:
                lines += [
                    f"## {subject} of {d.name}{kind}  ({d.path}:{d.line})",
                    "",
                    *rows,
                    "",
                ]
    return "\n".join(lines)


def _default_root() -> Path:
    return Path(importlib.util.find_spec("sage_extensions").origin).parent


def select_vertices(
    declarations: list[CategoryDeclaration],
    patterns: list[str],
    direction: str,
    between: list[str],
    remove: list[str],
) -> tuple[set[str], set[tuple[str, str]]]:
    """Slice declared reachability; conditional declarations remain a union.

    Dynamic programming follows Python's dependency order, not a local graph
    algorithm: https://docs.python.org/3/library/graphlib.html
    A cyclic relation raises CycleError and cannot be presented as a poset.
    """
    edges = _all_edges(declarations)
    vertices = _vertices(declarations, edges)
    supers = {v: {b for a, b in edges if a == v} for v in vertices}
    above: dict[str, set[str]] = {}
    for vertex in TopologicalSorter(supers).static_order():
        above[vertex] = set(supers[vertex])
        for parent in supers[vertex]:
            above[vertex].update(above[parent])
    seeds = {v for v in vertices if any(fnmatchcase(v, p) for p in patterns)}
    unmatched = [p for p in patterns if not any(fnmatchcase(v, p) for v in vertices)]
    assert not unmatched, f"No declared vertices match {unmatched!r}"
    assert not patterns or seeds, f"No declared vertices match {patterns!r}"
    selected = set(vertices) if not patterns else seeds.copy()
    if direction in {"up", "both"}:
        selected.update(v for seed in seeds for v in above[seed])
    if direction in {"down", "both"}:
        selected.update(v for v in vertices if above[v] & seeds)
    if between:
        lower, upper = between
        assert lower in above and upper in above, (
            f"Unknown interval endpoints: {between!r}"
        )
        assert lower == upper or upper in above[lower], (
            f"Endpoints are not ordered: {between!r}"
        )
        selected &= (above[lower] | {lower}) & {
            v for v in vertices if v == upper or upper in above[v]
        }
    unmatched_removals = [
        p for p in remove if not any(fnmatchcase(v, p) for v in selected)
    ]
    assert not unmatched_removals, (
        f"No selected vertices match removal patterns {unmatched_removals!r}"
    )
    selected -= {v for v in selected if any(fnmatchcase(v, p) for p in remove)}
    for vertex in selected:
        declarations_of_vertex = [
            f"{d.path}:{d.line}" for d in declarations if d.vertex == vertex
        ]
        assert len(declarations_of_vertex) <= 1, (
            f"Ambiguous source vertex {vertex}: {declarations_of_vertex}; inspect raw declarations"
        )
    return selected, {(a, b) for a, b in edges if a in selected and b in selected}


def _self_declarations(declarations: list[CategoryDeclaration]) -> list[str]:
    """Categories declaring their own vertex, which the edge set drops; ``audit`` reports them."""
    return sorted(
        f"{d.vertex} {d.path}:{d.line}"
        for d in declarations
        if any(s.vertex == d.vertex for s in d.supercategories)
    )


def render_slice(
    declarations: list[CategoryDeclaration],
    vertices: set[str],
    edges: set[tuple[str, str]],
) -> str:
    declared = _declared_edges(declarations)
    return json.dumps(
        {
            "basis": "source declarations plus computed axiom edges; unresolved conditional branches are unioned",
            "orientation": "subcategory -> supercategory",
            "vertices": sorted(vertices),
            "edges": sorted(edges),
            "edge_evidence": [
                {
                    "from": a,
                    "to": b,
                    "kind": "declared or parameter projection"
                    if (a, b) in declared
                    else "computed axiom edge",
                    "declaration_sources": [
                        f"{d.path}:{d.line}" for d in declarations if d.vertex == a
                    ],
                }
                for a, b in sorted(edges)
            ],
            "declarations": json.loads(
                render_json([d for d in declarations if d.vertex in vertices])
            ),
            "self_declarations": _self_declarations(declarations),
            "boundary": "Parameters, dynamic returns and aliases require source review; absent paths are not proofs of missing mathematics.",
        },
        indent=2,
    )


def render_topology(
    vertices: set[str],
    edges: set[tuple[str, str]],
    complex_kind: str,
    max_vertices: int,
    fundamental_group: bool,
) -> str:
    """Delegate explicitly chosen complexes to Sage, retaining all isolated vertices.

    References: Sage Graph.clique_complex, FinitePoset.order_complex, and
    SimplicialComplex.homology/fundamental_group in the Sage reference manual.
    """
    from sage.combinat.posets.posets import Poset
    from sage.graphs.digraph import DiGraph
    from sage.graphs.graph import Graph
    from sage.topology.simplicial_complex import SimplicialComplex

    assert vertices, "Select a nonempty category slice"
    assert len(vertices) <= max_vertices, (
        f"Slice has {len(vertices)} vertices; narrow it or explicitly raise --max-vertices={max_vertices}"
    )
    graph = Graph([sorted(vertices), sorted(edges)], format="vertices_and_edges")
    match complex_kind:
        case "graph":
            complex_ = SimplicialComplex(
                [[v] for v in sorted(vertices)] + [list(e) for e in sorted(edges)]
            )
        case "flag":
            complex_ = graph.clique_complex()
        case "order":
            directed = DiGraph(
                [sorted(vertices), sorted(edges)], format="vertices_and_edges"
            )
            complex_ = Poset(directed, facade=True).order_complex()
        case _:
            raise ValueError(complex_kind)
    lines = [
        f"# {complex_kind} complex of the selected category relation",
        "",
        "These invariants describe this complex; they are not architecture scores.",
        "A clique fills a simplex in the flag complex. An order complex uses chains.",
        "A global top or bottom makes the order complex contractible; inspect proper intervals when appropriate.",
        f"Vertices: {', '.join(sorted(vertices))}",
        f"Facets: {complex_.facets()}",
        f"f-vector: {complex_.f_vector()}",
        f"Integral unreduced homology: {complex_.homology(reduced=False)}",
        f"Connected components: {graph.connected_components(sort=True)}",
    ]
    if fundamental_group:
        assert graph.is_connected(), (
            "Select one connected component for the fundamental group"
        )
        lines.append(
            f"Fundamental group presentation: {complex_.fundamental_group(simplify=False)}"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List every declared category and its declared supercategories, without importing the tree."
    )
    parser.add_argument("root", nargs="?", type=Path, default=_default_root())
    parser.add_argument(
        "--format",
        choices=(
            "table",
            "by-supercategory",
            "foreign",
            "audit",
            "shape",
            "cells",
            "dot",
            "json",
            "slice",
            "topology",
            "routes",
            "properties",
            "constructions",
        ),
        default="table",
    )
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument(
        "--select", action="append", default=[], help="category vertex glob; repeatable"
    )
    parser.add_argument(
        "--inferred",
        type=Path,
        help="JSON from sage_extensions.testing.category_inference: the categories of returned values, read at runtime",
    )
    parser.add_argument(
        "--direction", choices=("self", "up", "down", "both"), default="self"
    )
    parser.add_argument("--between", nargs=2, default=[], metavar=("LOWER", "UPPER"))
    parser.add_argument(
        "--remove",
        action="append",
        default=[],
        help="remove vertex glob from the selected complex",
    )
    parser.add_argument(
        "--complex", choices=("graph", "flag", "order"), default="order"
    )
    parser.add_argument(
        "--max-vertices", type=int, default=40, help="explicit size bound for topology"
    )
    parser.add_argument("--fundamental-group", action="store_true")
    parser.add_argument(
        "--operation",
        action="append",
        default=[],
        help="object operation for --format routes; repeatable",
    )
    arguments = parser.parse_args()

    declarations = read_tree(arguments.root)
    if arguments.format in {"slice", "topology"}:
        vertices, edges = select_vertices(
            declarations,
            arguments.select,
            arguments.direction,
            arguments.between,
            arguments.remove,
        )
        rendered = (
            render_slice(declarations, vertices, edges)
            if arguments.format == "slice"
            else render_topology(
                vertices,
                edges,
                arguments.complex,
                arguments.max_vertices,
                arguments.fundamental_group,
            )
        )
        if arguments.output:
            arguments.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered)
        return
    if arguments.format == "routes":
        print(render_routes(declarations, arguments.operation), end="")
        return
    if arguments.format == "constructions":
        print(
            render_constructions(
                declarations,
                arguments.root,
                arguments.select,
                json.loads(arguments.inferred.read_text(encoding="utf-8"))
                if arguments.inferred
                else {},
            ),
            end="",
        )
        return
    if arguments.format == "properties":
        print(render_properties(declarations, arguments.root), end="")
        return
    if arguments.select or arguments.between or arguments.remove:
        parser.error("selection options require --format slice or topology")
    rendered = {
        "table": render_table,
        "by-supercategory": render_by_supercategory,
        "foreign": render_foreign,
        "audit": render_audit,
        "shape": render_shape,
        "cells": render_cells,
        "dot": render_dot,
        "json": render_json,
    }[arguments.format](declarations)

    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
