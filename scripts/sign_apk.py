#!/usr/bin/env python3
"""
Patched APK'yı imzala ve yüklemeye hazır hale getir.
Android SDK build-tools kullanarak:
1. keytool ile debug keystore oluştur
2. zipalign ile hizala
3. apksigner ile imzala
"""
import os
import sys
import subprocess

BASE = r"C:\Users\user\OneDrive\Masaüstü\project"

# Android SDK paths
BUILD_TOOLS = r"C:\Users\user\AppData\Local\Android\Sdk\build-tools\36.0.0"
APKSIGNER = os.path.join(BUILD_TOOLS, "apksigner.bat")
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign.exe")

# Dosyalar
PATCHED_UNSIGNED = os.path.join(BASE, "app_patched_unsigned.apk")
PATCHED_ALIGNED  = os.path.join(BASE, "app_patched_aligned.apk")
PATCHED_SIGNED   = os.path.join(BASE, "app_patched_signed.apk")
DEBUG_KEYSTORE   = os.path.join(BASE, "debug_sign.jks")

print("=" * 60)
print("APK İmzalama ve Hizalama")
print("=" * 60)

# Build tools kontrol
if not os.path.exists(APKSIGNER):
    print(f"HATA: apksigner bulunamadı: {APKSIGNER}")
    sys.exit(1)
if not os.path.exists(ZIPALIGN):
    print(f"HATA: zipalign bulunamadı: {ZIPALIGN}")
    sys.exit(1)

print(f"✓ apksigner: {APKSIGNER}")
print(f"✓ zipalign: {ZIPALIGN}")

# Step 1: Debug keystore oluştur
if not os.path.exists(DEBUG_KEYSTORE):
    print("\n[1] Debug keystore oluşturuluyor...")
    result = subprocess.run([
        "keytool", "-genkey", "-v",
        "-keystore", DEBUG_KEYSTORE,
        "-alias", "debug_key",
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "365",
        "-dname", "CN=Debug, OU=Debug, O=Debug, L=Debug, ST=Debug, C=TR",
        "-storepass", "changeit",
        "-keypass", "changeit",
        "-storetype", "JKS"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Keystore oluşturuldu")
    else:
        print(f"HATA: {result.stderr}")
        # Devam etmeye çalış
else:
    print(f"\n[1] Mevcut keystore kullanılıyor: {DEBUG_KEYSTORE}")

# Step 2: Zipalign
print("\n[2] Zipalign uygulanıyor...")
if os.path.exists(PATCHED_ALIGNED):
    os.remove(PATCHED_ALIGNED)

result = subprocess.run([
    ZIPALIGN, "-v", "4",
    PATCHED_UNSIGNED,
    PATCHED_ALIGNED
], capture_output=True, text=True)

print("stdout:", result.stdout[:200] if result.stdout else "(boş)")
print("stderr:", result.stderr[:200] if result.stderr else "(boş)")

if result.returncode == 0 or os.path.exists(PATCHED_ALIGNED):
    print(f"✓ Aligned APK: {PATCHED_ALIGNED}")
    print(f"  Boyut: {os.path.getsize(PATCHED_ALIGNED):,} bytes")
else:
    print(f"HATA: zipalign başarısız (rc={result.returncode})")
    print("Aligned olmadan imzalamayı deniyorum...")
    import shutil
    shutil.copy2(PATCHED_UNSIGNED, PATCHED_ALIGNED)

# Step 3: apksigner
print("\n[3] APK imzalanıyor...")
if os.path.exists(PATCHED_SIGNED):
    os.remove(PATCHED_SIGNED)

result = subprocess.run([
    APKSIGNER, "sign",
    "--ks", DEBUG_KEYSTORE,
    "--ks-alias", "debug_key",
    "--ks-pass", "pass:changeit",
    "--key-pass", "pass:changeit",
    "--out", PATCHED_SIGNED,
    PATCHED_ALIGNED
], capture_output=True, text=True)

print("stdout:", result.stdout[:500] if result.stdout else "(boş)")
print("stderr:", result.stderr[:500] if result.stderr else "(boş)")

if os.path.exists(PATCHED_SIGNED):
    size = os.path.getsize(PATCHED_SIGNED)
    print(f"\n✓ İmzalı APK oluşturuldu: {PATCHED_SIGNED}")
    print(f"  Boyut: {size:,} bytes ({size/1024/1024:.1f} MB)")
    
    print("""
============================================================
YÜKLEME TALİMATLARI:
============================================================

1. USB Debugging açık olmalı

2. Mevcut uygulamayı kaldır (imza uyumsuzluğu için):
   adb uninstall com.vendor.studentapp

3. Patched APK yükle:
   adb install "app_patched_signed.apk"

4. Veya sadece yükle (-r = replace):
   adb install -r "app_patched_signed.apk"

NOT: Orijinal app farklı imzayla imzalandığından,
     önce uninstall + install gerekebilir.
     UYARI: Uygulama verileri silinecek!

============================================================
PATCH DOĞRULAMA:
============================================================
Login ekranına git → Doğru şifre gir → Giriş Yap'a bas
→ Spinner çalışacak → DIREK StudentTabs ekranına geçmeli!

İkinci basışta "hatalı" demeyecek çünkü navigation çalışacak.
============================================================
""")
else:
    print(f"HATA: İmzalı APK oluşturulamadı")
    print(f"Lütfen manuel imzalayın:")
    print(f'  apksigner sign --ks {DEBUG_KEYSTORE} --ks-alias debug_key --ks-pass pass:changeit --key-pass pass:changeit --out "{PATCHED_SIGNED}" "{PATCHED_ALIGNED}"')
