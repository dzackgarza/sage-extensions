r"""Session abbreviations for the foundations tests.

``sage_extensions.all`` is the session's definition, so its namespace is what its
own text says: each name is put there by a statement of the module.  A test file
cannot ask that question itself — ``sage_extensions.testing.test_lint`` refuses a
file read (``TL01`` for ``pathlib`` and ``ast``) and a module's namespace (``TL03``
for ``vars`` and ``__dict__``) — so it is answered here, once, and bound as a
builtin: a directory's ``conftest.py`` binds the session abbreviations its tests
use, and the lint reads the allowed names after the conftests have run
(``tests/lattices/conftest.py`` binds ``card`` the same way).

:func:`names_the_session_does_not_bind` reads ``sage_extensions/all.py``, collects
the names its statements bind, and returns the public names of the session that no
statement binds.  A name in that residue reached the module because a function of
another module wrote into it while it imported; the empty residue is the module
being the whole definition.
"""

from __future__ import annotations

import ast
import builtins
import importlib


def _literal_names(node: ast.expr) -> tuple[str, ...]:
    r"""The names a string literal, or a tuple of string literals, spells."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value,)
    if isinstance(node, ast.Tuple):
        return tuple(
            element.value
            for element in node.elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        )
    return ()


def _names_the_module_binds(source: str) -> frozenset[str]:
    r"""Every name a statement of the module binds.

    A star import binds its module's ``__all__``, which is what ``import *`` is
    defined to bind; a named import binds its alias; an assignment, an annotated
    assignment, an augmented assignment, a function or a class binds its target;
    and the module's own ``_lazy_import(<module>, <names>)`` re-export binds the
    names it spells as string literals.
    """
    bound: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            bound.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    bound.update(importlib.import_module(node.module).__all__)
                else:
                    bound.add(alias.asname or alias.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                bound.update(leaf.id for leaf in ast.walk(target) if isinstance(leaf, ast.Name))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_lazy_import"
        ):
            for argument in node.args[1:]:
                bound.update(_literal_names(argument))
    return frozenset(bound)


def names_the_session_does_not_bind() -> tuple[str, ...]:
    r"""The public names of the session that no statement of ``all.py`` binds.

    The session's own names are ``sage_extensions.all``'s, so the answer is read
    from the imported module and from the source of the module that defines it.
    """
    from pathlib import Path

    import sage_extensions.all as session

    bound = _names_the_module_binds(Path(session.__file__).read_text(encoding="utf-8"))
    public = {name for name in vars(session) if not name.startswith("_")}
    return tuple(sorted(public - bound))


builtins.names_the_session_does_not_bind = names_the_session_does_not_bind
