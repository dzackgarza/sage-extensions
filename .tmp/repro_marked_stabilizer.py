"""Minimal reproduction of the non-returning apex-stabilizer call (case_3 stage D).

Actual call path measured by before/after markers (jmw0d7uq2):
  subgroup_classes(G_h, lines) -> O().split_orbit(marked, subgroup)
  -> _marking_stabilizer_generators(category, marked)
  -> lattice_category()._marked_automorphism_generators(category, marked)
  (lattices.py:1862) -> sage_indefinite_port.indefinite.marked_lattices.
   automorphism_group_generators(ARROWS category, marked)
  -> INDUCTION.line_automorphism_generators(L, e1)  (isotropic_induction.py:306)

This probe exercises ONLY that innermost call on the published line
representatives of N = U + U(2) + E8(-2) (fixture unpolarized_enriques.json,
ids I_1_1 Z e1 and I_1_2 Z e3, gram from the same fixture), on the direct
block-gram N (byte-compatible), printing BEFORE each step.
"""
import time

START = time.monotonic()


def stage(label):
    print(f"[t={time.monotonic()-START:8.1f}s] {label}", flush=True)


stage("imports")
from tests.acceptance.consumer import element, lattice
from tests.fixtures.oracle_fixtures import load_e10_fundamental_domain  # sanity only
import json

FIXTURE = json.load(open("/work/tests/fixtures/unpolarized_enriques.json"))
GRAM = FIXTURE["lattice"]["gram"]
stage(f"fixture N gram: det {FIXTURE['lattice']['det']}, signature {FIXTURE['lattice']['signature']}")

N = lattice(GRAM)
stage(f"direct-gram N built: rank {N.rank()}, signature {N.signature_pair()}")

from sage_indefinite_port.indefinite.marked_lattices import automorphism_group_generators
from sage_indefinite_port.indefinite.marked_lattices import INDUCTION
from tests.acceptance.consumer import sublattice_category

for rep in FIXTURE["component_preserving_group"]["line_representatives"]:
    basis = rep["basis"]
    stage(f"line {rep['id']} ({rep['description']}): build marked sublattice")
    v = element(N, basis[0])
    marked = sublattice_category().object(N.subobject_on([v]).inclusion())
    stage(f"line {rep['id']}: DIRECT INDUCTION.line_automorphism_generators(N, v)")
    t0 = time.monotonic()
    gens = INDUCTION.line_automorphism_generators(N, v)
    stage(f"line {rep['id']}: INDUCTION returned {len(tuple(gens))} gens in {time.monotonic()-t0:.1f}s")
    category = sublattice_category()
    stage(f"line {rep['id']}: PORT automorphism_group_generators(category, marked)")
    t0 = time.monotonic()
    result = automorphism_group_generators(category, marked)
    stage(f"line {rep['id']}: port returned {len(tuple(result))} gens in {time.monotonic()-t0:.1f}s")

print("REPRO_OK", flush=True)
