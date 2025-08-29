"""compare.py - relaxed PRV layout checker

Usage:
  python compare.py sample.prv generated.prv

This script checks per-record that the number of continuation lines in the
generated PRV roughly matches the sample and that the date/time tokens are at
approximately the expected columns. It's intentionally permissive about numeric
values.
"""
from __future__ import annotations
import sys
from pathlib import Path


def parse_records(path: Path):
    """Return a list of records, where each record is a list of lines (strings)."""
    recs = []
    cur = []
    with path.open('r', encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line:
                continue
            if line and line[0].isdigit() and ' ' in line and line.split()[0].isdigit() and len(line.split()[0]) >= 5:
                # crude header detection: starts with program id digits
                if cur:
                    recs.append(cur)
                cur = [line]
            else:
                if cur is None:
                    cur = [line]
                else:
                    cur.append(line)
    if cur:
        recs.append(cur)
    return recs


def check_layout(sample_recs, gen_recs, date_col=7, time_col=18, tol=2):
    from statistics import median
    sample_conts = [len(r) - 1 for r in sample_recs if len(r) > 0]
    gen_conts = [len(r) - 1 for r in gen_recs if len(r) > 0]
    if not sample_conts or not gen_conts:
        print('No records to compare')
        return False
    samp_med = int(median(sample_conts))
    gen_med = int(median(gen_conts))
    print(f'sample median cont lines: {samp_med}, generated median cont lines: {gen_med}')

    # sample a subset and ensure date/time tokens exist near expected columns
    def has_date_time(line0):
        if len(line0) < date_col:
            return False
        d = line0[date_col-1:date_col+9]
        t = line0[time_col-1:time_col+8]
        return ('-' in d) and (':' in t)

    checks = 0
    passed = 0
    pairs = min(len(sample_recs), len(gen_recs), 50)
    for i in range(pairs):
        sr = sample_recs[i]
        gr = gen_recs[i]
        checks += 1
        ok = True
        # continuation count tolerance
        if abs((len(sr)-1) - (len(gr)-1)) > 2:
            ok = False
        # date/time presence in first continuation line (if present)
        if len(gr) > 1:
            if not has_date_time(gr[1]):
                ok = False
        if ok:
            passed += 1
    print(f'Passed {passed}/{checks} sampled records')
    return passed == checks


def main():
    if len(sys.argv) < 3:
        print('Usage: python compare.py sample.prv generated.prv')
        return 2
    sample = Path(sys.argv[1])
    gen = Path(sys.argv[2])
    sample_recs = parse_records(sample)
    gen_recs = parse_records(gen)
    ok = check_layout(sample_recs, gen_recs)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
