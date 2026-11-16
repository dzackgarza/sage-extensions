"""Probe: the kernel incidence rows on the smallest lattice whose kernel rows are not the ambient rows.

Runs the driver that the CI job runs, on ``U + U(2) + <-2>``, on a sampler thread that prints the
process RSS every five seconds, so the run's memory trace is recorded beside its rows.
"""
import os
import runpy
import sys
import threading
import time

START = time.monotonic()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def sample():
    while True:
        print(f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB", flush=True)
        time.sleep(5)


threading.Thread(target=sample, daemon=True).start()
sys.path.insert(0, "/repos/sage-extensions/tests")
sys.argv = [
    "coble_gamma_co_2_incidence_rows.py",
    "--rows", os.environ.get("PROBE_ROWS", "Otilde,Otilde+"),
    "--lattice", os.environ.get("PROBE_LATTICE", "U+U(2)+<-2>"),
    "--cap", os.environ.get("PROBE_CAP", "600"),
    "--budget", os.environ.get("PROBE_BUDGET", "900"),
]
print(f"[probe] argv {sys.argv[1:]}", flush=True)
runpy.run_path("/repos/sage-extensions/tests/coble_gamma_co_2_incidence_rows.py", run_name="__main__")
