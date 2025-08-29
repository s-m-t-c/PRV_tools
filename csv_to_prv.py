"""csv_to_prv.py (sanitized for repository)

Convert a CSV into a fixed-width PRV-like file. This version avoids any
absolute/local filesystem assumptions: defaults are repository-relative and
all paths may be passed on the command line.

Usage:
  python csv_to_prv.py input.csv output.prv [layout.json]
If layout.json is not provided the script will look for `layout.json` next to
this script.
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path
from collections import defaultdict
import json

# Defaults (repo-relative)
HERE = Path(__file__).resolve().parent
CSV_DEFAULT = HERE / "sample.csv"
OUT_DEFAULT = HERE / "sample.prv"
LAYOUT_JSON = HERE / "layout.json"

SENSOR_COUNT = 22


def fmt_exp_field(val, width=10) -> str:
    # simplified, robust exponential formatter inspired by the original
    try:
        if val is None or str(val).strip() == '':
            mant = 0.0
        else:
            mant = float(val)
    except Exception:
        mant = 0.0

    if mant == 0.0:
        rep = '.00000E+0'
    else:
        sign = '-' if mant < 0 else ''
        a = abs(mant)
        exp = 0
        while a >= 10.0:
            a /= 10.0; exp += 1
        while a < 0.1 and a != 0.0:
            a *= 10.0; exp -= 1
        mantissa = f"{a:.5f}"
        if mantissa.startswith('0'):
            mantissa = mantissa[1:]
        exp_sign = '+' if exp >= 0 else '-'
        rep = f"{sign}{mantissa}E{exp_sign}{abs(exp)}"
    if len(rep) > width:
        rep = rep[-width:]
    return rep.rjust(width)


def load_layout(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def place_into_line(buf: list, span, text: str):
    start, end = span
    width = end - start + 1
    s = str(text)
    if len(s) > width:
        s = s[:width]
    s = s.rjust(width)
    for i, ch in enumerate(s):
        buf[start - 1 + i] = ch


def convert(csv_path: Path, out_path: Path, layout_path: Path | None = None) -> int:
    csv_path = Path(csv_path)
    out_path = Path(out_path)
    layout_path = Path(layout_path) if layout_path else LAYOUT_JSON
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return 1
    layout = load_layout(layout_path)
    if layout is None:
        print(f"layout.json not found at {layout_path}")
        return 2

    cont_lines = layout.get('most_common_cont_lines', 6)
    line_spans = [l['common_spans'] for l in layout.get('lines', [])]

    groups = defaultdict(int)
    with csv_path.open(newline='') as fh, out_path.open('w', newline='') as out:
        reader = csv.DictReader(fh)
        row_count = 0
        for row in reader:
            key = (row.get('Program', '').strip(), row.get('PTT', '').strip())
            groups[key] += 1
            msg_index = groups[key]

            program = str(row.get('Program', '')).zfill(5)
            ptt = str(row.get('PTT', '')).zfill(6)
            msg_idx_s = str(msg_index).rjust(3)
            sensor_cnt = str(SENSOR_COUNT).rjust(2)
            sat = str(row.get('Satellite', '')).strip().ljust(1)
            header = f"{program} {ptt}  {msg_idx_s} {sensor_cnt} {sat}"
            out.write(header + '\n')

            sensors = [row.get(str(i), '') for i in range(1, SENSOR_COUNT + 1)]
            msgdate = row.get('Message date', '')
            dt_date = '0000-00-00'; dt_time = '00:00:00'
            try:
                if msgdate:
                    datepart, timepart = msgdate.split()
                    d, m, y = datepart.split('/')
                    dt_date = f"{y.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}"
                    hhmm = timepart.split(':')
                    if len(hhmm) == 2:
                        dt_time = f"{hhmm[0].zfill(2)}:{hhmm[1].zfill(2)}:00"
                    else:
                        dt_time = ':'.join([p.zfill(2) for p in hhmm])
            except Exception:
                pass

            sens_idx = 0
            li = 0
            while sens_idx < len(sensors) and li < len(line_spans):
                buf = [' '] * layout.get('line_length', 78)
                spans = line_spans[li]
                if li == 0:
                    place_into_line(buf, (7, 16), dt_date)
                    place_into_line(buf, (18, 25), dt_time)
                    comp = row.get('Compression index', '') or '1'
                    place_into_line(buf, (28, 28), str(comp))
                for span in spans:
                    if sens_idx < len(sensors):
                        v = sensors[sens_idx]
                        if v in (None, ''):
                            v = 0
                        w = span[1] - span[0] + 1
                        txt = fmt_exp_field(v, width=w)
                        place_into_line(buf, span, txt)
                        sens_idx += 1
                    else:
                        break
                out.write(''.join(buf).rstrip() + '\n')
                li += 1

            while sens_idx < len(sensors):
                buf = [' '] * layout.get('line_length', 78)
                fallback_spans = [(7, 16), (18, 25), (28, 36), (37, 45), (46, 54), (55, 63)]
                for span in fallback_spans:
                    if sens_idx >= len(sensors):
                        break
                    v = sensors[sens_idx]
                    if v in (None, ''):
                        v = 0
                    w = span[1] - span[0] + 1
                    txt = fmt_exp_field(v, width=w)
                    place_into_line(buf, span, txt)
                    sens_idx += 1
                out.write(''.join(buf).rstrip() + '\n')
            row_count += 1

    print(f"Wrote {row_count} records to {out_path}")
    return 0


if __name__ == '__main__':
    csvp = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_DEFAULT
    outp = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT
    layoutp = Path(sys.argv[3]) if len(sys.argv) > 3 else LAYOUT_JSON
    sys.exit(convert(csvp, outp, layoutp))

