#!/usr/bin/env python3
"""
APK v3 - Login patch + attendance endpoint patch.
Uses index.android.bundle.patched2 which contains all 3 patches.
"""
import os, sys, zipfile

BASE = r"C:\Users\user\OneDrive\Masaüstü\project"
ORIGINAL_APK   = os.path.join(BASE, "app_3.4.0.apk")
PATCHED_BUNDLE = os.path.join(BASE, "index.android.bundle.patched2")
OUTPUT_APK     = os.path.join(BASE, "app_patched.apk")
BUNDLE_IN_APK  = "assets/index.android.bundle"

print("=== APK Bundle Replacer (v3 - all patches) ===")

with open(PATCHED_BUNDLE, 'rb') as f:
    patched_data = f.read()
print(f"Patched bundle: {len(patched_data):,} bytes")

# Verify all patches
errors = 0

# Login patch: 0x4FF3BB = 0x03
if patched_data[0x4FF3BB] == 0x03:
    print("✓ Login patch: 0x4FF3BB = 0x03")
else:
    print(f"ERROR: Login patch missing! 0x4FF3BB = 0x{patched_data[0x4FF3BB]:02X}")
    errors += 1

# Attendance endpoint: m1/mtd25/ at 0xF0F92
ctx = patched_data[0xF0F92:0xF0F9B]
if ctx == b'm1/mtd25/':
    print(f"✓ Attendance endpoint patch: {ctx}")
else:
    print(f"ERROR: Endpoint patch missing! Got {ctx}")
    errors += 1

# yoklamaHaftalar -> yoklamaList (4-byte value)
import struct
entry_val = struct.unpack_from('<I', patched_data, 0xA3B34)[0]
if entry_val == 0x0B0AC4CC:
    print(f"✓ yoklamaHaftalar->yoklamaList string table patch: 0x{entry_val:08X}")
else:
    print(f"ERROR: String table patch missing! 0xA3B34 = 0x{entry_val:08X}")
    errors += 1

if errors:
    print(f"\n{errors} patch verification failed!")
    sys.exit(1)

print(f"\nBuilding APK: {OUTPUT_APK}")

with zipfile.ZipFile(ORIGINAL_APK, 'r') as src:
    with zipfile.ZipFile(OUTPUT_APK, 'w') as dst:
        for item in src.infolist():
            if item.filename.startswith('META-INF/'):
                continue  # skip old signatures

            if item.filename == BUNDLE_IN_APK:
                zi = zipfile.ZipInfo(BUNDLE_IN_APK)
                zi.date_time = item.date_time
                zi.compress_type = zipfile.ZIP_STORED
                dst.writestr(zi, patched_data)
                print(f"  ✓ PATCHED (STORED): {BUNDLE_IN_APK}")
            else:
                raw = src.read(item.filename)
                zi = zipfile.ZipInfo(item.filename)
                zi.date_time = item.date_time
                zi.compress_type = item.compress_type
                dst.writestr(zi, raw)

print(f"\n✓ APK built: {OUTPUT_APK}")
print(f"  Size: {os.path.getsize(OUTPUT_APK):,} bytes")

with zipfile.ZipFile(OUTPUT_APK) as z:
    info = z.getinfo(BUNDLE_IN_APK)
    ct = "STORE" if info.compress_type == 0 else f"DEFLATE({info.compress_type})"
    print(f"  Bundle compression: {ct}")
    if info.compress_type != 0:
        print("  ERROR: Must be ZIP_STORED!")
        sys.exit(1)

print("\nNext: sign APK with:")
print(f'  java -jar apksigner.jar sign --ks debug_sign.jks --ks-pass pass:changeit --key-pass pass:changeit --ks-alias debug_key {OUTPUT_APK}')
