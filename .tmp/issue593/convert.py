"""Rewrite every address-only cache decorator under src/ to the form #592 settled on."""

import ast, pathlib, sys

DECORATORS = {"cached_function", "weak_cached_function", "cached_method", "cached_method_no_args"}

PRINCIPLE = {
    "cached_function": "@_address_registry",
    "weak_cached_function": "@_weak_address_registry",
    "cached_method": "@_instance_address_registry",
}

DATUM = {
    # key normalizes an argument to a canonical owned object: name that object.
    "src/sage_extensions/categories/algebras/algebras.py:905":
        "@cached_function(key=lambda base_ring: _owned_ring(base_ring))",
    "src/sage_extensions/categories/abstract_categories/cat.py:190":
        "@cached_method(key=lambda self, domain, codomain: (self.object(domain), self.object(codomain)))",
    "src/sage_extensions/categories/rings/ring_foundation.py:4096":
        "@cached_method(key=lambda self, base_ring: _own_ring(base_ring))",
    # key names the datum the answer is built on; the engine is part of the answer.
    "src/sage_extensions/categories/schemes/relative_spec.py:178":
        "@cached_function(key=lambda datum, *, _engine=None, construction_data=None: (datum, _engine))",
    "src/sage_extensions/categories/schemes/relative_spec.py:193":
        "@cached_function(key=lambda datum, *, _engine=None, construction_data=None: (datum, _engine))",
}


def names_an_object(n):
    if isinstance(n, ast.Call):
        return not (isinstance(n.func, ast.Name) and n.func.id == "id")
    if isinstance(n, ast.Name):
        return n.id not in {"None", "True", "False"}
    if isinstance(n, (ast.Attribute, ast.Subscript, ast.Tuple, ast.List)):
        return True
    return False


def address_only_sites():
    sites = []
    for path in sorted(pathlib.Path("src").rglob("*.py")):
        text = path.read_text()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Name) or dec.func.id not in DECORATORS:
                    continue
                key = {k.arg: k.value for k in dec.keywords}.get("key")
                if key is None:
                    continue
                args = key.body if isinstance(key, ast.Lambda) else key
                elts = args.elts if isinstance(args, (ast.Tuple, ast.List)) else [args]
                if any(names_an_object(e) for e in elts):
                    continue
                sites.append((str(path), dec, text))
    return sites


def performed(text, names):
    r"""Return ``text`` with an import of ``names`` from ``sage_extensions.utilities``.

    An existing import of that module is extended; otherwise the import is placed
    after the last top-level ``from sage_extensions...`` import.
    """
    lines = text.splitlines()
    line_of = None
    have = set()
    for number, line in enumerate(lines):
        if line.startswith("from sage_extensions.utilities import "):
            line_of = number
            have = {name.strip() for name in line.split("import ", 1)[1].split(",")}
            break
    wanted = sorted(set(names) - have)
    if not wanted:
        return text
    if line_of is not None:
        merged = sorted(have | set(names))
        lines[line_of] = "from sage_extensions.utilities import " + ", ".join(merged)
    else:
        tree = ast.parse(text)
        anchor = 0
        for statement in tree.body:
            if isinstance(statement, (ast.Import, ast.ImportFrom)):
                anchor = statement.end_lineno
        inserted = "from sage_extensions.utilities import " + ", ".join(wanted)
        above = lines[anchor - 1] if anchor else ""
        lines[anchor:anchor] = [inserted] if above.startswith(("from ", "import ")) else ["", inserted]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def dropped_imports(text, path):
    r"""Return ``text`` with the cache-decorator names it no longer uses removed from its import."""
    for name in ("weak_cached_function", "cached_function", "cached_method_no_args", "cached_method"):
        if f"{name}(" in text or f"@{name}\n" in text:
            continue
        lines = text.splitlines()
        for number, line in enumerate(lines):
            if not line.startswith("from sage.misc.cachefunc import "):
                continue
            names = [item.strip() for item in line.split("import ", 1)[1].split(",")]
            if name not in names or len(names) == 1:
                continue
            kept = [item for item in names if item != name]
            lines[number] = "from sage.misc.cachefunc import " + ", ".join(kept)
            text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
        text = text.replace(f"{name}((", "(") if False else text
    return text


def main():
    sites = address_only_sites()
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        for path, dec, _ in sites:
            tag = f"{path}:{dec.lineno}"
            print(f"{tag:95s} {DATUM.get(tag, PRINCIPLE[dec.func.id])}")
        return

    by_file = {}
    for path, dec, text in sites:
        by_file.setdefault(path, []).append((dec, text))

    for path, items in by_file.items():
        text = items[0][1]
        lines = text.splitlines()
        replacements = []
        new_names = []
        for dec, _ in items:
            tag = f"{path}:{dec.lineno}"
            new = DATUM.get(tag, PRINCIPLE[dec.func.id])
            replacements.append((dec.lineno - 1, dec.end_lineno, " " * (dec.col_offset - 1) + new))
            if new.startswith("@"):
                new_names.append(new.split()[0].lstrip("@"))
        for start, end, new in sorted(replacements, reverse=True):
            lines[start:end] = [new]
        updated = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
        updated = performed(updated, [name for name in new_names if name.startswith("_")])
        updated = dropped_imports(updated, path)
        pathlib.Path(path).write_text(updated)
    print(f"converted {len(sites)} sites in {len(by_file)} files")


main()
