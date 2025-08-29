# copy of the converter (trimmed header)
from pathlib import Path
import json
from collections import defaultdict

# minimal: import the existing converter
from C:\\Users\\seanm\\Documents\\AWS\\csv_to_prv import convert

if __name__ == '__main__':
    import sys
    csvp = sys.argv[1]
    outp = sys.argv[2]
    convert(Path(csvp), Path(outp))
