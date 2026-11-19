r"""The ambient ``O(L)`` row runs through the driver, whose other rows carry a quotient.

``tests/coble_gamma_co_2_incidence_rows.py`` takes its rows under subgroups of
``O(L)``.  Three of the four labels are subgroups that retain a finite character
quotient -- the restricted stabilizers and the two kernel groups -- and one, the
``O`` row, is the ambient group itself, which retains none: the class route is
not defined for it and the driver takes the certificate route, as its own route
decision states.

A row's optional record of the plane class index is about the finite image, so it
is asked only of a row that has one.  Asking every row for it makes the ambient
row fail on a group that has no quotient -- and it fails after the row has
decided, in the driver's own code, which is why the failure is the driver's and
not the library's.

The lattice is ``6JRS = U + U + <-2>``, whose ``|O(A_L)|`` is one, so the
ambient row is one vertex of each kind joined by one edge and the whole driver
run costs seconds.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_ambient_row_decides_through_the_driver_and_records_no_class_index():
    r"""The ``O`` row on ``6JRS`` decides, and the run exits zero.

    The ambient group has no finite character quotient, so the plane class index
    -- a quotient of two orders of the finite image -- is not defined at its row
    and nothing about it is recorded.  The row itself is decided, which is what
    the run's exit status has to say.
    """
    status = incidence_rows_exit(
        ["--rows", "O", "--lattice", "6JRS", "--plane-class-index", "2", "--cap", "600"]
    )
    assert status == int(0)
