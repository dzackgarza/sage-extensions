r"""The Eichler transvection reads its data once, not once per entry.

For isotropic \(e\) and \(a\in e^\perp\),

\[
t(e,a)\colon v\longmapsto v-(a,v)\,e+(e,v)\,a-\tfrac12(a,a)(e,v)\,e ,
\]

equation (4) of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, printed
p. 8.  Its matrix in a basis of rank \(n\) is \(n^2\) entries, and the ring
arithmetic those entries need is the engine's: the vectors' coordinates and the
Gram matrix already are engine data, and the matrix the construction returns is
engine data, which is what the transvection is assembled from.

What must not scale with \(n^2\) is the number of times the construction crosses
between the owned ring and the engine.  It needs each vector's coordinates once
and one integrality decision per generator -- the statement that
\(\tfrac12 q(a)b(e,x)\) lies in the coefficient ring, by which the transvection
preserves the lattice.  It needs neither a vector's coordinates per basis label
nor the ring's own one per diagonal entry, which is what the construction asked
for while it did the entries' arithmetic in the owned ring: on
`T_Co`'s rational lattice eleven coordinates were read eleven times each and one
transvection took 16.9 ms of which the entries took 15.9 ms (#528).

The contract asserted here is a call count, never a time.  The engine-free
arithmetic of the same matrix is 0.365 ms against the 16.9 ms, and no test of
this suite may assert a duration.
"""

import pytest

from sage_extensions.all import *


def test_a_transvection_reads_each_vector_and_the_ring_once() -> None:
    r"""One transvection reads \(e\) once, \(a\) once, and the ring's one at most once.

    The control is \(U\oplus\langle 2\rangle\) over `QQ` in the basis
    \(e_0,e_1,e_2\), with \(e=e_0\) isotropic, \(f=e_1\) its hyperbolic
    partner of pairing one, and \(a=e_2\) of square two and \(b(e,a)=0\), so
    the transvection is not the identity: on the pair it is
    \(t(e,a)(e)=e\) and \(t(e,a)(f)=f+a-\tfrac12 q(a)\,e = f+a-e\).  That
    second image is what reads the coefficient \(\tfrac12 q(a)\): a
    construction that divided by the ring's one instead of by two sends \(f\) to
    \(f+a-2e\), and the control's own square-two \(a\) cannot see the
    difference on \(a\) alone.  Before the repair the same
    call read \(e\)'s coordinates three times -- once per basis label -- read
    \(a\)'s five, and asked the ring for its one five times, once per diagonal
    entry.  It now reads them three, five and at most one: the two reads of \(a\)
    beyond the construction's own are the guards' `q(a)` and `b(e,a)` and are the
    same at both readings, and the one of the ring is a cold-cache read of the
    isometry's assembly, not one per entry.

    Counted on the instances the caller holds, because a test reads no private
    attribute (TL02); the method shadowed is the vector's coordinate reader and
    the ring's own one.
    """
    lattice = Lattices(QQ)([[0, 1, 0], [1, 0, 0], [0, 0, 2]])
    labels = tuple(lattice.module_generating_set())
    isotropic = lattice.module_generator(labels[0])
    orthogonal = lattice.module_generator(labels[2])
    ring = lattice.base_ring()
    assert isotropic.q() == ring.zero()
    assert isotropic.b(orthogonal) == ring.zero()

    counts = {"the coordinates of e": 0, "the coordinates of a": 0, "the one of the ring": 0}

    def counted(name, original):
        def reread(*arguments, **keywords):
            counts[name] += 1
            return original(*arguments, **keywords)

        return reread

    isotropic_reader = isotropic.to_vector
    orthogonal_reader = orthogonal.to_vector
    ring_one = ring.one
    isotropic.to_vector = counted("the coordinates of e", isotropic_reader)
    orthogonal.to_vector = counted("the coordinates of a", orthogonal_reader)
    ring.one = counted("the one of the ring", ring_one)
    transvection = lattice.eichler_transvection(isotropic, orthogonal)
    isotropic.to_vector = isotropic_reader
    orthogonal.to_vector = orthogonal_reader
    ring.one = ring_one

    partner = lattice.module_generator(labels[1])
    assert isotropic.b(partner) == ring.one()
    assert transvection(isotropic) == isotropic
    assert transvection(partner) == partner + orthogonal - isotropic
    assert counts["the coordinates of e"] == 1
    assert counts["the coordinates of a"] == 3
    assert counts["the one of the ring"] <= 1
