#!/usr/bin/env python3
"""
Patched bundle'ı APK içine yerleştir.
APK = ZIP dosyası. zipfile modülü ile yeni APK oluştur.

NOT: APK'nın imzası bozulacak. İmzasız APK yüklemek için:
- Test cihazı: adb install --no-verify patched.apk
- Rootlu cihaz: adb push + pm install 
- Ya da yeniden imzalama gerekir

ALTERNATIF: APK yerine sadece Frida ile runtime patch.
"""
import os
import sys
import zipfile
import shutil
import io

BASE = r"C:\Users\user\OneDrive\Masaüstü\project"
ORIGINAL_APK = os.path.join(BASE, "app_3.4.0.apk")
PATCHED_BUNDLE = os.path.join(BASE, "index.android.bundle.patched")
OUTPUT_APK = os.path.join(BASE, "app_patched_unsigned.apk")

# Bundle'ın APK içindeki yolu
BUNDLE_PATH_IN_APK = "assets/index.android.bundle"

print("=" * 60)
print("APK Bundle Replacer")
print("=" * 60)
print(f"\nOriginal APK: {ORIGINAL_APK}")
print(f"Patched bundle: {PATCHED_BUNDLE}")
print(f"Output APK: {OUTPUT_APK}")

# Dosya kontrolleri
if not os.path.exists(ORIGINAL_APK):
    print(f"ERROR: APK bulunamadı: {ORIGINAL_APK}")
    sys.exit(1)

if not os.path.exists(PATCHED_BUNDLE):
    print(f"ERROR: Patched bundle bulunamadı: {PATCHED_BUNDLE}")
    sys.exit(1)

# Patched bundle oku
with open(PATCHED_BUNDLE, 'rb') as f:
    patched_bundle_data = f.read()

print(f"\nPatched bundle boyut: {len(patched_bundle_data):,} bytes")

# APK'yı aç ve içeriğini kontrol et
print("\nAPK içeriği aranıyor...")
with zipfile.ZipFile(ORIGINAL_APK, 'r') as apk:
    namelist = apk.namelist()
    
    # Bundle dosyasını bul
    bundle_entry = None
    for name in namelist:
        if 'index.android.bundle' in name:
            print(f"  Bundle bulundu: {name}")
            bundle_entry = name
    
    if not bundle_entry:
        print("  HATA: APK içinde bundle bulunamadı!")
        # Tüm asset dosyalarını listele
        for name in namelist:
            if 'asset' in name.lower():
                print(f"    {name}")
        sys.exit(1)
    
    print(f"\n✓ Bundle path in APK: {bundle_entry}")
    
    # Orijinal bundle boyutunu kontrol et
    info = apk.getinfo(bundle_entry)
    print(f"  Orijinal boyut: {info.file_size:,} bytes")
    print(f"  Compress type: {info.compress_type}")

# Yeni APK oluştur
print(f"\nYeni APK oluşturuluyor: {OUTPUT_APK}")

# Tüm dosyaları kopyala, sadece bundle'ı değiştir
with zipfile.ZipFile(ORIGINAL_APK, 'r') as original:
    with zipfile.ZipFile(OUTPUT_APK, 'w', compression=zipfile.ZIP_DEFLATED) as patched:
        
        total = len(original.namelist())
        for i, name in enumerate(original.namelist()):
            if i % 100 == 0:
                print(f"  [{i}/{total}] {name[:60]}")
            
            # META-INF (imza) dosyalarını atla
            if name.startswith('META-INF/'):
                print(f"  SKIP (imza): {name}")
                continue
            
            if name == bundle_entry:
                # Patched bundle'ı koy
                info = original.getinfo(name)
                # Sıkıştırma kullan
                patched.writestr(name, patched_bundle_data)
                print(f"  ✓ PATCHED: {name}")
            else:
                # Orijinal dosyayı kopyala
                data = original.read(name)
                info = original.getinfo(name)
                # Aynı compression type ile yaz
                patched.writestr(zipfile.ZipInfo(
                    filename=info.filename,
                    date_time=info.date_time
                ), data, info.compress_type)

print(f"\n✓ Patched APK oluşturuldu: {OUTPUT_APK}")
print(f"APK boyut: {os.path.getsize(OUTPUT_APK):,} bytes")

print("""
============================================================
APK YÜKLEME TALİMATLARI (imzasız apk):
============================================================

Android 4.4+ için yeniden imzalama gerekebilir.

YÖNTEM 1: Debug imzalamadan yükle (rootsuz, USB debugging açık):
  adb install -r --no-verify "app_patched_unsigned.apk"
  NOT: --no-verify Android 8+ için gerekiyor

YÖNTEM 2: apksigner ile yeniden imzala (önerilen):
  # keytool ile yeni keystore oluştur:
  keytool -genkey -v -keystore test.jks -alias test -keyalg RSA -keysize 2048 -validity 365
  # zipalign (gerekli):
  zipalign -v 4 app_patched_unsigned.apk app_patched_aligned.apk
  # imzala:
  apksigner sign --ks test.jks --ks-alias test --out app_patched_signed.apk app_patched_aligned.apk
  # yükle:
  adb install -r app_patched_signed.apk

YÖNTEM 3: Rootlu cihazda bundle'ı direkt değiştir:
  adb root
  adb push index.android.bundle.patched /data/app/~~*/com.vendor.studentapp-*/base.apk  
  (veya doğru uygulama data path'i)

YÖNTEM 4: Frida runtime patch (APK değiştirmeden):
  frida -U -f com.vendor.studentapp --no-pause -l frida_bytecode_patch.js
  
  Bu en az invazif yöntem - APK'ya dokunmadan anlık patch uygular.
============================================================
""")
