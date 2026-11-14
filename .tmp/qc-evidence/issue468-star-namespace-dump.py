r"""Dump every session binding of ``sage_extensions.all`` for a base/repair diff (#468).

    /sage/.venv/bin/python -u .scratch/issue468-namespace-dump.py <output.tsv>

One line per non-dunder name: the name, the type of the bound object, and the
module and qualified name that object declares itself under.  Two trees' dumps
compare equal exactly when the session binds the same objects.

A ``LazyImport`` is recorded unresolved: ten of ``categories.functions``' lazy
names raise on first attribute access (#440, older than this repair), so the dump
must not force them.
"""

import pathlib
import sys

import sage_extensions.all as session

rows = []
unresolved = []
for name, obj in sorted(session.__dict__.items()):
    if name.startswith("__") and name.endswith("__"):
        continue
    kind = type(obj).__name__
    if kind == "LazyImport":
        unresolved.append(name)
        rows.append(f"{name}\t{kind}\t<not resolved: lazy>")
        continue
    module = getattr(obj, "__module__", type(obj).__module__)
    qualname = getattr(obj, "__qualname__", type(obj).__name__)
    rows.append(f"{name}\t{kind}\t{module}.{qualname}")
target = pathlib.Path(sys.argv[1])
target.write_text("\n".join(rows) + "\n")
print(f"{len(rows)} names -> {target}")
print(f"lazy and left unresolved: {len(unresolved)} {unresolved}")
