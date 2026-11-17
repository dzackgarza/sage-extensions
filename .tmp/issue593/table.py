"""The 100 sites of the base tree, their keys, and the form each took."""

import ast, pathlib

BASE = pathlib.Path(".scratch/593base2")
D = {"cached_function", "weak_cached_function", "cached_method", "cached_method_no_args"}

DATUM = {
    "src/sage_extensions/categories/algebras/algebras.py:906": "datum key: the owned ring",
    "src/sage_extensions/categories/abstract_categories/cat.py:196": "datum key: the functor's objects",
    "src/sage_extensions/categories/rings/ring_foundation.py:4097": "datum key: the owned ring",
    "src/sage_extensions/categories/schemes/relative_spec.py:179": "datum key: the datum and its engine",
    "src/sage_extensions/categories/schemes/relative_spec.py:194": "datum key: the datum and its engine",
}

def names_an_object(n):
    if isinstance(n, ast.Call):
        return not (isinstance(n.func, ast.Name) and n.func.id == "id")
    if isinstance(n, ast.Name):
        return n.id not in {"None", "True", "False"}
    if isinstance(n, (ast.Attribute, ast.Subscript, ast.Tuple, ast.List)):
        return True
    return False

rows = []
for path in sorted(BASE.rglob("src/sage_extensions/**/*.py")):
    text = path.read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Name) or dec.func.id not in D:
                continue
            key = {k.arg: k.value for k in dec.keywords}.get("key")
            if key is None:
                continue
            args = key.body if isinstance(key, ast.Lambda) else key
            elts = args.elts if isinstance(args, (ast.Tuple, ast.List)) else [args]
            if any(names_an_object(e) for e in elts):
                continue
            addressed = [ast.unparse(a) for n in ast.walk(key)
                         if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "id" and len(n.args) == 1
                         for a in n.args]
            tag = f"{path.relative_to(BASE)}:{dec.lineno + 1}"
            rows.append((tag, node.name, dec.func.id, ", ".join(addressed),
                         DATUM.get(tag, ""), key))

PRINCIPLE = {"cached_function": "_address_registry", "weak_cached_function": "_weak_address_registry",
             "cached_method": "_instance_address_registry"}

print("| site | function | the addresses its key used | form |")
print("| --- | --- | --- | --- |")
for tag, name, kind, addressed, datum, _ in rows:
    form = datum.replace("datum key: ", "datum — ") if datum else "principle — `" + PRINCIPLE[kind] + "`"
    print(f"| `{tag}` | `{name}` | `{addressed}` | {form} |")
print(len(rows))
