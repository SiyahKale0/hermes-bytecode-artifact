import struct

with open('index.android.bundle.patched', 'rb') as f:
    data = bytearray(f.read())

# Function header size = 16 bytes
# Format:
#   word[0]: bits[31:25]=paramCount, bits[24:0]=bytecodeOffset  
#   word[1]: bits[14:0]=bytecodeSizeInBytes, bits[31:15]=other stuff
#   word[2]: ...
#   word[3]: ...

HEADER_SIZE = 16

def get_fun_info(fun_idx):
    header_off = 0x80 + fun_idx * HEADER_SIZE
    h = data[header_off:header_off+HEADER_SIZE]
    w = [struct.unpack_from('<I', h, i*4)[0] for i in range(4)]
    paramC = w[0] >> 25
    bcOff = w[0] & 0x1FFFFFF
    bcSize = w[1] & 0x7FFF
    return header_off, bcOff, paramC, bcSize, w

print('Function info for yoklama-related functions:')
for fun_idx in [26879, 26880, 26881, 26882, 26883, 26884, 26885, 26886]:
    header_off, bcOff, paramC, bcSize, w = get_fun_info(fun_idx)
    print(f'  _fun{fun_idx}: header@0x{header_off:X}, bc@0x{bcOff:X}, paramCount={paramC}, size={bcSize}')
    print(f'    words: {[hex(x) for x in w]}')
