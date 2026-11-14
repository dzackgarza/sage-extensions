C22: Applying the identity endomorphism of a subobject set rebuilds the object

`action(identity)(subgroup)` on the stabilizer action of a subgroup set answers a *new* subgroup object rather than the subgroup, so `assert ... is subgroup` fails: the identity arrow of the classifying category does not act as the identity on the objects, and no equivariance can be stated.

Failing tests on main `36e5eac` (2026-11-14), one file per run in the published image:

- `tests/groups/test_predicate_kernel_and_stabilizer_subgroups_of_s4.sage::test_normalizer_retains_its_conjugation_action_functor`
  `assert Subgroup of Symmetric group S_3 is Subgroup of Symmetric group S_3`
  at `tests/groups/test_predicate_kernel_and_stabilizer_subgroups_of_s4.sage:69: in test_normalizer_retains_its_conjugation_action_functor`

Defective call: `restricted_stabilizer_action` (src/sage_extensions/categories/group/predicate_subgroups.py:1297) and the stabilizer action at :1294.

Introduced by: not bisected: both are in the root commit c731175 (2026-10-26, Zack Garza); blamed at :1297.

Scope: the stabilizer action on a subobject set; one test.

Triage record: `results/issue411-triage.md` (C22), slice of #411.
