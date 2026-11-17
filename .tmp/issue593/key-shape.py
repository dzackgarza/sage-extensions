import ast, pathlib
D = {"cached_function", "weak_cached_function", "cached_method", "cached_method_no_args"}
def names_an_object(n):
    if isinstance(n, ast.Call):
        return not (isinstance(n.func, ast.Name) and n.func.id == "id")
    if isinstance(n, ast.Name):
        return n.id not in {"None", "True", "False"}
    if isinstance(n, (ast.Attribute, ast.Subscript, ast.Tuple, ast.List)):
        return True
    return False

for path in sorted(pathlib.Path("src").rglob("*.py")):
    text = path.read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Name) or dec.func.id not in D:
                continue
            kw = {k.arg: k.value for k in dec.keywords}
            key = kw.get("key")
            if key is None:
                continue
            args = key.body if isinstance(key, ast.Lambda) else key
            elts = args.elts if isinstance(args, (ast.Tuple, ast.List)) else [args]
            if any(names_an_object(e) for e in elts):
                continue
            params = [a.arg for a in node.args.args]
            lam = [a.arg for a in key.args.args] if isinstance(key, ast.Lambda) else []
            mentioned = {n.id for e in elts for n in ast.walk(e) if isinstance(n, ast.Name)}
            calls = [ast.unparse(n.func) for e in elts for n in ast.walk(e) if isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name) and n.func.id == "id")]
            missing = [p for p in params if p not in mentioned]
            extra = [l for l in lam if l not in params]
            notes = []
            if missing: notes.append("key-drops:" + ",".join(missing))
            if extra: notes.append("lambda-args:" + ",".join(extra))
            if calls: notes.append("normalizes:" + "|".join(calls))
            if notes:
                print(f"{path}:{node.lineno} {node.name} [{node.args.args and params[0]}] {' '.join(notes)}")
