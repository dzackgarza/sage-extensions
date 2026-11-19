r"""A run over a foreign lattice decides, and compares nothing it should not.

``tests/coble_gamma_co_2_incidence_rows.py`` states the Coble lattice's values
beside what it computed, for the Coble lattice.  Two properties of the *run* --
not of the comparison helper -- decide that the stating is not a condition:

* the ``Otilde`` row of ``U + U + <-4>`` decides, and the process exits with the
  decided row's status.  A page-value gate written in ``main`` as an unguarded
  comparison against the archive's ``(569160, 527, 189720)`` fires on this run,
  which computes one edge over one line cusp and one plane cusp, and the status
  below would then be the mismatch status and not zero;
* the run records no comparison at all, because the archive's numbers are
  ``T_Co``'s: a row of another lattice must not be read against them.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_kernel_row_of_a_foreign_lattice_decides_and_records_no_comparison():
    r"""The status is the decided row's, and nothing was compared against the archive.

    ``--plane-class-index 0`` keeps the run to the relation, so the status is
    reached on the row's own contract alone.
    """
    status, comparisons = incidence_rows_run(
        [
            "--rows", "Otilde",
            "--lattice", "U+U+<-4>",
            "--plane-class-index", "0",
            "--cap", "600",
        ]
    )
    assert comparisons == ()
    assert status == int(0)
