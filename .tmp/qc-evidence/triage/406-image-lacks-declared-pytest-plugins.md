The declared pytest invocation cannot start in the image the suite runs in: pytest-timeout and pytest-reportlog are not installed

`pyproject.toml`'s `[tool.pytest.ini_options] addopts` carries `--timeout=60 --timeout-method=signal` and `--report-log=tests/.report/run.jsonl`, and both plugins are declared in `[dependency-groups] dev`, but the Sage venv used for these runs carries `pytest` alone, so the invocation stops during argument parsing, before any plugin loads:

```
ERROR: usage: python -m pytest [options] [file_or_dir] [file_or_dir] [...]
python -m pytest: error: unrecognized arguments: --timeout=60 --timeout-method=signal --report-log=tests/.report/run.jsonl
  inifile: /repos/sage-extensions/pyproject.toml
  rootdir: /repos/sage-extensions
EXIT=4
```

The gap is older than this issue: the head note of `.tmp/qc-evidence/INDEX.md` records the same missing plugins and that every published log was taken with `addopts` blanked for that reason.

Every run cited in #406 supplied `pytest-timeout` and `pytest-reportlog` at `.scratch/wt406/.pydeps` on `PYTHONPATH`, which is not part of the repository and not part of the image.

Because this fails at argument parsing, none of the gates, none of the lint and none of the tests run: the whole suite is unmeasured on any host with this venv.

Acceptance: the environment in which the suite is declared to run provides the declared `dev` dependency group (so `just test` runs the repository's `addopts` unchanged), or the `addopts` stop naming plugins the image does not install.
