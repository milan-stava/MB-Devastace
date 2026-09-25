"""Run the emitted relocation machine code with a focused Z80 interpreter."""
from pathlib import Path

BASE=0x4000
START=0x4c28
OLD=0x5b00
IMAGE=Path('MBDEVY9.3').read_bytes()
assert len(IMAGE)==7168
SITES=(0x4194,0x45b0,0x45f9,0x47c4,0x47c7,0x47e4,0x4c20,
       0x5bbc,0x5bc7,0x5bd1,0x5bef)
INTERNAL=SITES[7:]
assert IMAGE[0x4c26-BASE:0x4c28-BASE]==bytes.fromhex('00 5b')
assert IMAGE[0x402b-BASE:0x402e-BASE]==bytes.fromhex('c3 28 4c')

def execute(destination):
    m=bytearray(65536)
    m[BASE:BASE+len(IMAGE)]=IMAGE
    m[0x4c26]=destination&255
    m[0x4c27]=destination>>8
    original=bytes(m[OLD:OLD+256])
    def word(addr):return m[addr]|(m[(addr+1)&65535]<<8)
    pc=START
    a=b=c=d=e=h=l=0
    sp=0
    zero=False
    def get():
        nonlocal pc
        x=m[pc];pc+=1;return x
    def getw():return get()|(get()<<8)
    def hl():return h<<8|l
    def set_hl(v):
        nonlocal h,l
        h=(v>>8)&255;l=v&255
    def push(v):
        nonlocal sp
        sp=(sp-1)&65535;m[sp]=(v>>8)&255
        sp=(sp-1)&65535;m[sp]=v&255
    def pop():
        nonlocal sp
        v=word(sp);sp=(sp+2)&65535;return v
    for _ in range(1000):
        op=get()
        if op==0x31:sp=getw()
        elif op==0x21:set_hl(getw())
        elif op==0x22:
            addr=getw();m[addr]=l;m[addr+1]=h
        elif op==0x2a:set_hl(word(getw()))
        elif op==0x01:
            value=getw();b=value>>8;c=value&255
        elif op==0x09:set_hl((hl()+(b<<8|c))&65535)
        elif op==0x44:b=h
        elif op==0x4d:c=l
        elif op==0x78:a=b
        elif op==0xb1:a|=c;zero=a==0
        elif op==0xca:
            addr=getw()
            if zero:
                assert addr==0x47da
                break
        elif op==0x5e:e=m[hl()]
        elif op==0x56:d=m[hl()]
        elif op==0x23:set_hl((hl()+1)&65535)
        elif op==0x2b:set_hl((hl()-1)&65535)
        elif op==0xe5:push(hl())
        elif op==0xe1:set_hl(pop())
        elif op==0xeb:
            v=hl();set_hl(d<<8|e);d=v>>8;e=v&255
        elif op==0x73:m[hl()]=e
        elif op==0x72:m[hl()]=d
        elif op==0x3d:a=(a-1)&255;zero=a==0
        elif op==0x20:
            rel=get()
            if not zero:pc=(pc+(rel if rel<128 else rel-256))&65535
        elif op==0x3e:a=get()
        elif op==0x11:
            value=getw();d=value>>8;e=value&255
        elif op==0xed:
            sub=get()
            if sub==0x5b:
                value=word(getw());d=value>>8;e=value&255
            elif sub==0xb0:
                count=b<<8|c
                for _ in range(count):
                    m[d<<8|e]=m[hl()]
                    set_hl((hl()+1)&65535)
                    value=(d<<8|e)+1;d=(value>>8)&255;e=value&255
                b=c=0
            else:raise AssertionError(('ED',sub))
        elif op==0xc3:
            dest=getw()
            assert dest==0x47da
            break
        else:raise AssertionError((f'{pc-1:04X}',f'{op:02X}'))
    else:raise AssertionError('relocator never returned to monitor')
    assert m[0x402b:0x402e]==bytes.fromhex('c3 da 47')
    if destination==OLD:
        assert bytes(m[BASE:BASE+len(IMAGE)])==(
            IMAGE[:0x402c-BASE]+bytes.fromhex('da 47')+
            IMAGE[0x402e-BASE:])
        return
    expected_block=bytearray(original)
    for site in INTERNAL:
        relative=site-OLD
        before=original[relative]|original[relative+1]<<8
        after=(before+destination-OLD)&65535
        expected_block[relative]=after&255
        expected_block[relative+1]=after>>8
    assert bytes(m[destination:destination+256])==expected_block
    for site in SITES:
        new=(word(site) if site not in INTERNAL else word(destination+site-OLD))
        expected=(IMAGE[site-BASE]|IMAGE[site+1-BASE]<<8)+destination-OLD
        assert new==expected&65535,(hex(site),hex(new),hex(expected&65535))
    assert m[destination:destination+0xba]==original[:0xba]
    assert m[destination+0xba:destination+0xbc]==original[0xba:0xbc]
    assert m[destination+0xfd:destination+0x100]==original[0xfd:]
    assert len(m)==65536

for address in (0x5b00,0x6000,0x8000,0x8123,0xc100):
    execute(address)
print('Relocation machine code: default, page-aligned and arbitrary 16-bit destinations OK; 11 fixups verified')
