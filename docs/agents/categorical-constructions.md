# Categorical constructions carry structural relations

The preamble has categories, method classes, and the category graph. It has no
independent behavior-composition layer.

- Do not call a preamble component a `mixin`.
- Do not insert a hand-written Python base to state a mathematical relation.
- State the relation, as `lean-categories` formalizes it, in the category graph.
- Class inheritance can implement the graph after category placement.
- Class inheritance must never replace categorical placement.
- `ObjectType`, `ElementType`, and Hom-category element types expose operations placed
  on a category in the public preamble architecture.
- Sage `ParentMethods`, `ElementMethods`, and `MorphismMethods` are private runtime
  implementation vocabulary during migration, not a second public class graph.

The set of core categorical constructions is small. Inspect all existing owners
before creating another construction.

- Start with `Cat.Object`, `SliceOver`, `CosliceUnder`, `Product`, `Coproduct`,
  `Biproduct`, `TensorProduct`, `Kernel`, and `Cokernel`.
- Inspect the preamble's module-level `Subobjects` construction as part of the same
  analysis.
- Use this subtree as the canonical construction vocabulary.
- Do not create a local helper for a relation already represented there.
- Do not let a preamble category silently use Sage's parallel construction.
- Resolve the construction owner instead of patching each call site.
- Do not keep two construction paths for the same mathematical construction.

Modules with varying base rings project to the category of rings. Modules over a
fixed ring form one fiber of that projection.

- A construction that requires one base ring belongs inside that fiber.
- Scalar extension and scalar restriction connect different fibers.
- Do not encode the same-base condition through Python inheritance or method
  resolution.
- Products, coproducts, tensor products, kernels, and cokernels must preserve the
  selected base ring when their definitions require it.
- A category join that returns `None` from `base_ring()` exposes an incorrect
  categorical relation.
- Fix the join or construction that lost the base ring.
- Do not add a local `base_ring()` override before that relation is correct.

A formed module is a module equipped with a form morphism. It is not a wrapper
around another module.

- Never inspect `__dict__` to discover mathematical structure.
- Never recover a deleted wrapper field through direct storage access.
- Ask the category-owned interface for the form and its defining module.
- A construction must define its action on objects and morphisms.
- A parent-only result does not establish a categorical construction.

Let `i: A -> M` be a subobject inclusion. For a bilinear form
`b: M tensor M -> R`, the induced form is `b compose (i tensor i)`.

- Implement formed subobjects through this functorial pullback.
- For another form classifier, apply its source functor to `i` before composition.
- Do not infer formed-subobject behavior from `_form` or `_module` storage fields.
- The subobject construction owns this transport.

When a correction identifies an existing construction subtree, return to that
owner immediately.

- Do not reduce the correction to a naming change.
- Do not continue a local field repair after the ownership error is known.
- Trace the canonical constructor, category join, parent construction, morphism
  action, and inherited methods as one path.
- A local patch is incomplete while that path remains incoherent.
- If local edits stop producing mathematical progress, return to the categorical
  construction. Do not stop the assigned work.
