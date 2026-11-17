import subprocess, sys
print("[smoke] module", __import__("sage_extensions").__file__, flush=True)
print(subprocess.run(("git","-C","/repos/sage-extensions","rev-parse","HEAD"), capture_output=True, text=True), flush=True)
from sage_extensions.timing import current_commit
print("[smoke] current_commit", current_commit(), flush=True)
