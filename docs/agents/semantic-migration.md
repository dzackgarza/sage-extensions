# Semantic migration and its verification pass (2026-08-21)

## Semantic migration

- The preamble centrally holds research's locally-authored Sage code. The mathematics it presents is `lean-categories`'.
- A migration request establishes the value of the selected corpus.
- The executor decides destination and synthesis, not whether the corpus deserved preservation.
- The unit of migration is a mathematical notion, not a file.
- Read each notion once for semantics.
- The reader should migrate or synthesize it while that context is live.
- Do not separate deep analysis from implementation when implementation needs that mathematical context.
- Do not make one agent produce a report for an unrelated new agent to interpret.
- A summary is not the migrated mathematics.
- Move prior art into the live preamble before reconciling it with current code.
- Prefer a real move over a parallel rewrite.
- After a mistaken edit yields the correct state, repair forward.
- Do not undo the correct state merely to reproduce it by a preferred method.
- Reconcile source and destination until the result is semantically a move plus required updates.
- Delete the original only after every useful notion has a destination: a preamble presentation, or a `lean-categories` request for mathematics it lacks.
- Deletion is a receipt for completed relocation.
- It is never a value judgment on the source.
- Preserve code, tests, specifications, examples, design corpora, and incomplete research.
- Incomplete research remains research.
- Planning corpora can contain mathematical structure and future categorical homes; the mathematics in them is carried to `lean-categories` as requests, never adopted here.
- Stub declarations can present structure `lean-categories` formalizes before algorithms exist.
- Existing TDD suites are forward requirements and must migrate to the preamble surface.
- Existing parity tests can document delegation boundaries.
- False source mathematics creates an obligation: record it with its evidence and request the corrected mathematics from `lean-categories`.
- Do not delete the false statement and preserve only an error ledger.
- Non-code logs, telemetry, caches, and tool output are outside a mathematical code migration.
- Do not create dispositions or rulings for irrelevant material.

## Value and evidence during migration

- Byte equality has no positive or negative mathematical meaning.
- A checksum can locate possible duplicates but cannot decide semantic equivalence.
- Execution status does not determine research value.
- Maturity, polish, file name, directory, and current scope do not determine research value.
- The absence of callers does not determine research value.
- The absence of complete algorithms does not determine research value.
- A source outside the current preamble scope is a reason to enrich the preamble.
- It is not a deletion reason.
- Compare source and destination definitions, hypotheses, codomains, conventions, and behavior.
- Verify that the destination presents every useful mathematical distinction.
- If the destination cannot express a notion because `lean-categories` lacks it, request it there; research does not define it.
- Do not discard the notion because the destination is incomplete.

## Execution shape for large migrations

- Inventory files once.
- Partition them into disjoint semantic batches.
- Assign one reader to each artifact or notion.
- Read, decide, migrate or synthesize, and retire the source in one context.
- Do not analyze the same material in repeated waves.
- Do not create an analysis fleet followed by a context-free implementation fleet.
- Preserve an agent's mathematical context when revising its instructions.
- Ask it to checkpoint before stopping it.
- Stop only when its frame is unusable, not when one instruction changes.
- Use agent reasoning effort that matches the mathematics.
- Do not spend a large research context on a file move or import update.
- Perform simple moves and direct edits directly.
- Do not write edit scripts for a bounded hand edit.
- Do not replace a direct migration with scripts that match and rewrite source text.
- A sweeping architectural refactor need not pass tests at each intermediate state.
- Determine the correct final migration and execute the coherent sweep.
- Do not invent an incremental-green requirement that the user did not give.
- During a declared semantic-only migration, do not run tests, hooks, or Sage.
- Commit those migration units with the user's declared hook posture.
- Run the separate integrated verification pass only after the semantic migration finishes.

## QC and tooling house rules

- Global QC belongs in `ai-review-ci`.
- Local repositories delegate to that global owner.
- Sage source must be lowered to Python before Python type analysis.
- Type checkers inspect the lowered Python, not raw `.sage` syntax.
- The custom Sage parser must be globally available to the lowering path.
- `sage-stubs` supplies the global Sage type surface.
- Owned tools track the latest upstream default branch.
- Do not create fixed revision policy for fast-moving local projects.
- Diagnostic recipes must preserve detailed errors, warnings, and issues in logs.
- Their final output must name the detailed log paths.
- Test execution must produce wall-time and profiling artifacts.
- Agents should inspect those artifacts instead of rerunning long commands for omitted output.
- These rules govern the later verification pass.
- They do not authorize running verification during a semantic-only migration.
