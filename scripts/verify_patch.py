#!/usr/bin/env python3
"""
Patched bundle'ı doğrula.
ip=0x8b'deki JmpFalse instruction'ının addr8=3 olduğunu kontrol et.
Original disassembly ile karşılaştır.
"""
import sys
import os
import io

BASE = r"C:\Users\user\OneDrive\Masaüstü\project"
ORIGINAL_BUNDLE = os.path.join(BASE, "app_decompiled", "resources", "assets", "index.android.bundle")
PATCHED_BUNDLE = os.path.join(BASE, "index.android.bundle.patched")

sys.path.insert(0, r"C:\Users\user\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages")

from hermes_dec.parsers.hbc_file_parser import HBCReader
from hermes_dec.parsers.hbc_bytecode_parser import parse_hbc_bytecode

def analyze_bundle(bundle_file, label):
    print(f"\n=== {label} ===")
    with open(bundle_file, 'rb') as f:
        data = f.read()
    
    reader = HBCReader()
    buf = io.BytesIO(data)
    reader.read_whole_file(buf)
    
    fh = reader.function_headers[25754]
    instructions = list(parse_hbc_bytecode(fh, reader))
    
    # ip=0x8b'deki instruction
    for instr in instructions:
        if instr.original_pos == 0x8b:
            func_offset = fh.offset
            abs_offset = func_offset + 0x8b
            
            # Raw bytes
            raw = data[abs_offset:abs_offset+3]
            
            print(f"  ip=0x8b (abs={abs_offset:#x}):")
            print(f"    Raw bytes: {raw.hex()}")
            
            inst = instr.inst
            print(f"    Opcode: {inst.name}")
            
            # Operands
            try:
                for op in inst.operands:
                    meaning_str = str(op.meaning)
                    print(f"    Operand: {meaning_str} = {op.val}")
            except:
                pass
            
            # Yorumlama
            if raw[0] == 0x92:  # JmpFalse
                addr8 = raw[1]
                reg = raw[2]
                target = instr.original_pos + addr8
                print(f"    Interpretation: JmpFalse addr8={addr8} r{reg} → jump to {target:#x}")
                
                if addr8 == 0x4d:  # 77
                    print(f"    STATUS: ORIGINAL (bug mevcut - navigation atlanıyor!)")
                elif addr8 == 0x03:  # 3
                    print(f"    STATUS: PATCHED ✓ (jump to next instruction - navigation ÇALIŞIYOR!)")
                else:
                    print(f"    STATUS: UNEXPECTED addr8={addr8:#x}")
            break
    else:
        print(f"  ip=0x8b bulunamadı!")

analyze_bundle(ORIGINAL_BUNDLE, "Original Bundle")
analyze_bundle(PATCHED_BUNDLE, "Patched Bundle")

print("\n=== ÖZET ===")
print("""
PATCH AÇIKLAMASI:
  - Fonksiyon: _fun25754 (initUserInformation)
  - Bundle offset: 0x004FF3BA
  - Değişiklik: JmpFalse addr8=0x4D → JmpFalse addr8=0x03
  
  ÖNCE: case 128: if(!r1) { goto case 216 }  ← navigation atlanıyordu
  SONRA: case 128: if(!r1) { goto case 142 }  ← navigation ÇALIŞIYOR!
  
  addr8=0x03 = jump to ip+3 = next instruction (case 142)
  case 142 = navigation.dispatch(StackActions.replace(STUDENT_TABS_ROOT))
  
  Bu patch hem:
  - getStudentProfile başarılı olduğunda (r1=undefined)
  - getStudentProfile başarısız olduğunda (r1=false)
  
  Her iki durumda da artık navigasyon çalışacak.
  
  NOT: getStudentProfile başarısız olursa (Stat=false):
  - dispatch(changeUser(null)) zaten çağrılmış olur (case 285)
  - Ama navigation token'sız çalışmaya çalışacak → muhtemelen auth error
  - Bu normal davranış: token geçersizse app logout logic tetikler
""")
