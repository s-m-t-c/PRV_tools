PRV_tools

Sanitized tools for converting CSV -> PRV

Usage
-----

Convert a CSV to a PRV using the repository converter:

```bash
python csv_to_prv.py input.csv output.prv [layout.json]
```

If `layout.json` is not provided the script will look for `layout.json` next to `csv_to_prv.py`.

Relaxed comparator
------------------

A relaxed layout checker is provided as `compare.py`. It checks that generated PRV records have the expected
number of continuation lines and that the date/time positions appear near the expected columns. It is intended
to be forgiving about data values and focuses on layout/spacing.

Run it like:

```bash
python compare.py sample.prv generated.prv
```

License
-------

This repository contains sanitized, minimal tools derived from a private workspace. Use as you wish.
PRV_tools - minimal sample repo

Contains a small subset of tools to convert CSV→PRV and a tiny sample dataset.
