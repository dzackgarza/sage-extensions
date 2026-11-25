# Addendum: private Sage-runtime realization of preamble category types

The [architecture specification](../../CONTRIBUTING.md#preamble-architecture-specification)
governs this boundary. Host runtime reuse and engine computation are different
responsibilities. Neither permits a Sage mathematical parent or element to become
the public preamble object by reclassification, subclassing, or facade parenting.

The preamble's category graph supplies `ObjectType`, `ElementType`, and
Hom-category types. Its root runtime may use Sage `Parent`, `Element`,
dynamic-class machinery, and method containers to realize those generated types.
`ParentMethods`, `ElementMethods`, and `SubcategoryMethods` name private Sage
mechanisms, not public placement. Keep the mapping in the shared runtime; descendants
declare their immediate mathematical structure and do not assemble host bases.

The shared construction path establishes required data before public return.
Only the root owns non-cooperative host initialization. A host post-init or
element-construction hook implements that path and cannot bypass it. Refinement
acts on a preamble object whose supplied data place it in the added category;
it neither constructs missing data by a label, nor follows a computed answer,
nor adopts a foreign instance.

Method-resolution details remain private. The runtime must make the selected
preamble operation authoritative, preserve existing justified placements, and
propagate element and morphism behavior through the same graph. If private
Sage category joining or dynamic-class ordering is required, implement it once
at that owner under its declared protocol. Consumers do not call
`_refine_category_`, rebuild `__class__`, install methods, or intercept engine
constructors to change a result's public meaning.

Concrete Sage rings, modules, groups, matrices, and their elements remain private
computation representations. An adapter builds them from preamble data, invokes
established algorithms, then raises every result through the preamble constructors.
It does not reclass those Sage objects, patch their APIs, or teach Sage
constructors to accept preamble parents. Private computational workspace mutation
does not alter the defining data. Cache and lifetime choices respect `OWN-10`.

Historical mechanisms remain inspectable at
`archives/lattice-research/src/sage_patches/ring_base_category.py`,
`archives/lattice-research/src/sage_patches/ideal_submodule.py`,
`archives/lattice-research/src/sage_patches/fraction_quotients.py`, and
`archives/lattice-research/src/sage_patches/module_enrichment.py`, or in their
source history. These are references, not sanctioned public construction routes.
The live construction contract above is what future code must satisfy.
