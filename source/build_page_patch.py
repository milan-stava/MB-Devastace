"""Build/check Y and configurable print-buffer relocation.

The input binary remains untouched. This intentionally small assembler accepts
only the instructions used in the added routine, making the byte-level patch
reproducible without requiring a particular installed Z80 toolchain.
"""
from pathlib import Path
import hashlib
import re

ORIGINAL_SHA256 = '24c6dd199b2c7d1d30da1c07d054e319400a0cce2914e98cb78e4481c0489408'
BASE = 0x4000
START = 0x4c03
LIMIT = 0x4c8c
source = Path('Devastace_MB03_page_Y.a80').read_text()
original = Path('MBDEVMB03_original.bin').read_bytes()
assert len(original) == 7168
assert hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256

lines = []
for raw in source.splitlines():
    line = raw.split(';', 1)[0].strip()
    if line:
        lines.append(line)

def n(s, labels):
    s=s.strip()
    if s.startswith('#'): return int(s[1:],16)
    if s.isdecimal(): return int(s)
    return labels[s]

def encode(line, pc, labels, sizing=False):
    if line.startswith('ORG '):
        assert n(line[4:],labels)==START
        return b''
    if line.startswith('ASSERT '):
        if not sizing:
            if line=='ASSERT page_reloc_destination == #4C26':
                assert labels['page_reloc_destination']==0x4c26
            else:
                assert n('page_end',labels)<=LIMIT
        return b''
    if line.startswith('DW '):
        args=line[3:].split(',')
        vals=[n(x,labels) if not sizing else labels.get(x.strip(),int(x.strip()[1:],16) if x.strip().startswith('#') else 0) for x in args]
        return bytes(y for v in vals for y in (v&255,v>>8))
    if line.startswith('DB '):
        parts=re.findall(r"'[^']*'|[^,]+",line[3:])
        return bytes(x for part in parts for x in (part[1:-1].encode('ascii') if part.startswith("'") else [n(part,labels)]))
    if line=='BIT 0,(IY+0)':return bytes.fromhex('fd cb 00 46')
    if line=='BIT 7,B':return bytes.fromhex('cb 78')
    if line=='SET 7,B':return bytes.fromhex('cb f8')
    if line in ('OR A','OR C','PUSH HL','POP HL','PUSH DE','POP DE','INC HL','DEC HL','INC (HL)','DEC (HL)','INC B','DEC B','DEC A','PUSH AF','POP AF','RET','RET Z','RET NZ','RET NC','RET C','ADD A,A','ADD A,C','ADD A,D','ADD A,L','ADD HL,BC','EX DE,HL','LD A,(HL)','LD D,(HL)','LD C,A','LD C,D','LD C,L','LD D,A','LD B,H','LD E,A','LD A,E','LD A,B','LD A,C','LD A,H','LD A,L','LD L,A','LD (HL),E','LD (HL),D','LD (HL),C','LD E,(HL)','LD E,C'):
        return bytes([{'OR A':0xb7,'OR C':0xb1,'PUSH HL':0xe5,'POP HL':0xe1,'PUSH DE':0xd5,'POP DE':0xd1,'INC HL':0x23,'DEC HL':0x2b,'INC (HL)':0x34,'DEC (HL)':0x35,
            'DEC A':0x3d,'ADD HL,BC':0x09,'EX DE,HL':0xeb,'LD D,(HL)':0x56,'LD B,H':0x44,'LD C,L':0x4d,'LD (HL),D':0x72,
            'INC B':0x04,'DEC B':0x05,'PUSH AF':0xf5,'POP AF':0xf1,'RET':0xc9,'RET Z':0xc8,'RET NZ':0xc0,'RET NC':0xd0,'RET C':0xd8,
            'ADD A,A':0x87,'ADD A,C':0x81,'ADD A,D':0x82,'ADD A,L':0x85,'LD A,(HL)':0x7e,
            'LD C,A':0x4f,'LD C,D':0x4a,'LD D,A':0x57,'LD E,A':0x5f,'LD A,E':0x7b,'LD A,B':0x78,'LD A,C':0x79,'LD A,H':0x7c,'LD A,L':0x7d,
            'LD L,A':0x6f,'LD (HL),E':0x73,'LD (HL),C':0x71,'LD E,(HL)':0x5e,'LD E,C':0x59}[line]])
    if line=='LDIR':return bytes.fromhex('ed b0')
    if line.startswith('LD SP,'):return bytes([0x31,*word(line[6:],labels,sizing)])
    if line.startswith('LD BC,'):return bytes([0x01,*word(line[6:],labels,sizing)])
    if line.startswith('LD DE,(') and line.endswith(')'):
        return bytes([0xed,0x5b,*word(line[7:-1],labels,sizing)])
    if line.startswith('LD HL,(') and line.endswith(')'):
        return bytes([0x2a,*word(line[7:-1],labels,sizing)])
    if line.startswith('LD DE,'):return bytes([0x11,*word(line[6:],labels,sizing)])
    if line.startswith('LD HL,'):
        target=n(line[6:],labels) if not sizing else labels.get(line[6:],0)
        return bytes([0x21,target&255,target>>8])
    if line.startswith('LD A,(#'):
        target=n(line[6:-1],labels)
        return bytes([0x3a,target&255,target>>8])
    if line.startswith('LD A,#'):
        return bytes([0x3e,n(line[5:],labels)])
    if line.startswith('LD (HL),#'):
        return bytes([0x36,n(line[8:],labels)])
    if line.startswith('LD (#') and line.endswith('),A'):
        target=n(line[4:-3],labels)
        return bytes([0x32,target&255,target>>8])
    if line.startswith('LD (#') and line.endswith('),HL'):
        return bytes([0x22,*word(line[4:-4],labels,sizing)])
    if line.startswith('LD A,') and line[5:].isdecimal():
        return bytes([0x3e,n(line[5:],labels)])
    if line in ('LD E,0','LD B,0'):
        return bytes.fromhex('1e 00' if line=='LD E,0' else '06 00')
    if line=="LD A,'?'":return bytes.fromhex('3e 3f')
    if line.startswith(('CP ','OUT (#17),')):
        if line=='OUT (#17),A':return bytes.fromhex('d3 17')
        return bytes([0xfe,n(line[3:],labels)])
    if line.startswith('CALL '):
        target=n(line[5:],labels)
        return bytes([0xcd,target&255,target>>8])
    if line.startswith('JP '):
        cond,target=(line[3:].split(',',1) if ',' in line[3:] else ('',line[3:]))
        value=n(target,labels) if not sizing else labels.get(target,int(target[1:],16) if target.startswith('#') else 0)
        return bytes([0xca if cond=='Z' else 0xc3,value&255,value>>8])
    if line.startswith('DJNZ '):
        target=line[5:];value=labels.get(target,pc+2) if sizing else n(target,labels)
        delta=value-(pc+2)
        if not sizing: assert -128<=delta<=127,(line,delta)
        return bytes([0x10,delta&255])
    if line.startswith('JR '):
        rest=line[3:]
        cond,target=(rest.split(',',1) if ',' in rest else ('',rest))
        opcode={'':0x18,'Z':0x28,'NZ':0x20,'NC':0x30,'C':0x38}[cond]
        value=labels.get(target,pc+2) if sizing else n(target,labels)
        delta=value-(pc+2)
        if not sizing: assert -128<=delta<=127,(line,delta)
        return bytes([opcode,delta&255])
    raise ValueError(f'Unrecognized instruction: {line}')

def word(value,labels,sizing=False):
    v=n(value,labels) if not sizing else labels.get(value, int(value[1:],16) if value.startswith('#') else 0)
    return [v&255,v>>8]

labels={}
pc=START
for line in lines:
    if line.endswith(':'):
        labels[line[:-1]]=pc
    else:
        pc+=len(encode(line,pc,labels,True))
assert labels['page_end']<=LIMIT,(labels['page_end'],LIMIT)

code=bytearray()
pc=START
for line in lines:
    if not line.endswith(':'):
        chunk=encode(line,pc,labels)
        code.extend(chunk)
        pc+=len(chunk)
assert pc==labels['page_end']

result=bytearray(original)
assert original[0x402b-BASE:0x402e-BASE]==bytes.fromhex('c3 da 47')
result[0x402b-BASE:0x402e-BASE]=bytes([0xc3,labels['page_relocate']&255,labels['page_relocate']>>8])
result[START-BASE:START-BASE+len(code)]=code
result[START-BASE+len(code):LIMIT-BASE]=bytes([0])* (LIMIT-START-len(code))
assert result[:0x402b-BASE]==original[:0x402b-BASE]
assert result[0x402e-BASE:START-BASE]==original[0x402e-BASE:START-BASE]
assert result[LIMIT-BASE:]==original[LIMIT-BASE:]
out=Path('MBDEVY9.3')
out.write_bytes(result)
print(f'Original  : {len(original)} bytes, SHA256 {ORIGINAL_SHA256}')
print(f'Replacement: #{START:04X}–#{pc-1:04X}, {len(code)} bytes')
print(f'Startup hook: #402B -> #{labels["page_relocate"]:04X}; destination word #{labels["page_reloc_destination"]:04X}')
print(f'Shared code from #{LIMIT:04X} onward unchanged')
print(f'Output    : {out}, SHA256 {hashlib.sha256(result).hexdigest()}')
