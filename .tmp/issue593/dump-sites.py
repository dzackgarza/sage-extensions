"""Dump every address-only cache decorator site with its function and key."""
import ast, pathlib

DECORATORS = {"cached_function", "weak_cached_function", "cached_method", "cached_method_no_args"}

def names_an_object(node):
    if isinstance(node, ast.Call):
        return not (isinstance(node.func, ast.Name) and node.func.id == "id")
    if isinstance(node, ast.Name):
        return node.id not in {"None", "True", "False"}
    if isinstance(node, (ast.Attribute, ast.Subscript, ast.Tuple, ast.List)):
        return True
    return False

rows = []
for path in sorted(pathlib.Path("src").rglob("*.py")):
    text = path.read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if not isinstance(decorator.func, ast.Name) or decorator.func.id not in DECORATORS:
                continue
            keywords = {k.arg: k.value for k in decorator.keywords}
            keyed = keywords.get("key")
            if keyed is None:
                continue
            arguments = keyed.body if isinstance(keyed, ast.Lambda) else keyed
            elements = arguments.elts if isinstance(arguments, (ast.Tuple, ast.List)) else [arguments]
            if any(names_an_object(e) for e in elements):
                continue
            rows.append((str(path), node.lineno, decorator.func.id, node.name,
                         ast.get_source_segment(text, decorator).replace("\n", " "),
                         ",".join(a.arg for a in node.args.args)))
print(len(rows))
for r in rows:
    print("%s:%d|%s|%s|%s|%s" % r)
