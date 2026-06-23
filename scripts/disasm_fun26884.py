import struct

with open('index.android.bundle.patched', 'rb') as f:
    data = bytearray(f.read())

# Hermes v96 opcode sizes (opcode byte + operands)
# Format: op -> (name, [operand_sizes_in_bytes])
# Operand types: r8=1, u8=1, i8=1, u16=2, i16=2, u32=4, i32=4, f64=8, addr8=1(signed), addr32=4(signed)
OPCODES = {
    0x00: ('Unreachable', []),
    0x01: ('NewEnvironment', [1, 1]),
    0x02: ('NewEnvironmentWithBuffer', [1, 2, 2]),
    0x03: ('CreateEnvironment', [1]),
    0x04: ('CreateClosure', [1, 1, 2]),
    0x05: ('CreateClosureLongIndex', [1, 1, 4]),
    0x06: ('CreateGeneratorClosure', [1, 1, 2]),
    0x07: ('CreateGeneratorClosureLongIndex', [1, 1, 4]),
    0x08: ('CreateAsyncClosure', [1, 1, 2]),
    0x09: ('CreateAsyncClosureLongIndex', [1, 1, 4]),
    0x0A: ('Mov', [1, 1]),
    0x0B: ('MovLong', [1, 4]),
    0x0C: ('LoadParam', [1, 1]),
    0x0D: ('LoadParamLong', [1, 4]),
    0x0E: ('LoadConstUInt8', [1, 1]),
    0x0F: ('LoadConstInt', [1, 4]),
    0x10: ('LoadConstDouble', [1, 8]),
    0x11: ('LoadConstBigInt', [1, 2]),
    0x12: ('LoadConstBigIntLongIndex', [1, 4]),
    0x13: ('LoadConstString', [1, 2]),
    0x14: ('LoadConstStringLongIndex', [1, 4]),
    0x15: ('LoadConstEmpty', [1]),
    0x16: ('LoadConstUndefined', [1]),
    0x17: ('LoadConstNull', [1]),
    0x18: ('LoadConstTrue', [1]),
    0x19: ('LoadConstFalse', [1]),
    0x1A: ('LoadConstZero', [1]),
    0x1B: ('CoerceBoolToBool', [1]),
    0x1C: ('TypeOf', [1, 1]),
    0x1D: ('ToNumber', [1, 1]),
    0x1E: ('ToNumeric', [1, 1]),
    0x1F: ('ToInt32', [1, 1]),
    0x20: ('AddEmptyString', [1, 1]),
    0x21: ('Sub_n', [1, 1, 1]),
    0x22: ('Mul_n', [1, 1, 1]),
    0x23: ('Div_n', [1, 1, 1]),
    0x24: ('Mod', [1, 1, 1]),
    0x25: ('Sub', [1, 1, 1]),
    0x26: ('Mul', [1, 1, 1]),
    0x27: ('Div', [1, 1, 1]),
    0x28: ('Mod2', [1, 1, 1]),
    0x29: ('IsIn', [1, 1, 1]),
    0x2A: ('InstanceOf', [1, 1, 1]),
    0x2B: ('Add', [1, 1, 1]),
    0x2C: ('BitAnd', [1, 1, 1]),
    0x2D: ('BitOr', [1, 1, 1]),
    0x2E: ('GetById', [1, 1, 1, 2]),      # dest, obj, cacheIdx, propID(u16)
    0x2F: ('GetByIdLong', [1, 1, 1, 4]),  # dest, obj, cacheIdx, propID(u32)
    0x30: ('TryGetById', [1, 1, 1, 2]),
    0x31: ('TryGetByIdLong', [1, 1, 1, 4]),
    0x32: ('PutById', [1, 1, 1, 2]),
    0x33: ('PutByIdLong', [1, 1, 1, 4]),
    0x34: ('TryPutById', [1, 1, 1, 2]),
    0x35: ('TryPutByIdLong', [1, 1, 1, 4]),
    0x36: ('PutNewOwnByIdShort', [1, 1, 1]),  # might be GetByVal
    0x37: ('PutNewOwnById', [1, 1, 2]),
    0x38: ('PutNewOwnByIdLong', [1, 1, 4]),
    0x39: ('PutNewOwnNEById', [1, 1, 2]),
    0x3A: ('PutNewOwnNEByIdLong', [1, 1, 4]),
    0x3B: ('PutByVal', [1, 1, 1]),
    0x3C: ('DelByVal', [1, 1, 1]),
    0x3D: ('PutOwnByIndex', [1, 1, 1]),
    0x3E: ('PutOwnByIndexL', [1, 1, 4]),
    0x3F: ('getByVal', [1, 1, 1]),
    0x40: ('GetPNameList', [1, 1, 1, 1]),
    0x41: ('GetNextPName', [1, 1, 1, 1, 1]),
    0x42: ('Call', [1, 1, 1]),
    0x43: ('Construct', [1, 1, 1]),
    0x44: ('Call1', [1, 1, 1]),
    0x45: ('CallDirect', [1, 1, 2]),
    0x46: ('Call2', [1, 1, 1, 1]),
    0x47: ('Call3', [1, 1, 1, 1, 1]),
    0x48: ('Call4', [1, 1, 1, 1, 1, 1]),
    0x49: ('CallLong', [1, 1, 1]),
    0x4A: ('CallDirectLong', [1, 1, 4]),
    0x4B: ('CallBuiltin', [1, 1, 1]),
    0x4C: ('CallBuiltinLong', [1, 1, 2]),
    0x4D: ('Ret', [1]),
    0x4E: ('Catch', [1]),
    0x4F: ('Throw', [1]),
    0x50: ('ThrowIfEmpty', [1, 1]),
    0x51: ('Debugger', []),
    0x52: ('AsyncBreakCheck', []),
    0x53: ('ProfilePoint', [2]),
    0x54: ('GetGlobalObject', [1]),
    0x55: ('GetNewTarget', [1]),
    0x56: ('CreateThis', [1, 1, 1]),
    0x57: ('SelectObject', [1, 1, 1]),
    0x58: ('LoadThisNS', [1]),
    0x59: ('CoerceThisNS', [1, 1]),
    0x5A: ('LoadParam', [1, 1]),   # alias?
    0x5B: ('IsUndefined', [1, 1]),
    0x5C: ('IsNull', [1, 1]),
    0x5D: ('IsBoolean', [1, 1]),
    0x5E: ('IsNumber', [1, 1]),
    0x5F: ('IsObject', [1, 1]),
    0x60: ('IsString', [1, 1]),
    0x61: ('Not', [1, 1]),
    0x62: ('Negate', [1, 1]),
    0x63: ('BitNot', [1, 1]),
    0x64: ('Inc', [1, 1]),
    0x65: ('Dec', [1, 1]),
    0x66: ('Add_n', [1, 1, 1]),
    0x67: ('Sub_n2', [1, 1, 1]),
    0x68: ('Mul_n2', [1, 1, 1]),
    0x69: ('Div_n2', [1, 1, 1]),
    0x6A: ('GetEnvironment', [1, 1]),
    0x6B: ('StoreNPToEnvironment', [1, 1, 1]),
    0x6C: ('StoreToEnvironment', [1, 1, 1]),
    0x6D: ('StoreNPToEnvironmentL', [1, 4, 1]),
    0x6E: ('LoadFromEnvironment', [1, 1, 1]),
    0x6F: ('LoadFromEnvironmentL', [1, 1, 4]),
    0x70: ('JmpTrue_Long_MAYBE', [1, 4]),
    0x71: ('StoreToEnvironmentFBL', [1, 1, 4]),
    0x72: ('LoadFromEnvironmentFB', [1, 1, 1]),
    0x73: ('LoadFromEnvironmentFBL', [1, 1, 4]),
    0x74: ('NewObject', [1]),
    0x75: ('NewObjectWithBuffer', [1, 2, 2]),
    0x76: ('NewObjectWithBufferLong', [1, 2, 4]),
    0x77: ('NewArray', [1, 2]),
    0x78: ('NewArrayWithBuffer', [1, 2, 2, 2]),
    0x79: ('NewArrayWithBufferLong', [1, 2, 2, 4]),
    0x7A: ('CreateRegExp', [1, 2, 2, 4]),
    0x7B: ('SwitchImm', [1, 4, 4, 4, 4]),
    0x7C: ('StrictEq', [1, 1, 1]),
    0x7D: ('StrictNeq', [1, 1, 1]),
    0x7E: ('Eq', [1, 1, 1]),
    0x7F: ('Neq', [1, 1, 1]),
    0x80: ('Less', [1, 1, 1]),
    0x81: ('LessEq', [1, 1, 1]),
    0x82: ('Greater', [1, 1, 1]),
    0x83: ('GreaterEq', [1, 1, 1]),
    0x84: ('Add32', [1, 1, 1]),
    0x85: ('Sub32', [1, 1, 1]),
    0x86: ('Mul32', [1, 1, 1]),
    0x87: ('Div32', [1, 1, 1]),
    0x88: ('Lshift32', [1, 1, 1]),
    0x89: ('Rshift32', [1, 1, 1]),
    0x8A: ('Urshift32', [1, 1, 1]),
    0x8B: ('JNotEqual_Long', [4, 1, 1]),
    0x8C: ('JEqual_Long', [4, 1, 1]),
    0x8D: ('JStrictNotEqual_Long', [4, 1, 1]),
    0x8E: ('JStrictEqual_Long', [4, 1, 1]),
    0x8F: ('JLess_Long', [4, 1, 1]),
    0x90: ('JLessN_Long', [4, 1, 1]),
    0x91: ('JLessEqual_Long', [4, 1, 1]),
    0x92: ('JLessEqualN_Long', [4, 1, 1]),
    0x93: ('JGreater_Long', [4, 1, 1]),
    0x94: ('JGreaterN_Long', [4, 1, 1]),
    0x95: ('JGreaterEqual_Long', [4, 1, 1]),
    0x96: ('JGreaterEqualN_Long', [4, 1, 1]),
    0x97: ('JmpLong', [4]),           # unconditional long jump
    0x98: ('JmpTrueLong', [4, 1]),    # long jump if true
    0x99: ('JmpFalseLong', [4, 1]),   # long jump if false
    0x9A: ('JmpUndefinedLong', [4, 1]),
    0x9B: ('SaveGenerator', [4]),
    0x9C: ('StartGenerator', []),
    0x9D: ('ResumeGenerator', [1, 1]),
    0x9E: ('CompleteGenerator', []),
    0x9F: ('CreateGenerator', [1, 1, 2]),
    0xA0: ('IteratorBegin', [1, 1]),
    0xA1: ('IteratorNext', [1, 1, 1]),
    0xA2: ('IteratorClose', [1, 1]),
    0xA3: ('Jmp', [1]),              # short unconditional jump (signed)
    0xA4: ('JmpTrue', [1, 1]),       # short jump if true
    0xA5: ('JmpFalse', [1, 1]),      # short jump if false
    0xA6: ('JmpUndefined', [1, 1]),  # short jump if undefined
    0xA7: ('JNotEqual', [1, 1, 1]),
    0xA8: ('JEqual', [1, 1, 1]),
    0xA9: ('JStrictNotEqual', [1, 1, 1]),
    0xAA: ('JStrictEqual', [1, 1, 1]),
    0xAB: ('JLess', [1, 1, 1]),
    0xAC: ('JLessN', [1, 1, 1]),
    0xAD: ('JLessEqual', [1, 1, 1]),
    0xAE: ('JLessEqualN', [1, 1, 1]),
    0xAF: ('JGreater', [1, 1, 1]),
    0xB0: ('JGreaterN', [1, 1, 1]),
    0xB1: ('JGreaterEqual', [1, 1, 1]),
    0xB2: ('JGreaterEqualN', [1, 1, 1]),
    0xB3: ('JEqual_Short', [1, 1, 1]),  # might differ
    0xB4: ('JLess_Short', [1, 1, 1]),
    0xB5: ('JLessEqual_Short', [1, 1, 1]),
    0xB6: ('JGreater_Short', [1, 1, 1]),
    0xB7: ('JGreaterEqual_Short', [1, 1, 1]),
    0xB8: ('DirectEval', [1, 1, 1]),
    0xB9: ('Call1', [1, 1, 1]),  # check
    0xBA: ('DelById', [1, 1, 2]),
    0xBB: ('DelByIdLong', [1, 1, 4]),
    0xBC: ('CreateClosure2', [1, 1, 2]),
    0xBD: ('CreateClosureLongIndex2', [1, 1, 4]),
    0xBE: ('CreateGeneratorClosure2', [1, 1, 2]),
    0xBF: ('CreateGeneratorClosureLongIndex2', [1, 1, 4]),
}

def disasm(data, start, size, label=""):
    bc = data[start:start+size]
    print(f'--- {label} bytecode @ 0x{start:X}, {size} bytes ---')
    print('Raw hex:', bc.hex())
    print()
    
    pos = 0
    while pos < len(bc):
        op = bc[pos]
        op_info = OPCODES.get(op, None)
        
        if op_info is None:
            print(f'  0x{pos:03X} (file:0x{start+pos:X}): {op:02X} = UNKNOWN_OP')
            pos += 1
            continue
        
        name, operands = op_info
        p = pos + 1
        vals = []
        
        try:
            for sz in operands:
                if sz == 1:
                    vals.append(bc[p])
                    p += 1
                elif sz == 2:
                    vals.append(struct.unpack_from('<H', bc, p)[0])
                    p += 2
                elif sz == 4:
                    vals.append(struct.unpack_from('<i', bc, p)[0])  # signed for jumps
                    p += 4
                elif sz == 8:
                    vals.append(struct.unpack_from('<d', bc, p)[0])
                    p += 8
        except Exception as e:
            print(f'  0x{pos:03X}: parse error: {e}')
            break
        
        raw = bc[pos:p].hex()
        vals_str = ', '.join(str(v) for v in vals)
        
        # Annotate jumps
        annot = ''
        if 'Jmp' in name or name.startswith('J'):
            if vals:
                # First operand is usually the jump offset (relative to next instruction)
                # For short jumps: offset is signed byte from instruction start or after
                joff = vals[0]
                if isinstance(joff, int):
                    # relative to current instruction
                    target = pos + joff
                    annot = f' -> case/pos 0x{target:03X}'
        
        print(f'  0x{pos:03X} (file:0x{start+pos:X}): {raw:20s}  {name}({vals_str}){annot}')
        pos = p

print("=== _fun26884 ===")
disasm(data, 0x5216AC, 399, "_fun26884")
