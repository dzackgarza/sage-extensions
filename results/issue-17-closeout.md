Standing state — provider `dzackgarza/sage-extensions`, `main` at `354231d8988fd399841af46924f51be4b851e6de`

**Accepted, each with the run that proves it**

- `51cf8e3` — discriminant morphisms on the real two-elementary form. The earlier fixture used the *negated* E8 Cartan matrix, which is unimodular, so the form had order 4 and every "all 1024 classes" claim was measured on 4 elements; the fixture is now −2·C (det 256, order 1024). Proof: `tests/lattices/test_discriminant_morphism_on_two_elementary_forms.sage`, **4 passed in 81.54 s** (job `jmw2fofuu`).
- `9e75ea5` — finite-set subset read (`power(Set((1, 2)))`), `FunctionSets` exported, session integer defers to an infinite cardinal power. Proof: `tests/sets/test_a_finite_literal_set_reads_as_a_subset.sage` 3 passed (job `jmw2g5nuo`); `tests/sets/test_function_sets_are_a_public_category.sage` 2 passed; `tests/sets/test_cardinals_and_ordinals.sage` new pin; provider `tests/sets` cleaned-worktree FAILED-id diff **43F/101P → 37F/110P** (6 fixed, 0 new, `.scratch/sets-failed-{baseline,after}.txt`); research's own four set files **4 failed/9 passed → 2 failed/11 passed** (jobs `jmw2fyzhl`, `jmw2g2t6l`, `.scratch/research-set-layer-*.log`).
- `ad436ca` — `FractionFieldQuotients` exported and its own default call repaired (`FractionFieldQuotients(ZZ)()` raised `TypeError`). Proof: `tests/modules/test_fraction_field_quotients_are_a_public_category.sage` 3 passed (job `jmw2gt8p2`); consumers `tests/forms/test_orbit_and_profile_radical_isometry.sage` + `test_polar_radical_criterion.sage` **18 passed in 176.57 s** (job `jmw2gu513`).
- `0dec903` — `FreeModules` and `Algebras` exported. Free-module placement was never broken (module, `f.image()`, `f.kernel()` all in `FreeModules(ZZ)` once nameable); `Algebras(ZZ).Associative().Unital().Commutative().de_rham_adjunction()` answers. Proof: `tests/modules/test_free_modules_are_a_public_category.sage` + `tests/algebras/test_commutative_algebras_are_reachable.sage`, **5 passed in 1.82 s** (job `jmw2hfgii`).
- `dc2c230` — `OwnedAbelianGroups`/`AbelianGroups`/`OwnedFiniteAbelianGroups` and `FinitelyPresentedTorsionModules` exported. `FinitelyPresentedTorsionModules(ZZ)` is callable and equals `Modules(ZZ).FinitelyPresented().Torsion()`, which supersedes the "no verified constructor" reading. Proof: `tests/groups/test_abelian_groups_and_torsion_modules_are_public.sage`, **3 passed in 40.03 s** (job `jmw2i1xaa`).

**Committed but unverified**

- `354231d` — `LatticeMorphismMethods.integral_restriction` builds its backward map from the inverse coordinate matrix's **rows** instead of its columns (`(F⁻¹)ᵀ` is the inverse only when `F` is symmetric, which is why `−id` and a root reflection pass and the Enriques stabilizer generator does not). Committed as a checkpoint, explicitly **not** a fix: no acceptance run completed. Three attempts (`jmw2gjxwy`, `jmw2h1gdp`, `jmw2h5o2e`) produced no output before being stopped — two starved by another session's CI job on the same image, the last cut by runtime maintenance. Evidence for the locus, not the fix: `.tmp/owner-reconciliation/port-case50-diagnosed4.log` and `-6.log` (construction stack `integral_isometry → integral_restriction:1447 → element_class`; coordinate determinant −1; form preserved; stored inverse not a left inverse; 384–496 q-defects of 1024).

**Blocked, and on what**

- All further rootfs work is blocked on the shared runtime's adoption of the Sage-owned GAP image at a zero-process boundary. This project's processes are stopped: session `shell_jobs` `running: 0`; no `/sage/.venv/bin/python` process; no process of this project on `sage-image/rootfs`; 11.8 GB available.
- `case50` acceptance is blocked on that resume: it needs the port's `test_boundaries.sage[case_50]` run against the adopted image. It is **not** passed and nothing here claims it is.
- No consumer pin was changed, no shared-runtime file was written. This connection exposes issue **reads only**, so this text is the comment that could not be posted from here.

**Exact command when the runtime resumes**

```
cd /workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
.scratch/launch_port_case50_inverse_fix.sh          # port case_50 against this checkout
tail -40 .tmp/owner-reconciliation/port-case50-inverse-fix3.log
```

and the provider-side pin:

```
.scratch/proot-run .scratch/one.sh tests/lattices/test_discriminant_morphism_on_two_elementary_forms.sage
```

**Recorded and open, not blocked** (details and raise sites in `TRAPS.md`): `Sets().Iso(A, B)` answers neither `order` nor `cardinality` while `Mor`/`End` do; `OwnedAbelianGroups().an_object()` (`C_2`) is in neither `AbelianGroups()` nor `FiniteAbelianGroups()`; `is_zero` on `Owned_NativeFreeAlgebraParent`; the cokernel "finitely presented only if its domain is finitely generated" assertion; `base must be a ring…` and `base must be a subring…` guards; join-key `KeyError`s; unhashable `OwnedJoinCategory.element_class`.
