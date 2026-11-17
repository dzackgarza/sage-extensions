r"""Probe: of the cache decorators under `src/`, how many key on addresses alone.

A decorator whose `key=` names an argument object -- the object itself, an
attribute of it, or a tuple containing it -- holds that object for as long as the
entry lives, so the address in the key cannot be reused while the entry is there.
One whose key is only `id(...)` calls and constants names no object: its answer
belongs to an address, and it is wrong the moment the object at that address is
another one.
"""

import ast
import pathlib

DECORATORS = {"cached_function", "weak_cached_function", "cached_method", "cached_method_no_args"}


def names_an_object(node):
    """Whether the key expression holds an object rather than only an address."""
    if isinstance(node, ast.Call):
        # id(x) is an address, not the object; every other call is treated as
        # naming whatever it returns, which the entry then holds.
        return not (isinstance(node.func, ast.Name) and node.func.id == "id")
    if isinstance(node, ast.Name):
        return node.id not in {"None", "True", "False"}
    if isinstance(node, (ast.Attribute, ast.Subscript, ast.Tuple, ast.List)):
        return True
    return False


def main():
    total = 0
    address_only = []
    holds = []
    for path in sorted(pathlib.Path("src").rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                if not isinstance(decorator.func, ast.Name):
                    continue
                if decorator.func.id not in DECORATORS:
                    continue
                total += 1
                keywords = {keyword.arg: keyword.value for keyword in decorator.keywords}
                keyed = keywords.get("key")
                if keyed is None:
                    continue
                arguments = keyed.body if isinstance(keyed, ast.Lambda) else keyed
                elements = (
                    arguments.elts
                    if isinstance(arguments, (ast.Tuple, ast.List))
                    else [arguments]
                )
                if any(names_an_object(element) for element in elements):
                    holds.append(f"{path}:{node.lineno}")
                else:
                    address_only.append(f"{path}:{node.lineno}")
    print(f"[probe] cache decorators under src/: {total}")
    print(f"[probe] of them with a key of addresses and constants only: {len(address_only)}")
    print(f"[probe] of them with a key that names an object: {len(holds)}")
    for site in address_only:
        print(f"  [address-only] {site}")


main()
