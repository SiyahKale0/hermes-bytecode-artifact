import struct

with open('index.android.bundle.patched', 'rb') as f:
    data = bytearray(f.read())

bc_start = 0x5215E7
bc = bytes(data[bc_start:bc_start+197])

print('Case 171 bytes (offset 0xAB = 171):')
print('Bytes 0xA8 to 0xBC:', bc[0xA8:0xBC].hex())
print()

# Bytes at case 171: 37 03 05 08 7F 62
# If GetById: op=0x37, dst=0x03, obj=0x05, cacheIdx=0x08, propID(2)=0x627F
prop1 = struct.unpack_from('<H', bc, 0xAF)[0]
print(f'Candidate propID at +4 (0xAF): {prop1} = 0x{prop1:X}')

# Or: if opcode=GetById starts at case 171 offset 0xAB
# and format is op(1)+dst(1)+obj(1)+cacheIdx(1)+propID(2) = total 6 bytes
# case 171 = start of instruction? 
# decompiled: r3 = r5.yoklamaHaftalar
# registers: r3=03, r5=05 -> GetById(0x37?, r3=03, r5=05, cache=08, propID=0x627F)
prop_case171 = struct.unpack_from('<H', bc, 0xAB + 4)[0]
print(f'propID if instr starts at 171: {prop_case171} = 0x{prop_case171:X}')

print()
# Verify string table:
# entry for ID X @ 0x91BB0 + X*4
# entry = (isUTF16<<31) | (storageOffset<<8) | length
#    OR: (storageOffset<<8) | length   (no UTF16 bit)
# We know yoklamaList: ID 37211, entry = 0x0B0AC4CC
# length=204? that's wrong for 'yoklamaList' (11 chars)

# Let me re-examine the format more carefully
# From previous: ID 37211 entry = 0x0B0AC4CC
val = 0x0B0AC4CC
print(f'yoklamaList entry 0x{val:08X}:')
print(f'  top byte: 0x{val>>24:02X}')
print(f'  bits[31:23] = {val>>23}')
print(f'  bits[22:0] = 0x{val & 0x7FFFFF:X}')
# Try: isUTF16(1) | length(7) | offset(24)  -- Hermes small string table
is_utf16 = (val >> 31) & 1
# Different format: [length:7][isUTF16:1][offset:24]?
length_try = (val >> 25) & 0x7F
offset_try = val & 0x1FFFFFF
print(f'  if length=bits[31:25]: {length_try}, offset=bits[24:0]: 0x{offset_try:X}')
storage_start = 0xC389C
print(f'  storage @ file 0x{storage_start + offset_try:X}: {repr(bytes(data[storage_start+offset_try:storage_start+offset_try+length_try]))}')

print()
# Let me try another format - hermes string table Small String Entry
# struct SmallStringTableEntry {
#   uint32_t offset : 23;
#   uint32_t length : 8;
#   uint32_t isUTF16 : 1;
# };
# Total:  [isUTF16:1][length:8][offset:23]
val2 = 0x0B0AC4CC  # big endian stored? No, it's little-endian in file
is_utf16_2 = (val2 >> 31) & 1
length_2 = (val2 >> 23) & 0xFF
offset_2 = val2 & 0x7FFFFF
print(f'SmallStringTableEntry format: isUTF16={is_utf16_2}, length={length_2}, offset=0x{offset_2:X}')
print(f'  storage @ file 0x{storage_start + offset_2:X}: {repr(bytes(data[storage_start+offset_2:storage_start+offset_2+length_2]))}')

print()
# Current string table entry for ID 18401
entry_off = 0x91BB0 + 18401 * 4
entry_val = struct.unpack_from('<I', data, entry_off)[0]
print(f'String ID 18401 entry @ file 0x{entry_off:X}: 0x{entry_val:08X}')
is_utf16_3 = (entry_val >> 31) & 1  
length_3 = (entry_val >> 23) & 0xFF
offset_3 = entry_val & 0x7FFFFF
print(f'  isUTF16={is_utf16_3}, length={length_3}, offset=0x{offset_3:X}')
if offset_3 + length_3 < 0x200000:
    print(f'  storage @ file 0x{storage_start + offset_3:X}: {repr(bytes(data[storage_start+offset_3:storage_start+offset_3+length_3]))}')

print()
# Also check what prop the GetById at case 171 is using
# We need to verify if propID in bytecode = 18401
# and check what the bytecode opcode at case 171 looks like
# Let's look at surrounding bytecodes more broadly
print('Full bytecode of _fun26882:')
for i in range(0, 197):
    print(f'  {i:3d} (0x{i:02X}): {bc[i]:02X}', end='')
    if (i+1) % 16 == 0:
        print()
    else:
        print(' ', end='')
print()
