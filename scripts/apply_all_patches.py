"""
App Bytecode Patcher - Complete Fix
===========================================
Applies all patches to the ORIGINAL backup bundle:
1. Login navigation fix
2. Endpoint mtd26 → mtd25
3. PropID yoklamaHaftalar → yoklamaList in _fun26882
4. PropID H_NO → TARIH (display text) in _fun26884
5. PropID H_NO → SAAT (React key) in _fun26884
6. yoklamaGunler GetById+NullCheck → NewArray+PutByIndex in _fun26884
7. yoklamaSaatList GetById+NullCheck → NewArray+PutByIndex in _fun26885
"""
import struct, shutil

SRC = 'index.android.bundle.backup'
DST = 'index.android.bundle.patched'

with open(SRC, 'rb') as f:
    data = bytearray(f.read())

print(f"Source: {SRC} ({len(data)} bytes)")

patches = [
    {
        'name': '1. Login navigation fix',
        'offset': 0x4FF3BB,
        'original': bytes([0x4D]),
        'replacement': bytes([0x03]),
    },
    {
        'name': '2. Endpoint mtd26 → mtd25',
        'offset': 0xF0F99,
        'original': bytes([0x36]),  # '6'
        'replacement': bytes([0x35]),  # '5'
    },
    {
        'name': '3. _fun26882: yoklamaHaftalar → yoklamaList propID',
        'offset': 0x521696,  # _fun26882 bc_offset(0x5215E7) + 175 (propID at +4 within GetById)
        'original': bytes([0x7F, 0x62]),  # propID 25215 = yoklamaHaftalar
        'replacement': bytes([0xFE, 0x69]),  # propID 27134 = yoklamaList
    },
    {
        'name': '4. _fun26884: H_NO → TARIH propID (display)',
        'offset': 0x5217A8,  # _fun26884 bc_offset(0x5216AC) + 252
        'original': bytes([0xC5, 0x66]),  # propID 26309 = H_NO
        'replacement': bytes([0x33, 0x44]),  # propID 17459 = TARIH
    },
    {
        'name': '5. _fun26884: H_NO → SAAT propID (React key)',
        'offset': 0x52181A,  # _fun26884 bc_offset(0x5216AC) + 366
        'original': bytes([0xC5, 0x66]),  # propID 26309 = H_NO
        'replacement': bytes([0x83, 0x69]),  # propID 27011 = SAAT
    },
    {
        'name': '6. _fun26884: yoklamaGunler → NewArray[item]',
        'offset': 0x5217EE,  # _fun26884 bc_offset(0x5216AC) + 322
        'original': bytes([
            0x37, 0x09, 0x00, 0x0C, 0x0F, 0x65,  # GetById r9=r0.yoklamaGunler
            0x0E, 0x07, 0x09, 0x06,                # Eq r7=(r9==r6=null)
            0x76, 0x06,                             # LoadConstUndefined r6
            0x90, 0x14, 0x07,                       # JmpTrue +20,r7 → goto 354
        ]),  # 15 bytes
        'replacement': bytes([
            0x07, 0x09, 0x01, 0x00,  # NewArray r9, 1
            0x44, 0x09, 0x00, 0x00,  # PutByIndex r9, r0, 0 → r9=[r0]
            0x76, 0x06,              # LoadConstUndefined r6
            0x76, 0x07,              # LoadConstUndefined r7
            0x90, 0x03, 0x07,        # JmpTrue +3,r7 → NOP (r7=undef, falls through)
        ]),  # 15 bytes
    },
    {
        'name': '7. _fun26885: yoklamaSaatList → NewArray[item]',
        'offset': 0x521A57,  # _fun26885 bc_offset(0x52183B) + 540
        'original': bytes([
            0x37, 0x09, 0x00, 0x10, 0x45, 0x6B,  # GetById r9=r0.yoklamaSaatList
            0x0E, 0x07, 0x09, 0x07,                # Eq r7=(r9==r7=null)
            0x76, 0x06,                             # LoadConstUndefined r6
            0x90, 0x14, 0x07,                       # JmpTrue +20,r7 → goto 572
        ]),  # 15 bytes
        'replacement': bytes([
            0x07, 0x09, 0x01, 0x00,  # NewArray r9, 1
            0x44, 0x09, 0x00, 0x00,  # PutByIndex r9, r0, 0 → r9=[r0]
            0x76, 0x06,              # LoadConstUndefined r6
            0x76, 0x07,              # LoadConstUndefined r7
            0x90, 0x03, 0x07,        # JmpTrue +3,r7 → NOP (r7=undef, falls through)
        ]),  # 15 bytes
    },
]

# Verify and apply each patch
all_ok = True
for p in patches:
    off = p['offset']
    orig = p['original']
    repl = p['replacement']
    actual = bytes(data[off:off+len(orig)])
    
    if actual != orig:
        print(f"  FAIL {p['name']}")
        print(f"    Expected: {orig.hex()}")
        print(f"    Got:      {actual.hex()}")
        all_ok = False
    else:
        print(f"  OK   {p['name']}")

if not all_ok:
    print("\nVerification FAILED! Aborting.")
    exit(1)

# Apply patches
for p in patches:
    off = p['offset']
    repl = p['replacement']
    data[off:off+len(repl)] = repl

with open(DST, 'wb') as f:
    f.write(data)

print(f"\nAll {len(patches)} patches applied successfully!")
print(f"Output: {DST} ({len(data)} bytes)")

# Verify the patched file
print("\nVerification of patched bytes:")
with open(DST, 'rb') as f:
    pdata = f.read()
for p in patches:
    off = p['offset']
    repl = p['replacement']
    actual = bytes(pdata[off:off+len(repl)])
    status = "OK" if actual == repl else "FAIL"
    print(f"  {status} {p['name']}: {actual.hex()}")
