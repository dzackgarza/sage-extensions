r"""A source file states what the code does, and its history is the commit body.

The reader of this library's source is a mathematician holding the code and
their own training.  What a docstring owes them is the convention in force where
several exist, the hypothesis a criterion applies under, the engine's input
demand or output shape, and a citation to the source of the mathematics.  An
issue number is none of these: it names a conversation about a change, whose
record is the commit that made it, so a line that carries one has replaced the
statement of what the code does with the history of how it came to say it -- and
a reader who wants the statement is sent to a tracker to find it.

So the contract is that no file the library ships names one.  Two facts are
asked here: the scan reports a mention it is handed (it would otherwise pass by
matching nothing), and the library's own source files name none.
"""


def test_the_scan_reports_the_line_that_names_an_issue():
    r"""A line spelling ``#`` and digits is reported by its path and line number.

    The scan is the whole of the evidence below, so it is asked first what it
    reports about a file written to be found: a docstring line naming an issue,
    and lines that state what the code does -- a rank, a page, a coefficient, a
    count -- which no number sign introduces.
    """
    sources = {
        "a_module.py": (
            "r\"\"\"The plane row of the rank-11 lattice.\"\"\"\n"
            "SPLIT = 1  # the plane splits off the lattice (#391)\n"
            "PAGE = 22\n"
        ),
    }

    reported = issue_number_mentions(sources)

    assert reported == ("a_module.py:2: SPLIT = 1  # the plane splits off the lattice (#391)",)


def test_no_source_file_names_an_issue_number():
    r"""Every file the library ships states what the code does and cites no issue.

    The files are the ones git tracks under ``src/``, so the assertion is about
    the library rather than about one machine's build output: a mention anywhere
    in them is a line whose reader has to go elsewhere for what it says.
    """
    assert issue_number_mentions() == ()
