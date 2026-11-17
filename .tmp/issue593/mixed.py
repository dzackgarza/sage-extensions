"""Search: cache keys that still name an object by its address.

A key that holds the object it addresses cannot have that address reused while
the entry lives.  "Holds" is read syntactically: the addressed expression occurs
in the key outside every call, so the key's value is the object itself.
"""

import ast, pathlib

D = {"cached_function", "weak_cached_function", "cached_method", "cached_method_no_args"}


def unparse(node):
    return ast.unparse(node)


def bare_forms(key):
    """Unparsed expressions of the key that are not inside any call."""
    forms = set()

    def walk(node):
        if isinstance(node, ast.Call):
            return
        forms.add(unparse(node))
        for child in ast.iter_child_nodes(node):
            walk(child)

    walk(key)
    return forms


rows = []
for path in sorted(pathlib.Path("src").rglob("*.py")):
    text = path.read_text()
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Name) or dec.func.id not in D:
                continue
            key = {k.arg: k.value for k in dec.keywords}.get("key")
            if key is None:
                continue
            addressed = [
                n.args[0]
                for n in ast.walk(key)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name)
                and n.func.id == "id"
                and len(n.args) == 1
            ]
            if not addressed:
                continue
            forms = bare_forms(key)
            held = all(unparse(a) in forms for a in addressed)
            rows.append((str(path), dec.lineno + 1, node.name, held, unparse(key)))

print(f"keys that mention an address: {len(rows)}")
print(f"  the key holds every object it addresses: {sum(1 for r in rows if r[3])}")
print(f"  it does not: {sum(1 for r in rows if not r[3])}")
print()
for path, line, name, held, key in rows:
    if not held:
        print(f"  {path}:{line} {name} :: {key}")
