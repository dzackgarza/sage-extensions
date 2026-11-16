r"""What one row of a Coble acceptance driver did, and the exit status that says it.

The two acceptance drivers of the Coble rows -- ``coble_kernel_plane_rows``,
the orbits of primitive isotropic planes of ``T_Co`` under the kernel
subgroups, and ``coble_gamma_co_2_incidence_rows``, the Tits-building
incidence of line and plane orbits -- take one row at a time under a per-row
cap and report what the row did.  The outcomes are different facts about a
run, so each has its own status and its own exit status:

* ``DECIDED`` -- the row returned, and every representative or edge it
  returned satisfies the row's contract;
* ``UNDECIDED`` -- the call did not return inside the caller's cap.  The cap
  is the caller's budget, not a mathematical statement, so the row claims
  nothing about the mathematics;
* ``CONTRACT_VIOLATION`` -- the row returned a representative or an edge that
  fails its check.  That is a statement about the library's answer, and not
  about the budget.

A decided row is then compared with an independent count of the row, and a
decided row whose count differs is the fourth exit status: the row decided,
and its answer is wrong.

``exit_status`` maps these to the run's report: ``0`` every row decided and
equal to its count, ``1`` a row undecided or the whole-run budget spent, ``2``
a returned representative or edge that breaks its contract, ``3`` a decided row
whose count differs.
"""

import enum


class RowStatus(enum.Enum):
    r"""What one row did: decided, undecided, or a broken contract."""

    DECIDED = "decided"
    UNDECIDED = "undecided"
    CONTRACT_VIOLATION = "contract violation"


EXIT_DECIDED = 0
EXIT_UNDECIDED = 1
EXIT_CONTRACT_VIOLATION = 2
EXIT_COUNT_MISMATCH = 3


def exit_status(status):
    r"""The exit status of a run whose row did ``status``."""
    match status:
        case RowStatus.DECIDED:
            return EXIT_DECIDED
        case RowStatus.UNDECIDED:
            return EXIT_UNDECIDED
        case RowStatus.CONTRACT_VIOLATION:
            return EXIT_CONTRACT_VIOLATION
    raise ValueError(f"{status} is not the status of a row")
