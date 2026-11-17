import ast, pathlib, sys

DECORATORS = {"cached_function", "weak_cached_function", "cached_method", "cached_method_no_args"}

def names_an_object(node):
    if isinstance(node, ast.Call):
        return not (isinstance(node.func, ast.Name) and node.func.id == "id")
    if isinstance(node, ast.Name):
        return node.id not in {"None", "True", "False"}
    if isinstance(node, (ast.Attribute, ast.Subscript, ast.Tuple, ast.List)):
        return True
    return False

sites = []
for path in sorted(pathlib.Path("src").rglob("*.py")):
    text = path.read_text()
    lines = text.splitlines()
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
            sites.append((str(path), node, text, lines))

want = sys.argv[1:] if len(sys.argv) > 1 else None
for path, node, text, lines in sites:
    tag = "%s:%d" % (path, node.lineno)
    if want and not any(w in tag for w in want):
        continue
    print("=" * 100)
    print(tag, node.decorator_list and ast.get_source_segment(text, [d for d in node.decorator_list if isinstance(d, ast.Call) and getattr(d.func, 'id', '') in DECORATORS][-1]).replace("\n", " "))
    body = text.splitlines()[node.lineno - 1:node.end_lineno]
    for line in body[:26]:
        print("   ", line)
