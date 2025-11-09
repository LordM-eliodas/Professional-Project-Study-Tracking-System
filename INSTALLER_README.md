# 📦 Installer Oluşturma Kılavuzu / Installer Creation Guide

## 🎯 Genel Bakış / Overview

Bu proje, **Inno Setup** kullanarak profesyonel bir Windows kurulum programı oluşturur. Kurulum programı:

This project uses **Inno Setup** to create a professional Windows installer. The installer:

- ✅ Program Files'a kurulum yapar / Installs to Program Files
- ✅ Masaüstünde kısayol oluşturur / Creates desktop shortcut
- ✅ Başlat menüsüne ekler / Adds to Start Menu
- ✅ Kaldırma programı ekler / Adds uninstaller
- ✅ Modern kurulum arayüzü / Modern installer interface

---

## 📋 Gereksinimler / Requirements

### 1. Inno Setup Kurulumu / Install Inno Setup

1. **Inno Setup İndir** / Download Inno Setup:
   - Web sitesi: https://jrsoftware.org/isdl.php
   - En son sürümü indirin (6.x veya üzeri önerilir)
   - Download the latest version (6.x or higher recommended)

2. **Kurulum** / Installation:
   - İndirilen dosyayı çalıştırın / Run the downloaded file
   - Kurulum sihirbazını takip edin / Follow the installation wizard
   - Varsayılan ayarlarla kurun / Install with default settings

### 2. Python ve Bağımlılıklar / Python and Dependencies

- Python 3.8+ yüklü olmalı / Python 3.8+ must be installed
- Tüm bağımlılıklar yüklü olmalı / All dependencies must be installed

---

## 🚀 Kurulum Programı Oluşturma / Creating Installer

### Yöntem 1: Otomatik (Önerilen) / Method 1: Automatic (Recommended)

```bash
# 1. Önce exe dosyasını oluşturun / First, build the exe file
python build_exe.py

# 2. Installer oluşturun / Create installer
python create_installer.py
```

Script otomatik olarak:
- Inno Setup'ı bulur
- installer.iss dosyasını derler
- installer_output klasöründe installer oluşturur

The script automatically:
- Finds Inno Setup
- Compiles installer.iss file
- Creates installer in installer_output folder

### Yöntem 2: Manuel / Method 2: Manual

1. **Inno Setup Compiler'ı açın** / Open Inno Setup Compiler
2. **File → Open** ile `installer.iss` dosyasını açın / Open `installer.iss` file
3. **Build → Compile** ile derleyin / Compile with Build → Compile
4. Installer `installer_output` klasöründe oluşur / Installer will be created in `installer_output` folder

---

## 📁 Dosya Yapısı / File Structure

```
EJU_Takip/
├── installer.iss              # Inno Setup script dosyası
├── create_installer.py        # Otomatik installer oluşturma script'i
├── dist/
│   └── Crono_Ders_Takip_Sistemi.exe  # Ana uygulama exe'si
└── installer_output/         # Oluşturulan installer (buraya kaydedilir)
    └── Crono_Setup.exe       # Kurulum programı
```

---

## ⚙️ Installer Ayarları / Installer Settings

### Kurulum Konumu / Installation Location

Varsayılan olarak Program Files'a kurulur:
- `C:\Program Files\Crono Ders Takip Sistemi\`

By default, installs to Program Files:
- `C:\Program Files\Crono Ders Takip Sistemi\`

### Veri Klasörü / Data Folder

Uygulama verileri AppData klasöründe saklanır:
- `%APPDATA%\CronoDersTakip\data\`

Application data is stored in AppData folder:
- `%APPDATA%\CronoDersTakip\data\`

> ⚠️ **Not**: Artık exe dosyasının yanında data klasörü oluşmaz!
> 
> ⚠️ **Note**: Data folder will no longer be created next to the exe file!

### Kısayollar / Shortcuts

Kurulum sırasında oluşturulur:
- ✅ Masaüstü kısayolu (isteğe bağlı)
- ✅ Başlat menüsü kısayolu
- ✅ Hızlı başlat (Windows 7 ve öncesi)

Created during installation:
- ✅ Desktop shortcut (optional)
- ✅ Start menu shortcut
- ✅ Quick launch (Windows 7 and earlier)

---

## 🔧 Installer Özelleştirme / Customizing Installer

### installer.iss Dosyasını Düzenleme / Editing installer.iss

```iss
[Setup]
AppName={#MyAppName}              ; Uygulama adı / Application name
AppVersion={#MyAppVersion}         ; Versiyon / Version
DefaultDirName={autopf}\{#MyAppName}  ; Kurulum dizini / Installation directory
```

### İkon Değiştirme / Changing Icon

1. `pngegg.png` dosyasını değiştirin / Replace `pngegg.png` file
2. Veya `SetupIconFile` satırını düzenleyin / Or edit `SetupIconFile` line

### Lisans Dosyası / License File

`LicenseFile=LICENSE` satırı ile lisans dosyası gösterilir.

License file is shown via `LicenseFile=LICENSE` line.

---

## 📦 Dağıtım / Distribution

### Installer Dosyası / Installer File

Oluşturulan installer dosyası:
- **Konum / Location**: `installer_output/Crono_Setup.exe`
- **Boyut / Size**: ~50-60 MB (exe dosyası dahil / including exe file)
- **Format**: Windows Installer (.exe)

### Dağıtım Önerileri / Distribution Recommendations

1. **GitHub Releases**: Installer'ı GitHub Releases'a yükleyin
2. **Web Sitesi**: Kendi web sitenizde paylaşın
3. **Cloud Storage**: Google Drive, Dropbox, vb.

---

## 🐛 Sorun Giderme / Troubleshooting

### Inno Setup Bulunamıyor / Inno Setup Not Found

**Sorun / Problem**: `create_installer.py` Inno Setup'ı bulamıyor

**Çözüm / Solution**:
1. Inno Setup'ın kurulu olduğundan emin olun
2. Varsayılan konumda kurulu değilse, `create_installer.py` dosyasındaki path'leri güncelleyin

### Installer Derleme Hatası / Compilation Error

**Sorun / Problem**: Installer derlenirken hata alıyorsunuz

**Çözüm / Solution**:
1. `installer.iss` dosyasındaki syntax hatalarını kontrol edin
2. Tüm dosya yollarının doğru olduğundan emin olun
3. Inno Setup Compiler'da manuel olarak derleyip hata mesajlarını kontrol edin

### EXE Dosyası Bulunamıyor / EXE File Not Found

**Sorun / Problem**: `dist/Crono_Ders_Takip_Sistemi.exe` bulunamıyor

**Çözüm / Solution**:
```bash
# Önce exe dosyasını oluşturun / First, build the exe file
python build_exe.py
```

---

## 📝 Notlar / Notes

- Installer oluşturmadan önce mutlaka exe dosyasını oluşturun
- Before creating installer, always build the exe file first
- Installer boyutu exe dosyası boyutuna bağlıdır
- Installer size depends on exe file size
- Her yeni sürüm için installer.iss'teki versiyonu güncelleyin
- Update version in installer.iss for each new release

---

## 🔗 Faydalı Linkler / Useful Links

- **Inno Setup**: https://jrsoftware.org/isinfo.php
- **Inno Setup Dokümantasyonu**: https://jrsoftware.org/ishelp/
- **Inno Setup Örnekleri**: https://jrsoftware.org/is3/example-scripts.php

---

<div align="center">

**Made with ❤️ by TEAM AURORA**

</div>

