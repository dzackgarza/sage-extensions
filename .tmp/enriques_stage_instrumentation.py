"""
Minimal stage instrumentation separating the four conflated sub-stages in the
single `discriminant orthogonal group + discriminant morphisms` bundle.

Retains the same specimen (case_3 92897280;5/10/19, same G_h predicate,
same 6144 MiB guard) without repeating the full 2400s indistinguishable run.

Sub-stages (each prints BEFORE it starts):
  S1: generator-family realization for G_h — first `group.group_generators()` read
  S2: discriminant-group construction — `anti_invariant.discriminant_group()`
  S3: discriminant orthogonal group — `A_L.orthogonal_group()`
  S4: per-generator discriminant morphisms — `g.discriminant_morphism()` for g in G_h
  S5: finite-character image construction — `OrthogonalCharacterQuotient._gap_regular_model`
      and `finite_character_quotient().image_keys` on G_h

Each stage is timed separately and guarded by peakrss sampling; a cap on one
does not hide attribution of the others. This uses existing substantive
UltraMath reports/workers and exact current code (predicate_subgroups.py,
orthogonal_quotients.py, lattice_morphisms.py) to diagnose the call path,
distinguishing construction from realization and C-only stack uncertainty.
"""
import time, sys
START = time.time()
def stage(msg):
    print(f"[s {time.time()-START:.1f}s] {msg}", flush=True)

stage("imports")
from sage_extensions.categories.lattices import Lattices
from sage_extensions.all import ZZ
# ... actual staged probing to be filled from existing workers' transcripts
# Placeholder: this file documents the instrumentation plan, not a full rerun.
# Realization will reuse the retained G_h object from jmvzp7ijo's 209.7s construction
# and step through S1-S5 with separate peakrss samples.
