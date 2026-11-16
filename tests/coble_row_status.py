r"""What one row of a Coble acceptance driver did, and the exit status that says it.

The two acceptance drivers of the Coble rows -- ``coble_kernel_plane_rows``,
the orbits of primitive isotropic planes of ``T_Co`` under the kernel
subgroups, and ``coble_gamma_co_2_incidence_rows``, the Tits-building
incidence of line and plane orbits -- take one row at a time under a per-row
cap and report what the row did.  Five things a row can do are different facts
about a run, and each has its own status:

* ``DECIDED`` -- the row returned, and every representative or edge it
  returned satisfies the row's contract;
* ``UNDECIDED`` -- the call did not return inside the caller's cap.  The cap is
  the caller's budget, not a mathematical statement, so the row claims nothing
  about the mathematics;
* ``CONTRACT_VIOLATION`` -- the row returned a representative, an edge or a
  relation that fails its check.  That is a statement about the library's
  answer, and not about the budget;
* ``COUNT_MISMATCH`` -- the row decided, and its count is not the count an
  independent computation of the same row gives;
* ``ERROR`` -- the row step raised.  A refused or failing call is neither the
  caller's budget nor a statement about the mathematics: the driver prints the
  traceback and the run ends on this status.

A status carries the words a report is worded with and the exit status of a run
that ends on it, so the mapping from a status to its exit status is total by
construction: these members are the whole of what a row can report.
"""

import enum


class RowStatus(enum.Enum):
    r"""What one row did, with the words it is reported in and its run's exit status."""

    DECIDED = ("decided", 0)
    UNDECIDED = ("undecided", 1)
    CONTRACT_VIOLATION = ("contract violation", 2)
    COUNT_MISMATCH = ("count mismatch", 3)
    ERROR = ("error", 4)

    @property
    def words(self):
        r"""The status as a row's report words it."""
        return self.value[0]

    @property
    def exit_status(self):
        r"""The exit status of a run that ends on this status."""
        return self.value[1]
