"""Exercise Y's emitted Z80 bytes with the common number editor modeled.

The editor model follows #463C–#46B9 as disassembled from the original image.
It is not a hardware or full Z80 emulator; the real MB03+ must confirm UI.
"""
from pathlib import Path

image=Path('MBDEVY9.3').read_bytes()
base=0x4000
assert len(image)==7168
assert image[0x5820-base]==ord('>')  # first char in #4618 display

def run(keys, decimal):
    ram=bytearray(image)
    keys=iter(keys)
    pc=0x4c03
    a=hl=0
    zero=False
    written=[]
    shown=[]
    def byte():
        nonlocal pc
        v=ram[pc-base];pc+=1;return v
    for _ in range(50):
        op=byte()
        if op==0x3e:a=byte()
        elif op==0x32:
            addr=byte()|(byte()<<8);ram[addr-base]=a
        elif op==0x21:hl=byte()|(byte()<<8)
        elif op==0xcd:
            addr=byte()|(byte()<<8)
            if addr==0x4258:
                while True:
                    ch=ram[hl-base];hl+=1
                    shown.append(ch&127)
                    if ch&128:break
            elif addr==0x463c:
                entered=[]
                while True:
                    # #4618 reads the > from #5820 and prints reverse C at #FA.
                    assert ram[0x5820-base]==ord('>')
                    ch=next(keys)
                    if ch==0xb0:
                        if entered:entered.pop()
                        continue
                    digit=ch-48 if 48<=ch<=57 else ch-55 if 65<=ch<=70 else -1
                    if digit>=0:
                        if decimal and digit>=10:continue
                        if len(entered)<(4 if decimal else 3):
                            entered.append(ch)
                            continue
                    a=ch
                    ram[0x4620-base]=len(entered)
                    hl=int(bytes(entered).decode(),10 if decimal else 16) if entered else 0
                    ram[0x4023-base]=hl&255
                    ram[0x4024-base]=hl>>8
                    break
            else:raise AssertionError(hex(addr))
        elif op==0xfe:zero=a==byte()
        elif op==0x3a:
            addr=byte()|(byte()<<8);a=ram[addr-base]
        elif op==0xb7:zero=a==0
        elif op==0x7c:a=hl>>8
        elif op==0x7d:a=hl&255
        elif op==0xd3:
            assert byte()==0x17
            written.append(a)
        elif op==0xc0:
            if not zero:break
        elif op==0xc8:
            if zero:break
        elif op==0xc9:break
        else:raise AssertionError((hex(pc-1),hex(op)))
    else:raise AssertionError('Y did not return')
    if written:assert ram[0x5bdd-base]==written[-1]
    assert bytes(shown)==b'Pag'
    return written

for decimal in (False,True):
    for page in range(256):
        digits=f'{page:d}' if decimal else f'{page:X}'
        assert run([*map(ord,digits),13],decimal)==[page]
    for digits in ('','256' if decimal else '100','999' if decimal else 'FFF'):
        assert run([*map(ord,digits),13],decimal)==[]
    assert run([0xb1],decimal)==[]
    assert run([ord('1'),ord('2'),0xb0,ord('3'),13],decimal)==[13 if decimal else 0x13]
    assert run([ord('1'),0xb0,13],decimal)==[]
    assert run([ord('1'),ord('2'),0xb0,0xb0,ord('3'),13],decimal)==[3]
    assert run([ord('!')],decimal)==[]
    assert run([ord('G')],decimal)==[]
    if decimal:assert run([ord('A'),ord('1'),13],decimal)==[1]
    assert run([ord('1'),0xb1],decimal)==[]
print('Y machine bytes and modeled common editor: 256 values, both radices, EDIT, DELETE, range and invalid keys OK')
