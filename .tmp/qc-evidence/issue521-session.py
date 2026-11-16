"""The session's namespace, its ring identities and the dialect's lowering (#521)."""

import time

t0 = time.time()
import sage.all_cmdline  # noqa: F401
t1 = time.time()
import sage_extensions.all as session
t2 = time.time()
print(f"PROBE import sage.all_cmdline {t1 - t0:.3f} s; sage_extensions.all {t2 - t1:.3f} s")

print("NAMES-BEGIN")
for name in sorted(n for n in vars(session) if not n.startswith("_")):
    print(name)
print("NAMES-END")

import sage_extensions.rings as rings  # noqa: E402

print("RINGS-BEGIN")
for name in (
    "ZZ", "QQ", "AA", "QQbar", "RR", "RDF", "CDF", "CC",
    "GF", "Zmod", "Zp", "Qp", "RealField", "ComplexField",
    "CyclotomicField", "QuadraticField",
):
    present = name in vars(session)
    same = present and getattr(rings, name, None) is getattr(session, name)
    print(
        f"{name:18s} session={present!s:5s} rings={hasattr(rings, name)!s:5s} "
        f"identical={same!s:5s} declared={name in rings.__all__!s:5s}"
    )
print(f"ring_constructor_surface in session: {'ring_constructor_surface' in vars(session)}")
print("RINGS-END")

from sage.repl import preparse  # noqa: E402

SAMPLE = (
    "from sage_extensions.all import *\n"
    "\n"
    "M = Modules[ZZ]\n"
    "R = ZZ[x]\n"
    "T = Modules[k]\n"
)
print("PREPARSE-BEGIN")
print(preparse.preparse_file(SAMPLE))
print("PREPARSE-END")
