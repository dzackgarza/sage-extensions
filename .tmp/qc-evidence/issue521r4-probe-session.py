"""The session's published names, and the dialect's two readings of a subscript (#521)."""

import sage.all_cmdline  # noqa: F401
import sage_extensions.all as session
from sage.repl import preparse
from sage_extensions import language_runtime as runtime

public = frozenset(name for name in vars(session) if not name.startswith("_"))
declared = getattr(session, "__all__", None)
print(f"public names in the module: {len(public)}")
print(f"__all__ declared: {declared is not None}")
print(f"__all__ is the public names: {declared is not None and frozenset(declared) == public}")
print(f"__all__ duplicates dropped: {declared is not None and len(declared) == len(set(declared))}")
print(f"the dialect's vocabulary: {len(getattr(runtime, '_SESSION_NAMES', ()))}")
print(f"vocabulary is the declaration: {frozenset(getattr(runtime, '_SESSION_NAMES', ())) == frozenset(declared or ())}")

STAR = "from sage_extensions.all import *\n"
SNIPPETS = {
    "session name in an index": "countable = Sets.\u0394[aleph0]\n",
    "session ring in an index": "generated = Modules[ZZ]\n",
    "unwritten name in an index": "declared = QQ[t]\n",
    "second unwritten name": "declared = ZZ[x, y]\n",
    "file-bound name in an index": "k = 2\ngenerated = Modules[k]\n",
}
for label, snippet in SNIPPETS.items():
    lowered = preparse.preparse(STAR + snippet)
    rewrote = "._first_ngens" in lowered
    print(f"{label}: declares generators={rewrote}")

star_scope = {}
exec(preparse.preparse(STAR), star_scope)
bound_by_the_star_import = frozenset(name for name in star_scope if not name.startswith("_"))
print(f"names the star import binds: {len(bound_by_the_star_import)}")
print(f"that is the public namespace: {bound_by_the_star_import == public}")

for label, snippet in SNIPPETS.items():
    scope = {}
    try:
        exec(preparse.preparse(STAR + snippet), scope)
    except TypeError as report:
        print(f"{label}: runs no further than {report}")
        continue
    names = sorted(name for name in scope if not name.startswith("_") and name not in public)
    print(f"{label}: bindings the file made {names}")

print(f"Integer is the owned element: {session.Integer('7') in session.ZZ}")
print(f"RealNumber is exact: {session.RealNumber('1/3') * 3 == 1}")
print(f"matrix multiplies: {(session.matrix([[1, 0], [0, 1]]) * session.matrix([[1, 2], [3, 4]]))[0, 1] == 2}")
