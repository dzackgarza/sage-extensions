"""Does the user's own .sage corpus rely on the implicit generator declaration?

For every .sage file under the research repository: preparse it with the
session rule (the session vocabulary is `sage_extensions.all`'s names, as the
base code reads them) and with the upstream rule alone.  A file where the two
differ is one where the session rule suppresses a declaration the upstream rule
would have made.
"""
import glob
import collections

import sage_extensions.all  # noqa: F401
from sageparse.preparser import preparse_file

from sage_extensions import language_runtime as lr

lr._SESSION_MODULES = {"sage_extensions.all", "dzack_research.preamble.all"}
taken = lr._session_names
print("vocabulary:", len(taken("sage_extensions.all")), flush=True)

paths = sorted(glob.glob('/research/**/*.sage', recursive=True))
print("files:", len(paths), flush=True)

differ = []
for path in paths:
    try:
        source = open(path, encoding='utf-8').read()
    except UnicodeDecodeError:
        continue
    lr._session_names = taken
    try:
        with_rule = preparse_file(source)
    except Exception:
        continue
    lr._session_names = lambda module: frozenset()
    try:
        upstream = preparse_file(source)
    except Exception:
        continue
    if with_rule != upstream:
        left = with_rule.splitlines()
        right = upstream.splitlines()
        pairs = [
            (a, b) for a, b in zip(left, right) if a != b
        ]
        differ.append((path, pairs[:3]))

lr._session_names = taken
print("files where the session rule suppresses an upstream declaration:", len(differ), flush=True)
for path, pairs in differ:
    print(path)
    for a, b in pairs:
        print("  session rule:", a.strip()[:140])
        print("  upstream    :", b.strip()[:140])
