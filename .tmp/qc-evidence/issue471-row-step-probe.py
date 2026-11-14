r"""#471 probe: the kernel-plane-rows driver's isotropy check by the plane's
induced Gram tensor, and its two reports on the gate lattice U + U(2) + <-2>.

Parts:
  1. the induced Gram tensor of a plane the row returns, and of a rank-two
     primitive subobject that is not totally isotropic;
  2. the driver's check on both, timed warm;
  3. the driver's run_row and check_row_count on the gate lattice's two kernel
     rows, and main's exit status there;
  4. main's four exit statuses, each driven by a stub row so that the
     contract-violation report and the undecided report are shown apart.

The Coble rows are not run here: they are the CI job's.
"""

import importlib.util
import time

from sage_extensions.all import *  # noqa: F401,F403

PROBE_START = time.monotonic()


def log(message=""):
    print(f"[{time.monotonic() - PROBE_START:7.1f}s] {message}", flush=True)


def load_driver():
    spec = importlib.util.spec_from_file_location(
        "coble_kernel_plane_rows",
        "/repos/sage-extensions/tests/coble_kernel_plane_rows.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def header(name, value):
    log(f"--- {name} ---")
    log(str(value))


def old_spelling(lattice, subobject):
    r"""The check the reviewer read on main: pairings of chosen generators."""
    labels = tuple(subobject.module_generating_set())
    zero = lattice.base_ring().zero()
    for left in labels:
        for right in labels:
            if lattice.b(
                subobject.inclusion()(subobject.module_generator(left)),
                subobject.inclusion()(subobject.module_generator(right)),
            ) != zero:
                return False
    return True


driver = load_driver()
log(f"driver loaded: {driver.__doc__.splitlines()[0]}")
log(f"statuses: {[status.name + ' = ' + status.value for status in driver.RowStatus]}")
assert len(driver.RowStatus) == 3, list(driver.RowStatus)

gate = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
header("gate lattice", f"{gate} of rank {gate.module_rank()}")
stable = gate.stable_orthogonal_group()
stable_plus = stable.intersection(gate.O_plus())
ambient = tuple(stable.supergroup().isotropic_orbit_representatives(2))
log(f"ambient O(L)-plane classes: {len(ambient)}")
plane = ambient[0]

log("=== 1. the plane's induced Gram tensor ===")
induced = plane.gram_tensor()
pulled = gate.gram_tensor().pullback(plane.inclusion())
log(f"plane {plane} of rank {plane.module_rank()}, primitive {plane.is_primitive()}")
log(f"plane.gram_tensor() = {induced} in {induced.parent()}")
log(f"zero tensor of that framing: {induced.parent().zero()}")
log(f"induced == zero: {induced == induced.parent().zero()}")
log(f"ambient form pulled back along the inclusion: {pulled}")
log(f"the two spellings agree: {pulled == induced}")

labels = tuple(plane.module_generating_set())
log(f"its retained generators {labels} and their pairings:")
for left in labels:
    for right in labels:
        value = gate.b(
            plane.inclusion()(plane.module_generator(left)),
            plane.inclusion()(plane.module_generator(right)),
        )
        log(f"  b({left}, {right}) = {value}")

bad = gate.subobject_on((gate.basis_vector(0), gate.basis_vector(1)))
bad_induced = bad.gram_tensor()
log("")
log(f"a rank-two primitive subobject {bad} of rank {bad.module_rank()}, primitive {bad.is_primitive()}")
log(f"its induced Gram tensor = {bad_induced} in {bad_induced.parent()}")
log(f"induced == zero: {bad_induced == bad_induced.parent().zero()}")
log(f"the pairing of the two basis vectors it spans: {gate.b(gate.basis_vector(0), gate.basis_vector(1))}")

thin = gate.subobject_on((gate.basis_vector(0),))
log("")
log(f"a rank-one subobject {thin} of rank {thin.module_rank()}")

log("=== 2. the driver's check on these three ===")
log(f"plane: {driver._plane_contract_violation(plane)!r}")
log(f"non-isotropic rank-two: {driver._plane_contract_violation(bad)!r}")
log(f"rank one: {driver._plane_contract_violation(thin)!r}")
log(f"the old pairing loop on the plane: {old_spelling(gate, plane)}")
log(f"the old pairing loop on the non-isotropic rank-two: {old_spelling(gate, bad)}")

log("=== 2b. cost of the check, warm, per representative ===")
for name, check in (
    ("induced Gram tensor", lambda: driver._plane_contract_violation(plane)),
    ("old pairing loop", lambda: old_spelling(gate, plane)),
):
    start = time.monotonic()
    for _ in range(200):
        check()
    each = (time.monotonic() - start) / 200
    log(f"{name}: {each * 1000:.3f} ms each, x189720 = {each * 189720:.1f} s")

log("=== 3. the driver's rows on the gate lattice ===")
driver._coble_lattice = lambda: gate
log("main on the gate lattice (the driver's own rows, double cosets included):")
status = driver.main(["--cap", "900", "--budget", "0"])
log(f"main exit status: {status}")

log("=== 4. the two reports, and all four exit statuses ===")


class StubGroup:
    r"""The gate lattice's kernel group, with only its row replaced.

    Every other operation (``supergroup``, ``finite_character_quotient`` and
    the rest of the double-coset count) is the real group's, so the
    count-mismatch status below is decided against the real double cosets.
    """

    def __init__(self, real, planes, delay=0.0):
        self._real = real
        self._planes = tuple(planes)
        self._delay = delay

    def isotropic_orbit_representatives(self, rank):
        if self._delay:
            time.sleep(self._delay)
        return list(self._planes)

    def intersection(self, other):
        return self

    def __getattr__(self, name):
        return getattr(self._real, name)

    def __str__(self):
        return "a stub row"


class StubLattice:
    def __init__(self, lattice, group):
        self._lattice = lattice
        self._group = group

    def __getattr__(self, name):
        return getattr(self._lattice, name)

    def __str__(self):
        return f"the gate lattice {self._lattice} behind a stub row"

    def stable_orthogonal_group(self):
        return self._group


row = tuple(stable.isotropic_orbit_representatives(2))
log(f"the Otilde row on the gate lattice: {len(row)} planes")

count, contract_status = driver.run_row(StubGroup(stable, (bad, bad)), "Otilde", 60)
log(f"run_row of a row holding {bad}: ({count}, {contract_status!r})")
count, undecided_status = driver.run_row(StubGroup(stable, (), delay=30), "Otilde", 2)
log(f"run_row of a row that does not return inside 2 s: ({count}, {undecided_status!r})")
assert contract_status is not undecided_status, (contract_status, undecided_status)
log(f"the two reports differ: {contract_status!r} != {undecided_status!r}")

for expected, name, group in (
    (2, "a row holding a non-isotropic representative", StubGroup(stable, (bad, bad))),
    (1, "a row that does not return inside the cap", StubGroup(stable, (), delay=30)),
    (3, "a row whose count is not its double cosets", StubGroup(stable, (row[0], row[0], row[0]))),
):
    driver._coble_lattice = lambda group=group: StubLattice(gate, group)
    start = time.monotonic()
    got = driver.main(["--cap", "3", "--budget", "0"])
    log(f"main on {name}: exit status {got} in {time.monotonic() - start:.1f} s (expected {expected})")
    assert got == expected, (name, got, expected)

log("PROBE 471 DONE")
