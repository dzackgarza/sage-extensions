"""CPU time of the lowering, measured inside one process (#521)."""

import time

import sage.all_cmdline  # noqa: F401
import sage_extensions.all  # noqa: F401
from sage.repl import preparse

HEADER = "from sage_extensions.all import *\n"
BODY = "".join(
    f"M{i} = Modules[{name}]\n"
    for i, name in enumerate(["ZZ", "QQ", "Sym", "x", "y"] * 40)
)
SOURCE = HEADER + BODY

preparse.preparse_file(SOURCE)
times = []
for _ in range(5):
    start = time.process_time()
    preparse.preparse_file(SOURCE)
    times.append(time.process_time() - start)
print("cpu times: " + " ".join(f"{value:.4f}" for value in times))
print(f"min {min(times):.4f} s cpu for 200 assignments")
