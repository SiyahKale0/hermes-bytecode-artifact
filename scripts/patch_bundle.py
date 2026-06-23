#!/usr/bin/env python3
"""
the target app v3.4.0 - index.android.bundle Bytecode Patch
=========================================================

BUG: initUserInformation (_fun25754) case 128:
  if(!r1) { _fun25754_ip = 216; continue }  ← navigation atlanıyor
  
SEBEP: initStudentInformation (_fun25736) success path implicit undefined döndürüyor.
  r1 = undefined → !r1 = true → navigation HEP ATLANIYOR

PATCH:
  Bundle offset: 0x004FF32F + 0x008B = 0x004FF3BA
  Original bytes: 92 4D 01  (JmpFalse addr8=77, r1)
  Patched bytes:  92 03 01  (JmpFalse addr8=3,  r1)
  
  addr8=3 means: "if(!r1) jump to current_ip+3 = next instruction"
  This effectively makes the JmpFalse a NOP - navigation always proceeds!

DOĞRULAMA:
  - ip=0x008b: JmpFalse addr8=77 r1 → jumps to 0xD8 (case 216, skip navigation)
  - Patched: JmpFalse addr8=3 r1  → jumps to 0x8E (case 142, navigation!)
  - 0x8E = case 142: navigation.dispatch(StackActions.replace(STUDENT_TABS_ROOT))

KULLANIM:
  python patch_bundle.py
  
  Creates: index.android.bundle.patched
  Then replace: index.android.bundle with the patched version
  Then rebuild APK or push to device.
"""

import os
import sys
import struct
import shutil
import io

BASE = r"C:\Users\user\OneDrive\Masaüstü\project"
BUNDLE_FILE = os.path.join(BASE, "app_decompiled", "resources", "assets", "index.android.bundle")
PATCHED_FILE = os.path.join(BASE, "index.android.bundle.patched")
BACKUP_FILE = os.path.join(BASE, "index.android.bundle.backup")

# Patch constants
FUNC_BUNDLE_OFFSET = 0x004FF32F     # _fun25754 start in bundle
INSTR_FUNC_OFFSET = 0x008B          # JmpFalse instruction offset within function
PATCH_ABS_OFFSET = FUNC_BUNDLE_OFFSET + INSTR_FUNC_OFFSET  # 0x004FF3BA

ORIGINAL_BYTES = bytes([0x92, 0x4D, 0x01])   # JmpFalse addr8=77, r1
PATCHED_BYTES  = bytes([0x92, 0x03, 0x01])   # JmpFalse addr8=3,  r1 (= NOP effect)

print("=" * 60)
print("the target app v3.4.0 - Bundle Patcher")
print("=" * 60)
print(f"\nBundle: {BUNDLE_FILE}")
print(f"Patch offset: {PATCH_ABS_OFFSET:#010x} ({PATCH_ABS_OFFSET})")
print(f"Original:     {ORIGINAL_BYTES.hex()}")
print(f"Patched:      {PATCHED_BYTES.hex()}")

# Verify
if not os.path.exists(BUNDLE_FILE):
    print(f"\nERROR: Bundle dosyası bulunamadı: {BUNDLE_FILE}")
    sys.exit(1)

with open(BUNDLE_FILE, 'rb') as f:
    data = bytearray(f.read())

print(f"\nBundle boyut: {len(data):,} bytes")

# Sanity checks
if PATCH_ABS_OFFSET + 3 > len(data):
    print(f"ERROR: Patch offset dosya sınırlarının dışında!")
    sys.exit(1)

# Check magic
if data[:4] != bytes([0xC6, 0x1F, 0xBC, 0x03]):
    print(f"ERROR: Geçersiz Hermes magic! {data[:4].hex()}")
    sys.exit(1)

# Verify original bytes
actual_bytes = bytes(data[PATCH_ABS_OFFSET:PATCH_ABS_OFFSET+3])
print(f"\nOffset {PATCH_ABS_OFFSET:#x} mevcut bytes: {actual_bytes.hex()}")

if actual_bytes == ORIGINAL_BYTES:
    print("✓ Original bytes doğrulandı - patch uygulanabilir")
elif actual_bytes == PATCHED_BYTES:
    print("! Patch zaten uygulanmış!")
    sys.exit(0)
else:
    print(f"! UYARI: Beklenen {ORIGINAL_BYTES.hex()} ama {actual_bytes.hex()} bulundu")
    print("Bundle farklı bir versiyona ait olabilir. Devam etmek için 'yes' yazın:")
    if input().strip().lower() != 'yes':
        sys.exit(1)

# Context verification (extra safety)
# ip=0x80-0x90 context: LoadFromEnvironment + LoadConstFalse + Call2 + JmpFalse
expected_context = bytes([
    0x2e, 0x06, 0x0b, 0x0d,   # ip=0x80: LoadFromEnvironment r6, r11, 13
    0x79, 0x05,                # ip=0x84: LoadConstFalse r5
    0x53, 0x05, 0x06, 0x0c, 0x05,  # ip=0x86: Call2 r5, r6, r12, r5
    0x92, 0x4d, 0x01           # ip=0x8b: JmpFalse 77, r1
])

context_start = FUNC_BUNDLE_OFFSET + 0x80
actual_context = bytes(data[context_start:context_start+len(expected_context)])

if actual_context == expected_context:
    print("✓ Bağlam (context) doğrulandı - güvenli patch")
else:
    print(f"\nUYARI: Beklenen context:")
    print(f"  {expected_context.hex()}")
    print(f"Gerçek context:")
    print(f"  {actual_context.hex()}")
    print("Context eşleşmiyor!")

    # Bireysel kontrol
    jmpfalse_only = bytes(data[PATCH_ABS_OFFSET:PATCH_ABS_OFFSET+3])
    if jmpfalse_only == ORIGINAL_BYTES:
        print("Ama JmpFalse bytes doğru - devam ediyorum...")
    else:
        print("JmpFalse bytes de yanlış - DurDurDur!")
        sys.exit(1)

# Backup oluştur
print(f"\nBackup oluşturuluyor: {BACKUP_FILE}")
shutil.copy2(BUNDLE_FILE, BACKUP_FILE)
print("✓ Backup oluşturuldu")

# Patch uygula
print(f"\nPatch uygulanıyor...")
data[PATCH_ABS_OFFSET:PATCH_ABS_OFFSET+3] = PATCHED_BYTES

# Patched dosya yaz
print(f"Patched dosya yazılıyor: {PATCHED_FILE}")
with open(PATCHED_FILE, 'wb') as f:
    f.write(data)

print(f"✓ Patch tamamlandı!")
print(f"\nPatched bundle: {PATCHED_FILE}")
print(f"Backup:         {BACKUP_FILE}")

# Final verification
with open(PATCHED_FILE, 'rb') as f:
    verify_data = f.read()

verify_bytes = verify_data[PATCH_ABS_OFFSET:PATCH_ABS_OFFSET+3]
if bytes(verify_bytes) == PATCHED_BYTES:
    print(f"\n✓ Doğrulama başarılı: {verify_bytes.hex()}")
else:
    print(f"\n✗ Doğrulama başarısız: {verify_bytes.hex()} != {PATCHED_BYTES.hex()}")

print("\n" + "=" * 60)
print("SONRAKI ADIMLAR:")
print("=" * 60)
print("""
1. Patched bundle'ı APK'ya yerleştir:
   
   a) Orijinal APK'yı kopyala:
      copy "app_3.4.0.apk" "app_patched.apk"

   b) Bundle'ı APK içine koy:
      python replace_in_apk.py   (aşağıda oluşturulacak)

2. Veya sadece bundle push (ADB ile rootlu cihazda):
      adb push index.android.bundle.patched /data/data/com.vendor.studentapp/files/
      (veya doğru assets path'i)

3. Frida ile runtime patch (önerilir - APK rebuild gerekmez):
      frida -U -f com.vendor.studentapp --no-pause -l frida_bytecode_patch.js

4. Test:
   - Loglarda "Navigation trigger!" görmeli
   - Doğru şifre ile giriş → direkt StudentTabs ekranına geçmeli
""")
