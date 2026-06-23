# the target app v3.4.0 — Bytecode Bugfix

a state university öğrenci bilgi sistemi mobil uygulaması **the target app**'deki iki kritik hatanın, Hermes HBC v96 bytecode düzeyinde tersine mühendislik ile düzeltilmesi.

## Düzeltilen Hatalar

| # | Hata | Çözüm |
|---|------|-------|
| 1 | **Login** — Doğru bilgilerle giriş yapıldığında ana sayfaya yönlendirme yapılmıyor | Navigasyon indeksi düzeltmesi (1 byte) |
| 2 | **Yoklama** — Derse tıklandığında *"Seçilen derse ait yoklama bulunamadı"* hatası | Endpoint değişikliği + veri format adaptasyonu (6 patch, 28 byte) |

## Teknik Özet

- **Toplam değişiklik:** 29 byte, 7 patch
- **Hedef dosya:** `assets/index.android.bundle` (Hermes HBC v96, 6 MB)
- **Yöntem:** Binary bytecode patching — opcode, propID ve string storage düzeyinde cerrahi müdahale

### Yoklama Fix Detayı

Uygulama `mtd26` (getStudentAttendanceHistory) endpoint'ini çağırıyordu ancak sunucu `Stat: false` döndürüyordu. Çalışan `mtd25` (getStudentAttendance) endpoint'i ise **farklı bir veri formatı** (flat liste vs nested yapı) kullanıyordu.

Çözüm:
1. API endpoint'i `mtd26` → `mtd25` olarak değiştirildi
2. Response property `yoklamaHaftalar` → `yoklamaList` propID yönlendirmesi
3. Render zincirindeki property erişimleri (`H_NO` → `TARIH`, `SAAT`) güncellendi
4. Nested yapı bekleyen null-check'ler, `NewArray` + `PutByIndex` ile flat item'ı tek elemanlı diziye sararak bypass edildi

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| _(patched APK not redistributed)_ | The patched APK is a modified build of a third-party commercial application and is **not** redistributed here for legal/ethical reasons. Rebuild it from your own copy of the original APK using the scripts below. |
| [**RAPOR_Tersine_Muhendislik.md**](RAPOR_Tersine_Muhendislik.md) | Detaylı tersine mühendislik raporu |

## Patch Tablosu

| # | Offset | Boyut | Açıklama |
|---|--------|-------|----------|
| 1 | `0x4FF3BB` | 1 B | Login navigasyon düzeltmesi |
| 2 | `0x0F0F99` | 1 B | API endpoint mtd26 → mtd25 |
| 3 | `0x521696` | 2 B | yoklamaHaftalar → yoklamaList propID |
| 4 | `0x5217A8` | 2 B | H_NO → TARIH propID (başlık) |
| 5 | `0x52181A` | 2 B | H_NO → SAAT propID (React key) |
| 6 | `0x5217EE` | 15 B | yoklamaGunler → NewArray wrap |
| 7 | `0x521A57` | 15 B | yoklamaSaatList → NewArray wrap |

## Araçlar

- Python 3.10 — Bytecode analizi ve hex patching
- JADX 1.5.1 — Java decompile
- hbc-decompiler 0.1.0 — Hermes HBC → JS decompile
- ADB 35.0.2 + Android Emulator (API 35)
- apksigner (build-tools 36.0)

## Reproducibility — Python Scripts

Makalede kullanılan tüm patch ve analiz script'leri `scripts/` klasöründe yer alıyor. Her script Python 3.10 ile çalışır ve harici bağımlılığı yoktur (yalnızca `sign_apk.py` için `apksigner` gerekir).

| Script | Rol | Girdi | Çıktı |
|---|---|---|---|
| [`scripts/apply_all_patches.py`](scripts/apply_all_patches.py) | **Ana patch pipeline** — 7 patch'i otomatik uygular | `index.android.bundle` | `index.android.bundle.patched` |
| [`scripts/patch_bundle.py`](scripts/patch_bundle.py) | Tek-patch (login JmpFalse offset) uygulama referans implementasyonu | `index.android.bundle` | patched bundle |
| [`scripts/verify_patch.py`](scripts/verify_patch.py) | Patch sonrası byte-byte doğrulama | original + patched bundle | pass/fail raporu |
| [`scripts/replace_in_apk.py`](scripts/replace_in_apk.py) | Patched bundle'ı APK içine yerleştirme (ZIP_STORED ile) | orijinal APK + patched bundle | patched APK |
| [`scripts/sign_apk.py`](scripts/sign_apk.py) | `apksigner` üzerinden APK imzalama | patched APK + keystore | signed APK |
| [`scripts/rebuild_apk_v3.py`](scripts/rebuild_apk_v3.py) | Replace + sign tek komutta | orijinal APK + patched bundle | final imzalı APK |
| [`scripts/parse_headers2.py`](scripts/parse_headers2.py) | HBC v96 fonksiyon header parser | `index.android.bundle` | fonksiyon offset/size tablosu |
| [`scripts/analyze_fun26882.py`](scripts/analyze_fun26882.py) | Yoklama data-loader fonksiyonunun bytecode analizi | bundle | disassembly çıktısı |
| [`scripts/disasm_fun26884.py`](scripts/disasm_fun26884.py) | Hafta-render fonksiyonunun bytecode disassembly + propID çıkarımı | bundle | opcode + propID listesi |

### Makaledeki Figürler

Paper'daki Figure 1-5'in üretim kodu ve çıktıları `figures/` altındadır:

- [`figures/generate_figures.py`](figures/generate_figures.py) — Matplotlib ile tüm figürleri 300 DPI'da üretir
- `figures/fig{1-5}*.png` — Üretilmiş 300 DPI figür PNG'leri (papera gömülen sürümler)

### Kullanım Örneği

```bash
# 1. Bundle'ı bir APK'dan çıkar
unzip "app_3.4.0.apk" assets/index.android.bundle -d extracted/

# 2. 7 patch'in tamamını uygula
python3 scripts/apply_all_patches.py extracted/assets/index.android.bundle

# 3. Doğrula
python3 scripts/verify_patch.py extracted/assets/index.android.bundle{,.patched}

# 4. APK içine yerleştir ve imzala
python3 scripts/rebuild_apk_v3.py \
  "app_3.4.0.apk" \
  extracted/assets/index.android.bundle.patched \
  app_patched_signed.apk
```

---

*Bu çalışma eğitim ve araştırma amacıyla yapılmıştır.*
