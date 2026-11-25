# Mathematical structure as implementation compression

An advisor can compress a large mathematical correction into one short
question.  The student must unfold the structure that makes the correction
true.  The question is not a request for the smallest compatible patch.

Consider an integral domain \(R\) and its fraction field
\(K=\operatorname{Frac}(R)\).  The advisor asks why ideals are not presented as
\(R\)-submodules of the regular module \(R\).  The advisor also asks why an
integral basis is not an \(R\)-basis of the relevant integral \(R\)-algebra.
These are not two method requests.  They expose one missing mathematical
foundation.

Scalar extension relates the algebra and module categories:

```text
Alg_R  -- K tensor_R (-) -->  Alg_K
 | U_R                         | U_K
 v                             v
Mod_R  -- K tensor_R (-) -->  Mod_K
```

The vertical functors take the underlying modules.  The horizontal functors
change scalars.  Their compatibility explains how algebra structure, module
structure, bases, subobjects, and morphisms move together.

For an integral \(R\)-algebra \(O\), its base change can give a
\(K\)-algebra \(A\):

\[
K\otimes_R O \cong A.
\]

The integral basis then belongs to the underlying \(R\)-module of \(O\).
It is not a new tuple-valued operation attached directly to \(A\).  The same
base-change structure gives \(K\otimes_R R[x]\cong K[x]\).  Polynomial rings
and number-field algebras therefore belong to one scalar-change theory.

This theory is implementation compression.  Ideals can use module and
subobject operations.  Bases can use the free-module structure.  Algebra
morphisms can move through scalar extension.  Many apparent missing methods
become consequences of structures that `lean-categories` formalizes and the
repository already presents.

The failed trajectory hears only the word "basis".  It asks PARI for
elements and returns a tuple in \(A\).  It can also take a chosen
\(K\)-basis and clear denominators.  Both actions produce local data while
leaving the algebra and functors absent.

Clearing denominators selects a presentation-dependent \(R\)-lattice.  It
does not by itself select the integral closure or a maximal order.  It gives
no coherent action on morphisms.  It therefore cannot explain later basis,
ideal, or transport operations.

Rejecting a Sage order wrapper does not remove the mathematical order.  It
makes ownership of the integral \(R\)-algebra more important.  PARI can
compute data used to construct that object.  PARI cannot replace the object
or the functorial structure around it.

The advisor's question reveals why dozens of methods remain missing.  Their
absence is not necessarily a backlog of local implementations.  It can show
that one theoretical foundation is absent.  Once that foundation exists,
the apparently difficult work can become generic and small.

The lesson is not a rule that functors always precede methods.  The lesson is
to recognize mathematical compression.  A deep correction can change which
work exists at all.  Preserving the old implementation with a cheap
workaround preserves the misunderstanding that created the work.
