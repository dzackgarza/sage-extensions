r"""The category graph the source declares, read with ``ast``.

``AGENTS.md`` reads a change to a category's placement on the declared graph:
the breadth of the node it lands under, the depth of a leaf, the declaration
that is a shortcut, the cycles that owe a 2-cell, the size of the largest
2-connected block.  A session cannot answer those questions.  Importing the
preamble gives the categories Sage joined -- the classes that survived the
dynamic construction, with computed supercategories already flattened -- while
the rule is about the declaration a contributor wrote.

So the declarations are read out of the source with ``ast``, and
``sage_extensions`` is not imported at all: a tree that is mid-refactor and does
not load still has its graph, and a declaration read wrongly here is a fact
about the source rather than about an import.

**What a declaration states.**  A ``super_categories`` (or
``extra_super_categories``) return of ``[D(...)]`` in ``class C`` asserts the
forgetful functor ``C -> D``, which is one edge of the complex.  The expressions
a return may carry, and what each contributes:

===============================  ===========================================
written                          read as
===============================  ===========================================
``D()``, ``D(ring)``             the vertex ``D``; the parameter is recorded
                                 as written, never evaluated
``D().FinitelyGenerated()``      the vertex ``D`` refined by that name, which
                                 is a vertex of its own declaring ``D``
``D().Subobjects(X)``            ``D.Subobjects`` when the tree presents that
                                 class, else the vertex ``D`` with the
                                 construction named and its parameters
                                 recorded as written
===============================  ===========================================

A step of the expression names a category when it takes no parameter -- the
join Sage builds, ``Finite``, ``FinitelyGenerated``, ``Even`` -- and is a
construction applied to the category when it takes one.  That is the same
distinction the source writes: a refinement is a category an object of ``D``
also belongs to, and a construction is a category built from ``D`` and
something else.  A refined vertex declares each vertex with one refinement
fewer, which is the node the refinement adjoins and where an object that drops
it lands.

A vertex is therefore the module that defines the class, the qualified class
name, and the refinement set adjoined to it, sorted: ``Lattices().Even().
Nondegenerate()`` and ``Lattices().Nondegenerate().Even()`` are one vertex,
because the join is by set.

**What it refuses to state.**  A return that is a local (``return categories``),
a call to a helper of unknown result (``_distinct_supercategories(supers)``), or
a category computed from the instance (``self.base_category()``) names no
category in the source: the edge is not written down anywhere.  Such a return is
recorded against the class with its expression as written and marked
``computed``, and :func:`audit_rows` lists it.  Working out which category the
expression will evaluate to would put an edge in the graph that nobody wrote,
which is the one thing a reader of declarations must not do.

**Vertices are classes, not names.**  Two modules may each write ``Objects``, and
``Modules.Subobjects`` is not ``Modules``.  A vertex is identified by the module
that defines the class, the qualified class name and the refinement set; the
label is what a reader types, and :func:`declaration_rows` prints the owner
where two vertices would otherwise read alike.  A name is resolved in the module
that writes it -- a class or function or module-level value of that module, an
import of that module followed to the module that defines it, then the tree --
and a name that resolves to nothing is ``undefined``, an audit finding rather
than a vertex invented for it.  A function the tree defines is read through its
return, because ``FiniteSets()`` is ``Sets().Finite()`` written a second way.

Run ``python -m sage_extensions.testing.category_graph VIEW``, or
``just category-graph VIEW``.  The views are ``categories`` (the default),
``by-supercategory``, ``foreign``, ``shape``, ``cells``, ``audit``, ``json`` and
``svg``.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SOURCE = Path("src") / "sage_extensions"
RESPONSIBLE_FOR_DECLARATIONS = SOURCE / "categories"
DECLARING_METHODS = ("super_categories", "extra_super_categories")
METHOD_CONTAINERS = frozenset(
    {"ParentMethods", "ElementMethods", "MorphismMethods", "SubcategoryMethods"}
)
r"""The class bodies whose methods are not categories.

A category's behaviour lives in nested ``ParentMethods``/``ElementMethods``
containers, whose nested classes are method containers again; a category nested
in a category is a subcategory or an axiom.  Walking a class body stops at these
names, so a class written inside one is not read as a category.
"""

AXIOM_BASE = "CategoryWithAxiom"
r"""The base a class derives from to be an axiom: ``CategoryWithAxiom`` and its variants."""

STATED = ""
r"""The tag of a declaration the source states in full: it names a vertex."""

COMPUTED = "computed"
r"""The tag of a declaration written as a local expression, so no edge is stated."""

UNDEFINED = "undefined"
r"""The tag of a declaration naming a name nothing in the tree defines."""

AMBIGUOUS = "ambiguous"
r"""The tag of a declaration naming a class the tree defines in several modules."""


@dataclass(frozen=True, order=True)
class Category:
    r"""One vertex of the declared graph.

    ``owner`` is the repository-relative path of the module that defines the
    class, ``sage`` for a category Sage defines, and ``unresolved`` for a name
    the tree defines nowhere.  ``name`` is the qualified class name within that
    module.  ``refinements`` is the refinement set adjoined to it, sorted: the
    categories an object of it also belongs to, which the declaration states by
    a chain of nullary steps.
    """

    owner: str
    name: str
    refinements: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        r"""The name a reader types: the class, then each refinement in turn."""
        return "".join((self.name, *(f".{refinement}" for refinement in self.refinements)))

    @property
    def stated(self) -> bool:
        r"""Whether the tree defines this vertex, rather than Sage or nothing."""
        return self.owner not in ("sage", "unresolved")

    def with_refinement(self, refinement: str) -> Category:
        r"""This vertex with one more refinement: the node the refinement adjoins."""
        return Category(self.owner, self.name, tuple(sorted({*self.refinements, refinement})))

    def without_refinement(self, refinement: str) -> Category:
        r"""This vertex with one refinement fewer: the node it declares."""
        return Category(
            self.owner, self.name,
            tuple(name for name in self.refinements if name != refinement),
        )


@dataclass(frozen=True, order=True)
class Declaration:
    r"""One expression a category class returns as a supercategory.

    ``declared`` is the vertex the expression names, and ``None`` when the
    expression names no category statically; ``unresolved`` then says why
    (:data:`COMPUTED`, :data:`UNDEFINED` or :data:`AMBIGUOUS`).  ``stated`` is
    the expression as written, which is what a reader checks the edge against.
    ``constructions`` are the steps after the head that take a parameter, so the
    declaration is that construction applied to the head with the parameters
    ``stated`` shows.  ``conditional`` says the return is one of several: the
    class declares the edge on a condition the source states.
    """

    declaring: Category
    declared: Category | None
    stated: str
    site: str
    method: str
    unresolved: str = STATED
    constructions: tuple[str, ...] = ()
    conditional: bool = False


@dataclass(frozen=True)
class _Class:
    r"""A class body of the tree: where it is, what it derives from, how it nests."""

    owner: str
    qualname: str
    lineno: int
    bases: tuple[str, ...]
    nested: tuple[str, ...]


@dataclass(frozen=True)
class _Function:
    r"""A module-level function, read for the category it returns.

    The returns and the names the body binds are all the reader keeps of it: a
    declaration names the function and the reader follows it to the category, so
    the body itself is not retained.  A tree of 250000 lines holds a hundred
    thousand nodes per file, and keeping them alive to answer one question about
    a return makes every garbage collection walk all of it.
    """

    returns: tuple[ast.expr, ...]
    local: frozenset[str]


@dataclass(frozen=True)
class _Site:
    r"""One ``super_categories`` or ``extra_super_categories`` return in a class body."""

    qualname: str
    method: str
    elements: tuple[ast.expr, ...]
    local: frozenset[str]
    conditional: bool


@dataclass(frozen=True)
class _Module:
    r"""What one module body binds, and the declarations its classes write.

    The parsed tree is not kept: the classes, the functions' returns, the
    module-level values, the imports and the declaration expressions are the
    whole of what a later resolution can reach, and dropping the rest is what
    keeps the read proportionate to the source rather than to its syntax.
    """

    owner: str
    classes: dict[str, _Class]
    functions: dict[str, _Function]
    values: dict[str, ast.expr]
    imports: dict[str, tuple[str, str]]
    modules: dict[str, str]
    declarations: tuple[_Site, ...]


def _parse(path: Path, owner: str) -> _Module:
    r"""The syntax tree ``path`` holds, and the names its module body binds.

    A category is named in four ways: a class the module defines, a function
    returning one (``FiniteSets()`` is ``Sets().Finite()``), a module-level
    assignment of one (``OwnedAbelianGroups = AbelianGroups``), and an import.
    All four are read here, from the module body only, because that is where a
    name a class body resolves has to be bound.

    A package that publishes its names lazily binds them through the table its
    ``__getattr__`` reads -- ``_EXPORTS = {"FiniteSets": ("...set_categories",
    "FiniteSets")}`` -- which states the same binding an import states, so the
    table is read as one.  Without it a declaration written through such a
    package would read as naming nothing.
    """
    tree = ast.parse(path.read_text(), filename=str(path))
    classes: dict[str, _Class] = {}
    functions: dict[str, _Function] = {}
    values: dict[str, ast.expr] = {}
    imports: dict[str, tuple[str, str]] = {}
    modules: dict[str, str] = {}
    declarations: list[_Site] = []
    for node in tree.body:
        match node:
            case ast.ImportFrom(module=module, names=names, level=0) if module is not None:
                for alias in names:
                    imports[alias.asname or alias.name] = (module, alias.name)
            case ast.Import(names=names):
                for alias in names:
                    modules[alias.asname or alias.name.split(".")[0]] = (
                        alias.name if alias.asname else alias.name.split(".")[0]
                    )
            case ast.ClassDef():
                _collect(node, owner, "", classes, declarations)
            case ast.FunctionDef():
                functions[node.name] = _Function(_returns(node), _local_names(node))
            case ast.Assign(targets=[ast.Name(id=name)], value=ast.Dict() as value):
                bindings = _reexports(value)
                if bindings is None:
                    values[name] = value
                else:
                    imports.update(bindings)
            case ast.Assign(targets=[ast.Name(id=name)], value=value):
                values[name] = value
            case ast.AnnAssign(target=ast.Name(id=name), value=value) if value is not None:
                values[name] = value
    return _Module(owner, classes, functions, values, imports, modules, tuple(declarations))


def _reexports(table: ast.Dict) -> dict[str, tuple[str, str]] | None:
    r"""The bindings a lazy export table states, or ``None`` when it is not one.

    ``{"FiniteSets": ("sage_extensions...set_categories", "FiniteSets")}`` maps a
    public name to the module and name it is resolved from, which is exactly what
    an import of that module binds.  Every value has to be such a pair: a dict
    that holds anything else is data, and the reader leaves it alone.
    """
    bindings: dict[str, tuple[str, str]] = {}
    for key, value in zip(table.keys, table.values):
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
            return None
        match value:
            case ast.Tuple(elts=[ast.Constant(value=str() as module),
                                 ast.Constant(value=str() as name)]):
                bindings[key.value] = (module, name)
            case _:
                return None
    return bindings or None


def _collect(
    node: ast.ClassDef,
    owner: str,
    prefix: str,
    classes: dict[str, _Class],
    declarations: list[_Site],
) -> None:
    r"""Record ``node``, every category nested in it, and every declaration it writes.

    A nested ``ParentMethods``/``ElementMethods``/``MorphismMethods`` container
    is where behaviour lives, so the walk stops there: a class inside one is part
    of a method, never a category.
    """
    qualname = f"{prefix}{node.name}"
    nested = tuple(
        child.name for child in node.body
        if isinstance(child, ast.ClassDef) and child.name not in METHOD_CONTAINERS
    )
    classes[qualname] = _Class(owner, qualname, node.lineno, _base_names(node), nested)
    for child in node.body:
        if isinstance(child, ast.ClassDef) and child.name not in METHOD_CONTAINERS:
            _collect(child, owner, f"{qualname}.", classes, declarations)
        elif isinstance(child, ast.FunctionDef) and child.name in DECLARING_METHODS:
            local = _local_names(child)
            for returned, conditional in _method_returns(child):
                declarations.append(
                    _Site(qualname, child.name, _elements(returned), local, conditional)
                )


def _base_names(node: ast.ClassDef) -> tuple[str, ...]:
    r"""The names a class derives from, as written: ``Category``, ``OwnedCategory``."""
    names = []
    for base in node.bases:
        root = _root_name(base)
        if root is not None:
            names.append(root)
    return tuple(names)


def _root_name(node: ast.expr) -> str | None:
    r"""The bare name an expression is built on, or ``None`` for a literal."""
    while True:
        match node:
            case ast.Name(id=name):
                return name
            case ast.Call(func=inner) | ast.Attribute(value=inner) | ast.Subscript(value=inner):
                node = inner
            case _:
                return None


def _returns(function: ast.FunctionDef) -> tuple[ast.expr, ...]:
    r"""Every expression ``function`` returns, in the order the source writes them."""
    return tuple(
        node.value for node in ast.walk(function)
        if isinstance(node, ast.Return) and node.value is not None
    )


def _method_returns(method: ast.FunctionDef) -> tuple[tuple[ast.expr, bool], ...]:
    r"""Each expression ``method`` returns, and whether it is one of several.

    A method with more than one return declares its edge on a condition the
    source states, which the reader keeps rather than resolving away.
    """
    returns = _returns(method)
    return tuple((value, len(returns) > 1) for value in returns)


def _local_names(method: ast.FunctionDef) -> frozenset[str]:
    r"""The names ``method`` binds: parameters, assignment targets, nested definitions.

    A declaration written as one of these is computed, so the class states no
    edge; the reader records it and lists it under ``audit``.
    """
    bound = {argument.arg for argument in ast.walk(method) if isinstance(argument, ast.arg)}
    bound.update(
        target.id for node in ast.walk(method) if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
    )
    bound.update(
        node.target.id for node in ast.walk(method) if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
    )
    bound.update(
        node.name for node in ast.walk(method)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    return frozenset(bound)


def _chain(expr: ast.expr) -> tuple[ast.expr, tuple[tuple[str, bool], ...]]:
    r"""An expression's head, and the steps applied to it with whether each takes a parameter.

    ``Modules(self.base_ring()).FinitelyPresented().Torsion()`` gives the head
    ``Modules`` and the steps ``(("FinitelyPresented", False), ("Torsion",
    False))``; the head's own parameter is recorded as written instead of being
    evaluated, because the vertex does not depend on the ring.
    """
    steps: list[tuple[str, bool]] = []
    node = expr
    while True:
        match node:
            case ast.Call(func=inner, args=args, keywords=keywords):
                if isinstance(inner, ast.Attribute):
                    steps.append((inner.attr, bool(args or keywords)))
                    node = inner.value
                    continue
                node = inner
            case ast.Attribute(value=inner, attr=attr):
                steps.append((attr, False))
                node = inner
            case ast.Subscript(value=inner):
                node = inner
            case _:
                return node, tuple(reversed(steps))


@dataclass(frozen=True)
class _Stated:
    r"""What one declaration expression names: a vertex, or why it names none."""

    category: Category | None
    unresolved: str
    constructions: tuple[str, ...]
    stated: str


def read(repository: Path) -> DeclaredGraph:
    r"""The category graph ``repository`` declares, read from its source.

    Every module under ``src/sage_extensions`` is parsed for the names it binds,
    because a declaration may reach a category through a re-export; the
    declarations themselves are read only from ``categories/``, which is where
    the tree places them.

    The vertices are the classes that declare and the categories they name.  A
    category whose supercategories are Sage's own -- a class with no
    ``super_categories`` of its own, placed by the join -- declares nothing the
    source states, and the graph does not invent a vertex for it.
    """
    repository = Path(repository)
    declarations: list[Declaration] = []
    parsed: dict[str, _Module] = {}
    for path in sorted((repository / SOURCE).rglob("*.py")):
        owner = path.relative_to(repository).as_posix()
        parsed[owner] = _parse(path, owner)
    packages = {_dotted(owner): owner for owner in parsed}
    parsed = _modules_apart(parsed, packages)
    index = _class_index(parsed)
    for owner, module in parsed.items():
        if not Path(owner).is_relative_to(RESPONSIBLE_FOR_DECLARATIONS):
            continue
        declarations.extend(_declarations_of(module, parsed, packages, index))
    return DeclaredGraph(*_categorised(tuple(declarations)))


def _dotted(owner: str) -> str:
    r"""The module name of a repository-relative path: ``a/b/c.py`` is ``a.b.c``."""
    parts = owner.removesuffix(".py").split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts[1:])


def _modules_apart(
    parsed: dict[str, _Module], packages: dict[str, str]
) -> dict[str, _Module]:
    r"""Separate the module aliases from the member imports.

    ``from sage_extensions.categories import sets as owned_sets`` binds a module
    and reads in the declaration as ``owned_sets.FiniteSets()``, while
    ``from ...sets import FiniteSets`` binds a name.  Only the tree's own modules
    tell them apart, so the distinction is drawn once here, after every module
    is known, rather than guessed from the import's spelling.
    """
    apart = {}
    for owner, module in parsed.items():
        modules = dict(module.modules)
        imports = dict(module.imports)
        for name, (from_module, original) in module.imports.items():
            dotted = f"{from_module}.{original}"
            if dotted in packages:
                modules[name] = dotted
                del imports[name]
        apart[owner] = _Module(
            owner, module.classes, module.functions, module.values, imports, modules,
            module.declarations,
        )
    return apart


def _class_index(parsed: dict[str, _Module]) -> dict[str, tuple[str, ...]]:
    r"""Each class name the tree defines at module level, and the modules that define it.

    The index is what makes an ambiguous name visible: a declaration naming a
    class two modules define resolves to no vertex until its own module's
    imports say which one it means.
    """
    index: dict[str, set[str]] = {}
    for owner, module in parsed.items():
        for qualname in module.classes:
            if "." not in qualname:
                index.setdefault(qualname, set()).add(owner)
    return {name: tuple(sorted(owners)) for name, owners in index.items()}


def _declarations_of(
    module: _Module,
    parsed: dict[str, _Module],
    packages: dict[str, str],
    index: dict[str, tuple[str, ...]],
) -> list[Declaration]:
    r"""Every declaration the classes of ``module`` write down."""
    found: list[Declaration] = []
    for site in module.declarations:
        declaring = _class_vertex(module, site.qualname)
        for element in site.elements:
            stated = _stated(
                element, module, parsed, packages, index, site.local,
                frozenset({(module.owner, site.qualname)}),
            )
            found.append(
                Declaration(
                    declaring=declaring,
                    declared=stated.category,
                    stated=stated.stated,
                    site=f"{module.owner}:{element.lineno}",
                    method=site.method,
                    unresolved=stated.unresolved,
                    constructions=stated.constructions,
                    conditional=site.conditional,
                )
            )
    return found


def _elements(returned: ast.expr) -> tuple[ast.expr, ...]:
    r"""The declaration expressions a return carries.

    A list or tuple carries one declaration per element -- a starred element is
    a computed one, kept so ``audit`` can report it -- and any other expression
    carries one declaration of its own, which :func:`_stated` refuses to name
    when the source does not.
    """
    if isinstance(returned, (ast.List, ast.Tuple)):
        return tuple(returned.elts)
    return (returned,)


def _class_vertex(module: _Module, qualname: str) -> Category:
    r"""The vertex a class path names: the class, and the axioms it is written under.

    A class nested in an axiom is an object of that axiom, and an axiom class is
    the vertex its base already names with one more refinement: ``Lattices.Even``
    is the vertex ``Lattices`` refined by ``Even``, which is the node Sage's join
    builds and the one an axiom reduction walks down from.
    """
    parts = qualname.split(".")
    for depth in range(1, len(parts) + 1):
        declared = module.classes.get(".".join(parts[:depth]))
        if declared is not None and any(
            base.startswith(AXIOM_BASE) for base in declared.bases
        ):
            return Category(
                module.owner, ".".join(parts[:depth - 1]), tuple(sorted(parts[depth - 1:]))
            )
    return Category(module.owner, qualname)


def _stated(
    element: ast.expr,
    module: _Module,
    parsed: dict[str, _Module],
    packages: dict[str, str],
    index: dict[str, tuple[str, ...]],
    local: frozenset[str],
    seen: frozenset[tuple[str, str]],
) -> _Stated:
    r"""The vertex one declaration expression names, or why it names none."""
    if isinstance(element, ast.Starred):
        return _Stated(None, COMPUTED, (), ast.unparse(element))
    written = ast.unparse(element)
    head, steps = _chain(element)
    if not isinstance(head, ast.Name) or head.id in local or head.id == "self":
        return _Stated(None, COMPUTED, (), written)
    if head.id in module.modules:
        return _member(
            module.modules[head.id], steps, written, parsed, packages, index,
            seen | {(module.owner, head.id)},
        )
    named = _name(module, head.id, parsed, packages, index, seen)
    if named.category is None:
        return _Stated(None, named.unresolved, (), written)
    refined = _refined(named.category, steps, parsed)
    return _Stated(refined.category, STATED, named.constructions + refined.constructions, written)


def _member(
    dotted: str,
    steps: tuple[tuple[str, bool], ...],
    written: str,
    parsed: dict[str, _Module],
    packages: dict[str, str],
    index: dict[str, tuple[str, ...]],
    seen: frozenset[tuple[str, str]],
) -> _Stated:
    r"""A declaration written through a module: ``owned_sets.FiniteSets()``.

    The first step names the member.  A module this reader did not parse is
    Sage's, so the member is a Sage category; a module of the tree's is read the
    same way any other name is.
    """
    if not steps:
        return _Stated(None, COMPUTED, (), written)
    owner = packages.get(dotted)
    if owner is None:
        return _Stated(Category("sage", steps[0][0]), STATED, (), written)
    named = _name(parsed[owner], steps[0][0], parsed, packages, index, seen)
    if named.category is None:
        return _Stated(None, named.unresolved, (), written)
    refined = _refined(named.category, steps[1:], parsed)
    return _Stated(refined.category, STATED, named.constructions + refined.constructions, written)


def _name(
    module: _Module,
    name: str,
    parsed: dict[str, _Module],
    packages: dict[str, str],
    index: dict[str, tuple[str, ...]],
    seen: frozenset[tuple[str, str]],
) -> _Stated:
    r"""The category ``name`` denotes in ``module``: a class, a function's result, a value, an import.

    A function the tree defines is read through its one return, which is where
    ``FiniteSets()`` is ``Sets().Finite()``; a module-level assignment is read
    through its value, which is where ``OwnedAbelianGroups`` is ``AbelianGroups``.
    The reader follows both because the declaration names the category all the
    same, and a reader that stopped at the class would report an edge missing
    where the source writes it in a second spelling.

    A name nothing binds is undefined, and a name the tree defines in several
    modules and this one does not import is ambiguous: both are findings, and
    neither is a vertex invented for it.
    """
    if (module.owner, name) in seen:
        return _Stated(None, COMPUTED, (), name)
    declared = module.classes.get(name)
    if declared is not None:
        return _Stated(_class_vertex(module, declared.qualname), STATED, (), name)
    function = module.functions.get(name)
    if function is not None:
        return _returned(
            module, name, function, parsed, packages, index, seen | {(module.owner, name)}
        )
    value = module.values.get(name)
    if value is not None:
        return _stated(
            value, module, parsed, packages, index, frozenset(),
            seen | {(module.owner, name)},
        )
    imported = module.imports.get(name)
    if imported is not None:
        from_module, original = imported
        if from_module.split(".")[0] == "sage":
            return _Stated(Category("sage", original), STATED, (), name)
        owner = packages.get(from_module)
        if owner is None:
            return _Stated(None, COMPUTED, (), name)
        return _name(parsed[owner], original, parsed, packages, index, seen | {owner})
    owners = index.get(name, ())
    match owners:
        case (only,):
            return _Stated(Category(only, name), STATED, (), name)
        case ():
            return _Stated(None, UNDEFINED, (), name)
        case _:
            return _Stated(None, AMBIGUOUS, (), name)


def _returned(
    module: _Module,
    name: str,
    function: _Function,
    parsed: dict[str, _Module],
    packages: dict[str, str],
    index: dict[str, tuple[str, ...]],
    seen: frozenset[tuple[str, str]],
) -> _Stated:
    r"""The category a function returns.

    One return is followed; a function returning a category from several
    branches states no single edge, so the reader records it as computed.
    """
    if len(function.returns) != 1:
        return _Stated(None, COMPUTED, (), name)
    return _stated(function.returns[0], module, parsed, packages, index, function.local, seen)


def _refined(
    vertex: Category,
    steps: tuple[tuple[str, bool], ...],
    parsed: dict[str, _Module],
) -> _Stated:
    r"""Walk the steps after a category's head: a refinement, a nested class, or a construction.

    A step that takes no parameter refines the vertex: ``FinitelyGenerated`` and
    ``Even`` name categories an object of the head also belongs to.  A name the
    tree presents as a class nested in the head is that class.  A step that takes
    a parameter is a construction applied to the head -- ``Subobjects(X)``,
    ``SliceOver(X)`` -- recorded as such, because the tree presents no category
    class for the result and the reader will not guess where it lands.
    """
    constructions: list[str] = []
    for step, parameterised in steps:
        nested = _nested(parsed, vertex, step)
        if nested is not None:
            vertex = nested
            continue
        if parameterised:
            constructions.append(step)
            continue
        vertex = vertex.with_refinement(step)
    return _Stated(vertex, STATED, tuple(constructions), "")


def _nested(
    parsed: dict[str, _Module], vertex: Category, step: str
) -> Category | None:
    r"""The class ``step`` names inside ``vertex``, when the tree presents one."""
    module = parsed.get(vertex.owner)
    if module is None:
        return None
    qualname = f"{vertex.name}.{step}"
    if qualname not in module.classes:
        return None
    return _class_vertex(module, qualname)


def _categorised(
    declarations: tuple[Declaration, ...]
) -> tuple[tuple[Declaration, ...], tuple[Category, ...]]:
    r"""The declarations, and every vertex they name or refine.

    Each refined vertex declares every vertex with one refinement fewer, so the
    vertex set is closed under dropping refinements: the walk down from
    ``Lattices.FinitelyGenerated.Nondegenerate.Even`` passes through every
    combination of the three, which is what makes two orders of the same
    refinements one vertex and one path.
    """
    vertices: set[Category] = set()
    for declaration in declarations:
        vertices.add(declaration.declaring)
        if declaration.declared is not None:
            vertices.add(declaration.declared)
    pending = list(vertices)
    while pending:
        vertex = pending.pop()
        for refinement in vertex.refinements:
            fewer = vertex.without_refinement(refinement)
            if fewer not in vertices:
                vertices.add(fewer)
                pending.append(fewer)
    return declarations, tuple(sorted(vertices))


@dataclass(frozen=True)
class DeclaredGraph:
    r"""What the tree declares: the declarations, and the vertices they name.

    ``declarations`` carries each expression as written, in source order, so a
    reader checks an edge against the line it came from.  Everything else is
    derived from them: the stated edge set, the refinements that adjoin a vertex
    to the one it declares, breadth, depth, the shortcut declarations, and the
    cycle space.
    """

    declarations: tuple[Declaration, ...]
    categories: tuple[Category, ...]

    def stated_edges(self) -> tuple[tuple[Category, Category], ...]:
        r"""The edges the source writes down: one per declaration that names a category.

        Repeated declarations of one edge are one edge here; the declarations
        themselves stay in :attr:`declarations`, so the sites are not lost.
        """
        return tuple(sorted({
            (declaration.declaring, declaration.declared)
            for declaration in self.declarations
            if declaration.declared is not None and declaration.declared != declaration.declaring
        }))

    def reduction_edges(self) -> tuple[tuple[Category, Category], ...]:
        r"""The edges a refinement adds: each refined vertex declares one refinement fewer."""
        return tuple(sorted({
            (vertex, vertex.without_refinement(refinement))
            for vertex in self.categories
            for refinement in vertex.refinements
        }))

    def edges(self) -> tuple[tuple[Category, Category], ...]:
        r"""Every edge of the complex: the stated ones, and the refinement reductions."""
        return tuple(sorted({*self.stated_edges(), *self.reduction_edges()}))

    def labelled(self, label: str) -> tuple[Category, ...]:
        r"""The vertices that print as ``label``.

        A label is what a reader types; a vertex is a class of one module.  Two
        vertices sharing a label are returned side by side rather than merged, so
        an assertion about one of them sees both.
        """
        return tuple(vertex for vertex in self.categories if vertex.label == label)

    def declares(self, label: str) -> frozenset[str]:
        r"""The labels the declarations of this category name.

        A declaration that names no category statically -- a local expression --
        contributes nothing here: :meth:`computed` reports those, because the
        difference between "declares nothing" and "declares something the
        reader will not guess" is the whole point of reading the source.
        """
        return frozenset(
            declaration.declared.label
            for declaration in self.declarations
            if declaration.declaring.label == label and declaration.declared is not None
            and declaration.declared != declaration.declaring
        )

    def supercategories_of(self, label: str) -> frozenset[str]:
        r"""The labels one step below this category: what it declares, and what it refines.

        Both are steps of the same complex.  A declaration states where an
        object goes when the added structure is forgotten; a refinement states
        the vertex an object of the refined category is also an object of, which
        is the node that drops it.
        """
        return frozenset(
            declared.label
            for declaring, declared in self.edges()
            if declaring.label == label
        )

    def computed(self) -> frozenset[str]:
        r"""The categories whose declaration is a local expression, so no edge is stated."""
        return frozenset(
            declaration.declaring.label
            for declaration in self.declarations
            if declaration.unresolved == COMPUTED
        )

    def claimants(self, declared: Category) -> tuple[Declaration, ...]:
        r"""The declarations that name ``declared``, in source order."""
        return tuple(
            declaration for declaration in self.declarations
            if declaration.declared == declared
        )

    def breadth(self) -> dict[Category, int]:
        r"""How many distinct categories declare each vertex directly.

        Breadth counts statements a contributor made, not the refinements Sage's
        join adds: a reduction is the node a refinement adjoins, not a claim
        about where an object belongs.
        """
        counts: dict[Category, int] = {vertex: 0 for vertex in self.categories}
        for declaring, declared in self.stated_edges():
            counts[declared] = counts.get(declared, 0) + 1
            counts.setdefault(declaring, counts.get(declaring, 0))
        return counts

    def roots(self) -> tuple[Category, ...]:
        r"""The vertices that declare nothing: where a path of forgetful functors ends."""
        declaring = {edge[0] for edge in self.edges()}
        return tuple(vertex for vertex in self.categories if vertex not in declaring)

    def depths(self) -> dict[Category, int]:
        r"""Each vertex's fewest steps to a category that declares nothing.

        A short path from a leaf to the root is the diagnostic: structure is
        being restated at the leaf instead of inherited from the level that
        carries it.
        """
        inward: dict[Category, list[Category]] = {vertex: [] for vertex in self.categories}
        for declaring, declared in self.edges():
            inward[declared].append(declaring)
        depth = {root: 0 for root in self.roots()}
        frontier = list(depth)
        while frontier:
            following = []
            for vertex in frontier:
                for claimant in inward[vertex]:
                    if claimant not in depth:
                        depth[claimant] = depth[vertex] + 1
                        following.append(claimant)
            frontier = following
        return {vertex: depth.get(vertex, -1) for vertex in self.categories}

    def shortcuts(self) -> tuple[tuple[Category, Category, tuple[Category, ...]], ...]:
        r"""The declarations that state a path the graph already provides.

        A declaration ``C -> D`` is a shortcut when ``D`` is reachable from ``C``
        without it: two composites of forgetful functors the graph asserts are
        equal, which is an edge carrying no reachability of its own.
        """
        outward: dict[Category, set[Category]] = {}
        for declaring, declared in self.edges():
            outward.setdefault(declaring, set()).add(declared)
        return tuple(
            (declaring, declared, path)
            for declaring, declared in self.stated_edges()
            for path in (_through(outward, declaring, declared),)
            if path
        )

    def numbered(self) -> tuple[dict[Category, int], dict[int, Category]]:
        r"""Each vertex's number in Sage's graph, and each number's vertex.

        Sage's cycle routines hand their graph to a compiled implementation that
        takes integers, so the drawing and the homology number the vertices and
        the report prints the names back.
        """
        numbers = {vertex: index for index, vertex in enumerate(self.categories)}
        return numbers, {index: vertex for vertex, index in numbers.items()}

    def complex(self):
        r"""Sage's graph of the complex: a vertex per category, an edge per declaration."""
        from sage.all import Graph

        numbers = self.numbered()[0]
        graph = Graph(loops=False, multiedges=False)
        graph.add_vertices(sorted(numbers.values()))
        graph.add_edges((numbers[declaring], numbers[declared]) for declaring, declared in self.edges())
        return graph

    def cycle_rank(self) -> int:
        r"""The rank of the cycle space: ``E - V + C`` of the declared complex.

        The complex has a 0-cell per category and a 1-cell per declaration and no
        2-cell, so its first homology is the whole cycle space and its
        fundamental group is free of this rank.
        """
        graph = self.complex()
        return graph.size() - graph.order() + graph.connected_components_number()

    def generators(self) -> tuple[tuple[Category, ...], ...]:
        r"""A minimum cycle basis: each generator a short closed path.

        Sage's routine, not a spanning forest of this module's: the graph that
        Sage itself traverses to join and linearize the preamble's categories is
        the same object, and a cycle basis computed any other way answers a
        different question about it.
        """
        vertices = self.numbered()[1]
        return tuple(
            tuple(vertices[number] for number in cycle)
            for cycle in self.complex().minimum_cycle_basis()
        )

    def blocks(self) -> tuple[tuple[Category, ...], ...]:
        r"""The 2-connected blocks, largest first: the coherence a change joins."""
        vertices = self.numbered()[1]
        return tuple(sorted(
            (
                tuple(sorted(vertices[number] for number in block))
                for block in self.complex().biconnected_components()
            ),
            key=lambda block: (-len(block), block),
        ))


def _through(
    outward: dict[Category, set[Category]], source: Category, target: Category
) -> tuple[Category, ...]:
    r"""A shortest path from ``source`` to ``target`` other than the declaration stating it.

    Leaving ``source`` by any other edge and never stepping onto ``target``
    before arriving is what is left once the declaration itself is removed: the
    second route, when one exists.
    """
    parents: dict[Category, Category] = {}
    frontier = [source]
    seen = {source}
    while frontier:
        following = []
        for vertex in frontier:
            for neighbour in sorted(outward.get(vertex, ())):
                if vertex == source and neighbour == target:
                    continue
                if neighbour == target:
                    path = [target, vertex]
                    while path[-1] != source:
                        path.append(parents[path[-1]])
                    return tuple(reversed(path))
                if neighbour not in seen:
                    seen.add(neighbour)
                    parents[neighbour] = vertex
                    following.append(neighbour)
        frontier = following
    return ()


def _shown(categories) -> dict[Category, str]:
    r"""What each vertex prints as: its label, and its owner when labels repeat.

    Two modules may each write ``Objects``, and the reader keeps them apart as
    vertices; the printed form does too, because a report that silently merged
    them would read as one category with two declarations.
    """
    shares: dict[str, int] = {}
    for vertex in categories:
        shares[vertex.label] = shares.get(vertex.label, 0) + 1
    return {
        vertex: (
            vertex.label if shares[vertex.label] == 1
            else f"{vertex.label} ({vertex.owner})"
        )
        for vertex in categories
    }


def _rendered(rows: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    r"""Two columns, the second aligned: the statement, and where it is written."""
    if not rows:
        return ()
    width = max(len(left) for left, _ in rows)
    return tuple(f"{left.ljust(width)}  {right}" if right else left for left, right in rows)


def declaration_rows(graph: DeclaredGraph) -> tuple[str, ...]:
    r"""Every category and what it declares: the default view.

    One line per declaration expression, with the expression as written and the
    site it came from, so a reader compares the edge against its source rather
    than against a summary of it.
    """
    shown = _shown(graph.categories)
    rows = []
    for declaration in graph.declarations:
        if declaration.declared is None:
            target = f"({declaration.unresolved})"
        else:
            target = shown[declaration.declared]
            if declaration.constructions:
                target = f"{target} via {'.'.join(declaration.constructions)}"
        right = "  ".join(part for part in (
            declaration.stated,
            "(conditional)" if declaration.conditional else "",
            f"[{declaration.method} {declaration.site}]",
        ) if part)
        rows.append((f"{shown[declaration.declaring]} -> {target}", right))
    return _rendered(tuple(rows))


def supercategory_rows(graph: DeclaredGraph) -> tuple[str, ...]:
    r"""Each supercategory, and who claims it: the audit surface for placement.

    A large group under one heading is one mathematical claim made many times
    over, and reading the members together is how a member that does not belong
    becomes visible.
    """
    shown = _shown(graph.categories)
    groups = []
    for declared in graph.categories:
        claimants = tuple(
            declaration for declaration in graph.claimants(declared)
            if declaration.declaring != declared
        )
        if claimants:
            groups.append((-len(claimants), shown[declared], claimants))
    lines: list[str] = []
    for negative, label, claimants in sorted(groups, key=lambda group: (group[0], group[1])):
        lines.append(f"{label}  <- {-negative} claimants")
        lines.extend(
            f"    {shown[declaration.declaring]}  {declaration.stated}  [{declaration.site}]"
            for declaration in claimants
        )
    return tuple(lines)


def foreign_rows(graph: DeclaredGraph) -> tuple[str, ...]:
    r"""Owned categories declaring a Sage category.

    The tree presents its own categories; a declaration that lands in Sage's is
    a placement the tree does not own, and the reader lists each one so it can
    be read rather than counted.
    """
    shown = _shown(graph.categories)
    return _rendered(tuple(
        (f"{shown[declaration.declaring]} -> {shown[declaration.declared]}",
         f"{declaration.stated}  [{declaration.site}]")
        for declaration in graph.declarations
        if declaration.declared is not None and declaration.declared.owner == "sage"
    ))


def shape_rows(graph: DeclaredGraph) -> tuple[str, ...]:
    r"""Breadth, depth, and the declarations that are shortcuts.

    Breadth at a node is how many categories declare it directly, which counts
    unfactored edges.  Depth is the fewest steps from a leaf to a category that
    declares nothing, and a short path is the diagnostic that structure is being
    restated at the leaf.  A shortcut is a declaration whose target the graph
    already reaches without it.
    """
    stated = graph.stated_edges()
    reductions = graph.reduction_edges()
    shown = _shown(graph.categories)
    lines = [
        f"vertices {len(graph.categories)}  declarations {len(graph.declarations)}"
        f"  stated edges {len(stated)}  refinement reductions {len(reductions)}"
        f"  components {graph.complex().connected_components_number()}"
        f"  rank H1 {graph.cycle_rank()}",
        "",
        "breadth (declarations received, most first):",
    ]
    lines.extend(
        f"  {count:>4}  {label}"
        for count, label in sorted(
            ((count, shown[vertex]) for vertex, count in graph.breadth().items() if count),
            key=lambda row: (-row[0], row[1]),
        )
    )
    lines.append("")
    lines.append("depth (steps to a category that declares nothing, deepest first):")
    lines.extend(
        f"  {depth:>4}  {label}"
        for depth, label in sorted(
            ((depth, shown[vertex]) for vertex, depth in graph.depths().items()),
            key=lambda row: (-row[0], row[1]),
        )
    )
    shortcuts = graph.shortcuts()
    lines.append("")
    lines.append(f"shortcut declarations: {len(shortcuts)}")
    for declaring, declared, path in shortcuts:
        route = " -> ".join(shown[vertex] for vertex in path)
        lines.append(f"  {shown[declaring]} -> {shown[declared]}   also as {route}")
    return tuple(lines)


def cell_rows(graph: DeclaredGraph) -> tuple[str, ...]:
    r"""The homology, and the cycles that owe a 2-cell.

    The complex has a 0-cell per category, a 1-cell per declaration and no
    higher cells, so every generator of its first homology is a pair of
    composites of forgetful functors the graph asserts are equal, and the 2-cell
    that would fill it is that assertion's proof.  A minimum cycle basis prints
    each generator as a short closed path, and the 2-connected blocks are the
    groups a change joins.
    """
    complex_ = graph.complex()
    generators = sorted(graph.generators(), key=lambda cycle: (len(cycle), cycle))
    shown = _shown(graph.categories)
    lines = [
        f"vertices {complex_.order()}  edges {complex_.size()}"
        f"  components {complex_.connected_components_number()}"
        f"  rank H1 {graph.cycle_rank()}  generators {len(generators)}",
        "",
        "generators (a minimum cycle basis, shortest first):",
    ]
    for index, cycle in enumerate(generators, start=1):
        route = " -> ".join(shown[vertex] for vertex in cycle)
        lines.append(f"  {index:>3}: {route} -> {shown[cycle[0]]}")
    blocks = graph.blocks()
    lines.append("")
    lines.append("blocks (2-connected, largest first):")
    for block in blocks:
        joined = "  ".join(sorted(shown[vertex] for vertex in block))
        lines.append(f"  {len(block):>4}  {joined}")
    return tuple(lines)


def audit_rows(graph: DeclaredGraph) -> tuple[str, ...]:
    r"""What needs no reading of the objects: the declarations that state no edge.

    A name declared as a supercategory and defined nowhere, a declaration
    computed from a local expression so the edge is not stated at all, a
    category declaring its own name, and a declaration whose target the graph
    already reaches: each is a finding the reader cannot settle by reading the
    line, which is why it is listed rather than resolved.
    """
    shown = _shown(graph.categories)
    lines: list[str] = []
    for title, tag in (
        ("declared and not defined at the site", (UNDEFINED, AMBIGUOUS)),
        ("computed, so the edge is not written down", (COMPUTED,)),
    ):
        found = tuple(
            declaration for declaration in graph.declarations
            if declaration.unresolved in tag
        )
        lines.append(f"{title}: {len(found)}")
        lines.extend(
            f"  {shown[declaration.declaring]}  {declaration.stated}"
            f"  [{declaration.site}]"
            for declaration in found
        )
        lines.append("")
    selves = tuple(
        declaration for declaration in graph.declarations
        if declaration.declared == declaration.declaring
    )
    lines.append(f"declaring their own name: {len(selves)}")
    lines.extend(
        f"  {shown[declaration.declaring]}  {declaration.stated}  [{declaration.site}]"
        for declaration in selves
    )
    shortcuts = graph.shortcuts()
    lines.append("")
    lines.append(f"shortcut declarations: {len(shortcuts)}")
    for declaring, declared, path in shortcuts:
        route = " -> ".join(shown[vertex] for vertex in path)
        lines.append(f"  {shown[declaring]} -> {shown[declared]}   also as {route}")
    lines.append("")
    lines.append(
        f"vertices {len(graph.categories)}  declarations {len(graph.declarations)}"
        f"  rank H1 {graph.cycle_rank()}"
    )
    return tuple(lines)


def report(graph: DeclaredGraph) -> dict:
    r"""The graph as data: what a query reads, answered from the same vertices the views print."""
    shown = _shown(graph.categories)
    breadth = graph.breadth()
    depth = graph.depths()
    return {
        "vertices": [
            {
                "label": vertex.label,
                "owner": vertex.owner,
                "name": vertex.name,
                "refinements": list(vertex.refinements),
                "breadth": breadth.get(vertex, 0),
                "depth": depth.get(vertex, -1),
            }
            for vertex in graph.categories
        ],
        "declarations": [
            {
                "declaring": shown[declaration.declaring],
                "declared": (
                    None if declaration.declared is None else shown[declaration.declared]
                ),
                "stated": declaration.stated,
                "method": declaration.method,
                "site": declaration.site,
                "unresolved": declaration.unresolved,
                "constructions": list(declaration.constructions),
                "conditional": declaration.conditional,
            }
            for declaration in graph.declarations
        ],
        "cycle_rank": graph.cycle_rank(),
        "generators": [
            " -> ".join(shown[vertex] for vertex in cycle) for cycle in graph.generators()
        ],
        "blocks": [sorted(shown[vertex] for vertex in block) for block in graph.blocks()],
        "shortcuts": [
            [shown[declaring], shown[declared], [shown[vertex] for vertex in path]]
            for declaring, declared, path in graph.shortcuts()
        ],
    }


def rendered_json(graph: DeclaredGraph) -> str:
    r"""The graph as one JSON object, for a query rather than for reading."""
    return json.dumps(report(graph), indent=2, sort_keys=True)


DOT_DIRECTORY = Path(".tmp") / "category-graph"
r"""Where ``svg`` writes the drawing: an artifact of a run, not a document of the tree."""


def written_svg(graph: DeclaredGraph, directory: Path = DOT_DIRECTORY) -> tuple[str, ...]:
    r"""Draw the literal graph, and report the two files it wrote.

    Every vertex and every edge, refinement reductions dashed so the ones the
    tree states are the solid lines: the drawing is what a reader looks at when
    a block grew, and the dot file is what another tool redraws it from.
    """
    shown = _shown(graph.categories)
    identifiers = {vertex: f"n{index}" for index, vertex in enumerate(graph.categories)}
    stated = set(graph.stated_edges())
    lines = ["digraph declared {", "  rankdir=RL;", "  node [shape=box, fontsize=10];"]
    lines.extend(
        f'  {identifiers[vertex]} [label="{shown[vertex]}"];' for vertex in graph.categories
    )
    for declaring, declared in graph.edges():
        style = "" if (declaring, declared) in stated else " [style=dashed]"
        lines.append(f"  {identifiers[declaring]} -> {identifiers[declared]}{style};")
    lines.append("}")
    directory.mkdir(parents=True, exist_ok=True)
    dot = directory / "declared-graph.dot"
    dot.write_text("\n".join(lines) + "\n")
    drawing = directory / "declared-graph.svg"
    subprocess.run(
        ("dot", "-Tsvg", str(dot), "-o", str(drawing)),
        check=True, capture_output=True, text=True,
    )
    return (f"wrote {dot}", f"wrote {drawing}")


VIEWS = {
    "categories": declaration_rows,
    "by-supercategory": supercategory_rows,
    "foreign": foreign_rows,
    "shape": shape_rows,
    "cells": cell_rows,
    "audit": audit_rows,
}
r"""The declaration views, each a function of the graph alone."""


def render(graph: DeclaredGraph, view: str, *, repository: Path = Path(".")) -> str:
    r"""The text ``view`` prints for ``graph``: the views, ``json``'s object, or the drawing."""
    if view == "json":
        return rendered_json(graph)
    if view == "svg":
        return "\n".join(written_svg(graph, repository / DOT_DIRECTORY))
    return "\n".join(VIEWS[view](graph))


def main(argv: tuple[str, ...] = ()) -> int:
    r"""Print one view of the declared graph of the checkout this runs in."""
    parser = argparse.ArgumentParser(
        prog="python -m sage_extensions.testing.category_graph",
        description="The category graph the source declares, and the views of it.",
    )
    parser.add_argument(
        "view", nargs="?", default="categories", choices=tuple(VIEWS) + ("json", "svg"),
    )
    parser.add_argument("--repository", default=".", help="the checkout to read")
    arguments = parser.parse_args(list(argv))
    print(render(read(Path(arguments.repository)), arguments.view, repository=Path(arguments.repository)))
    return 0


if __name__ == "__main__":
    sys.exit(main(tuple(sys.argv[1:])))
