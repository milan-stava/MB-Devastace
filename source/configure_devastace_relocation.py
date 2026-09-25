"""Set the 16-bit helper-block destination in the MBDEVY9.3 binary.

Example: python3 configure_devastace_relocation.py --dest 0x8000
This modifies only file offsets 0x0C26..0x0C27 of a new copy.
"""
import argparse
import hashlib
from pathlib import Path

EXPECTED='b5be03ca690c3dc85a3893913ddad4b717af0be7d74292d171695160c09e3003'
INPUT=Path('MBDEVY9.3')
OFFSET=0x0c26

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dest',required=True,help='16-bit address, e.g. #8000 or 0x8000')
parser.add_argument('--output',type=Path,help='new BSDOS .3 filename')
args=parser.parse_args()
number=args.dest.strip().replace('#','0x',1)
try:
    target=int(number,0)
except ValueError:
    parser.error('destination must be a 16-bit hexadecimal or decimal address')
if target!=0x5b00 and not 0x6000<=target<=0xff00:
    parser.error('choose #5B00 or writable, permanently accessible RAM #6000..#FF00')

data=bytearray(INPUT.read_bytes())
if hashlib.sha256(data).hexdigest()!=EXPECTED:
    parser.error('MBDEVY9.3 differs from the verified base binary')
assert data[OFFSET:OFFSET+2]==bytes.fromhex('00 5b')
out=args.output or Path(f'MBDEVY9_{target:04X}.3')
if out.resolve()==INPUT.resolve():
    parser.error('output must differ from the base binary')
data[OFFSET:OFFSET+2]=target.to_bytes(2,'little')
out.write_bytes(data)
print(f'{out}: destination #{target:04X}, file offsets #0C26..#0C27 = {data[OFFSET]:02X} {data[OFFSET+1]:02X}, length {len(data)}')
