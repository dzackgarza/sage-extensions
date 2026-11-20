r"""The line-cusp key partition of `Otilde(T_Co)` is one partition, in any process.

A line cusp is a `Gamma`-orbit of primitive isotropic lines and `Gamma = ker rho`
acts trivially on `A_L`, so the divided class of a primitive vector is constant on
the orbit: the partition of the cusps by class is determined by the lattice and
the subgroup, and two processes must answer the same partition.

They do not.  Under `PYTHONHASHSEED` 0 and 1 the same computation gives partitions
of 527 cusps whose multiplicities differ (largest buckets 9, 9, 8, 8, 7, ... in one
and 7, 5, 5, 5, 5, ... in the other), and one run in three raises inside the walk.
No lattice below `T_Co` shows it: `6JRS`, `U + U(2) + <-2>`, `U + U(2) + <-4>` and
`U + U + <-4>` answer the same partition under both seeds.
"""

from sage_extensions.all import *  # noqa: F401,F403

import json
import os
import subprocess
import sys

CHILD = """
import importlib.util
import json
import sys

sys.path.insert(0, "{tests}")

spec = importlib.util.spec_from_file_location(
    "rows", "{tests}/coble_gamma_co_2_incidence_rows.py"
)
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)
from sage_extensions.categories.orthogonal_quotients import _isotropic_line_image_key

lattice = rows._lattice_by_name("Tco")
subgroup = rows._row_subgroup(lattice, "Otilde")
quotient = subgroup.finite_character_quotient()
counts = {{}}
for cusp in subgroup.cusps(1):
    key = repr(sorted(_isotropic_line_image_key(quotient, cusp.representative())))
    counts[key] = counts.get(key, 0) + 1
print(json.dumps(sorted(counts.values(), reverse=True)))
"""


def _partition(hash_seed):
    r"""The partition of the line cusps' keys, computed in a child process."""
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = hash_seed
    source = CHILD.format(tests=os.path.join(os.getcwd(), "tests"))
    completed = subprocess.run(
        [sys.executable, "-c", source],
        capture_output=True,
        text=True,
        env=environment,
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    sizes = json.loads(completed.stdout)
    assert len(sizes) > 1, "a partition with one bucket cannot witness anything"
    return sizes


def test_the_line_cusp_key_partition_is_the_same_in_two_processes():
    first = _partition("0")
    second = _partition("1")
    assert first == second, (
        f"the line cusps' key partition depends on the process: {first[:12]} then "
        f"{second[:12]}"
    )
