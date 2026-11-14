import ast, pathlib

path = pathlib.Path("src/sage_extensions/all.py")
text = path.read_text()
lines = text.splitlines(keepends=True)
tree = ast.parse(text)

AREAS = (
    "sage_extensions.categories.abstract_categories",
    "sage_extensions.categories.algebras",
    "sage_extensions.categories.divisors",
    "sage_extensions.categories.forms",
    "sage_extensions.categories.functions",
    "sage_extensions.categories.group.profinite",
    "sage_extensions.categories.modules",
    "sage_extensions.categories.modules.framed",
    "sage_extensions.categories.modules.framed.finitely_generated",
    "sage_extensions.categories.modules.framed.formed",
    "sage_extensions.categories.modules.group_modules",
    "sage_extensions.categories.modules.pure",
    "sage_extensions.categories.modules.pure.finitely_generated",
    "sage_extensions.categories.schemes.toric",
    "sage_extensions.categories.sets",
    "sage_extensions.categories.sets.enumerated",
    "sage_extensions.groups",
    "sage_extensions.lexicon",
    "sage_extensions.rings",
    "sage_extensions.schemes",
    "sage_extensions.static_types",
    "sage_extensions.tensors",
)

def all_of(p):
    t = ast.parse(p.read_text())
    for node in t.body:
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "__all__" for x in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                return [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
    return []

root = pathlib.Path("src/sage_extensions")
declared = set()
for area in AREAS:
    names = all_of(root / pathlib.Path(*area.split(".")[1:]) / "__init__.py")
    assert names, area
    declared.update(names)

edits = []
for node in tree.body:
    if isinstance(node, ast.ImportFrom) and node.module:
        names = [(a.name, a.asname) for a in node.names]
        keep = [(n, a) for n, a in names if n not in declared]
        if len(keep) == len(names):
            continue
        if not keep:
            edits.append((node.lineno, node.end_lineno, None))
            continue
        body = "".join(f"    {n},\n" for n, _ in keep)
        edits.append((node.lineno, node.end_lineno, [f"from {node.module} import (  # noqa: F401\n{body})\n"]))
    elif (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
          and getattr(node.value.func, "id", "") == "_lazy_import"):
        call = node.value
        if len(call.args) < 2 or not isinstance(call.args[1], (ast.Tuple, ast.List)):
            continue
        module = call.args[0].value
        names = [e.value for e in call.args[1].elts if isinstance(e, ast.Constant)]
        keep = [n for n in names if n not in declared]
        if len(keep) == len(names):
            continue
        if not keep:
            edits.append((node.lineno, node.end_lineno, None))
            continue
        body = "".join(f'        "{n}",\n' for n in keep)
        edits.append((node.lineno, node.end_lineno, [f'_lazy_import(\n    "{module}",\n    (\n{body}    ),\n)\n']))

for start, end, replacement in sorted(edits, reverse=True):
    lines[start - 1:end] = [] if replacement is None else replacement

block = [
    "# The session publishes what each area package declares.  A package's\n",
    "# ``__all__`` is the one authority for its names (OWN-19; AGENTS, \"Names and\n",
    "# ownership\"), so this module names no member of those declarations: the\n",
    "# packages below are the session's areas and each contributes its whole\n",
    "# ``__all__``.  An area's constructor is a session name by construction, so a\n",
    "# second hand-written list cannot drift from the owner's (API-06, API-07).\n",
    "_AREA_PACKAGES = (\n",
] + [f'    "{a}",\n' for a in AREAS] + [
    ")\n",
    "for _area_package_name in _AREA_PACKAGES:\n",
    "    _area_package = _import_module(_area_package_name)\n",
    "    for _area_name in _area_package.__all__:\n",
    "        globals()[_area_name] = getattr(_area_package, _area_name)\n",
    "del _area_package_name, _area_package, _area_name\n",
]

anchor = None
for index, line in enumerate(lines):
    if line.startswith("from sage_extensions import language_runtime as _language_runtime"):
        anchor = index + 1
        break
assert anchor is not None
lines[anchor:anchor] = ["\n"] + block
path.write_text("".join(lines))
ast.parse(path.read_text())
print("statements touched:", len(edits), "lines now:", len(lines))
