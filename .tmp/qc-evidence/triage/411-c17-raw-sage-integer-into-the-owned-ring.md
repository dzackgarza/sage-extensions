C17: A raw Sage integer is refused at the owned integer ring

`TypeError: cannot convert 3 into Integer Ring: it is a raw Sage element of Integer Ring; construct it from a ring of this session`, raised while the mod-3 cyclotomic character of `Gal(F_5bar/F_5)` is evaluated: an engine integer produced inside the computation cannot be used as an exponent in the owned ring.

Failing tests on main `c8a3ced` (2026-11-14), one file per run in the published image:

- `tests/groups/test_profinite_character_mor_archive.sage::test_mod_three_cyclotomic_character_of_f5_has_kernel_of_index_two`
  `TypeError: cannot convert 3 into Integer Ring: it is a raw Sage element of Integer Ring; construct it from a ring of this session`
  at `src/sage_extensions/categories/rings/ring_foundation.py:6525: in _element_constructor_`

Defective call: src/sage_extensions/categories/rings/ring_foundation.py:6525 (the owned integer ring's element constructor).

Introduced by: not bisected: the constructor's refusal is in root commit c731175 (2026-10-26, Zack Garza); the line was blamed there.

Scope: the ingress of an engine integer into the owned integer ring, on a path the library itself computes; one test. The boundary is deliberate (`OWN-02`), so the repair is at the computation that produces the engine integer, not at the constructor.

Triage record: `results/issue411-triage.md` (C17), slice of #411.
