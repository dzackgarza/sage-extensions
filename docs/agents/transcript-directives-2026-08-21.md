# Transcript-derived research directives (2026-08-21)

The governing model is:

- Mathematics determines the architecture.
- Categories own generic operations.
- Concrete classes store only necessary construction data.
- A leaf category handles only its immediate supercategory.
- Structure and methods must then propagate through the full category chain.
- The system must support parent, element, and subcategory methods.
- Category methods should precede class methods in the MRO.
- Concrete classes can then supply faster implementations when necessary.
- New leaf categories must need little repeated code.
- Generated methods are unacceptable because mathematicians cannot audit their source.

Specific mathematical directives include:

- A lattice is first a set and a module.
- Cardinality belongs to its underlying set.
- A formed module is constructed from its form morphism.
- Bilinear forms use the tensor square.
- Quadratic forms use the divided square.
- These form types require separate free-forgetful adjunctions.
- Forgetting a form is a functor, not an object method.
- Module morphisms require the same base ring.
- Every module-related category must require its base ring.
- `IntegralLattices` must also require an explicit ring.
- Membership predicates belong to refined subcategories.
- An object claiming membership must supply the required predicate.
- Other operations should remain category methods.
- Axiomatic subcategories need not have separate concrete realization classes.
- Special algorithms can make otherwise undecidable questions decidable on restricted categories.
- KBMAG is valuable for exactly this reason.
- Differences between full reflection groups and smaller reflection subgroups are substantive research results.

The migration philosophy is semantic preservation:

- A corpus selected for migration is presumed valuable.
- Every file must receive one semantic reading.
- Preserve mathematics, specifications, tests, examples, design work, and incomplete research.
- Incomplete research is not disposable.
- Foundational categories remain valuable without current callers.
- Tests and known values are mathematical products.
- Incorrect mathematics should produce a corrected statement.
- Deletion alone does not preserve the lesson.
- Remove a source only after its useful content has a durable destination.
- Byte equality, execution status, file names, maturity, and polish do not measure mathematical value.
- Do not split reading and implementation between agents when the reader’s mathematical context is essential.
- Prefer migration of existing prior art over a parallel implementation.

The epistemic directive is equally strong:

- A false architectural claim requires a review of foundational assumptions.
- Local counts and reduced error totals do not establish correctness.
- Inspect existing code, archived work, plans, and repository memory first.
- Use transcripts only when those sources do not resolve the question.
- Do not ask the user to make a technical decision that the assigned research should determine.
- Ask only when several materially different interpretations remain.

The recent verification rules were specific to the migration project:

- Perform the complete semantic migration before automated verification.
- Do not treat unverified work as deferred verification.
- Do not run Sage, tests, or hooks during that migration.
- Commit migration units without verification.
- Hold pushes until the later integrated verification pass.
- That later pass must use global `ai-review-ci` ownership.
- Sage source must be lowered before Python type analysis.
- QC must preserve detailed logs and wall-time reports.
- Local projects should follow current upstream `main`, not fixed revision pins.

Communication must report mathematical effects. It must not report token use, agent waves, repeated checks, or administrative state.
