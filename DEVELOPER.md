# 👨‍💻 Developer Documentation

<div align="center">

**Crono Ders Takip Sistemi - Open Source Development Guide**

**TEAM AURORA** | **Developer: Chaster** | **Version: 1.0.0**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-blue.svg)](https://www.python.org/dev/peps/pep-0008/)

[📖 Overview](#-genel-bakış--overview) • [🏗️ Architecture](#️-kod-organizasyonu--code-organization) • [🛠️ Setup](#️-geliştirme-ortamı--development-environment) • [📚 API](#-api-dokümantasyonu--api-documentation)

</div>

---

## 📋 İçindekiler / Table of Contents

- [Genel Bakış / Overview](#-genel-bakış--overview)
- [Proje Yapısı / Project Structure](#-proje-yapısı--project-structure)
- [Kod Organizasyonu / Code Organization](#️-kod-organizasyonu--code-organization)
- [Geliştirme Ortamı / Development Environment](#️-geliştirme-ortamı--development-environment)
- [Kod Standartları / Code Standards](#-kod-standartları--code-standards)
- [Katkıda Bulunma / Contributing](#-katkıda-bulunma--contributing)
- [API Dokümantasyonu / API Documentation](#-api-dokümantasyonu--api-documentation)
- [Test Etme / Testing](#-test-etme--testing)
- [Build ve Dağıtım / Build and Distribution](#-build-ve-dağıtım--build-and-distribution)
- [Debugging](#-debugging)
- [Yeni Özellik Ekleme / Adding New Features](#-yeni-özellik-ekleme--adding-new-features)

---

## 🎯 Genel Bakış / Overview

**Crono Ders Takip Sistemi**, modüler mimari kullanılarak geliştirilmiş bir Python uygulamasıdır. Uygulama, CustomTkinter kullanarak modern bir GUI sağlar ve Matplotlib ile görselleştirmeler yapar.

**Crono Ders Takip Sistemi** is a Python application developed using modular architecture. The application provides a modern GUI using CustomTkinter and visualizations using Matplotlib.

### Teknoloji Stack / Technology Stack

| Teknoloji / Technology | Versiyon / Version | Amaç / Purpose |
|------------------------|-------------------|----------------|
| **Python** | 3.8+ | Ana programlama dili / Main programming language |
| **CustomTkinter** | 5.2.0+ | Modern GUI framework |
| **Matplotlib** | 3.7.0+ | Chart and graph generation |
| **Pandas** | 2.0.0+ | Data manipulation (for exports) |
| **ReportLab** | 4.0.0+ | PDF generation |
| **Pillow (PIL)** | 10.0.0+ | Image processing |
| **OpenPyXL** | 3.1.0+ | Excel file handling |
| **PyInstaller** | 5.13.0+ | Executable creation |

### Mimari Prensipleri / Architecture Principles

1. **Modüler Yapı / Modular Structure**: Her modül tek bir sorumluluğa sahiptir
2. **Separation of Concerns**: UI, iş mantığı ve veri katmanları ayrıdır
3. **Dependency Injection**: Modüller arası bağımlılıklar minimize edilmiştir
4. **Extensibility**: Yeni özellikler kolayca eklenebilir
5. **Maintainability**: Kod okunabilir ve bakımı kolaydır

---

## 📁 Proje Yapısı / Project Structure

```
EJU_Takip/
├── src/                           # Kaynak kod / Source code
│   ├── __init__.py
│   ├── config/                    # Yapılandırma / Configuration
│   │   ├── __init__.py
│   │   ├── constants.py          # Uygulama sabitleri / Application constants
│   │   └── settings.py            # Ayarlar yönetimi / Settings management
│   ├── ui/                        # Kullanıcı arayüzü / User interface
│   │   ├── __init__.py
│   │   ├── main_window.py        # Ana pencere / Main window
│   │   └── components/            # UI bileşenleri / UI components
│   │       ├── __init__.py
│   │       └── dashboard.py      # Dashboard widget
│   ├── utils/                     # Yardımcı modüller / Utility modules
│   │   ├── __init__.py
│   │   ├── data_manager.py       # Veri yönetimi / Data management
│   │   ├── language.py           # Dil yönetimi / Language management
│   │   ├── time_tracker.py      # Zaman takibi / Time tracking
│   │   ├── notes_manager.py      # Not yönetimi / Notes management
│   │   ├── goal_tracker.py      # Hedef takibi / Goal tracking
│   │   ├── analytics.py         # Analitik / Analytics
│   │   ├── export_manager.py    # Dışa aktarma / Export management
│   │   ├── quote_manager.py    # Motivasyon sözleri / Motivation quotes
│   │   └── file_utils.py       # Dosya yardımcıları / File utilities
│   └── graphics/                  # Grafik modülleri / Chart modules
│       ├── __init__.py
│       └── chart_manager.py      # Grafik yönetimi / Chart management
├── locales/                       # Dil dosyaları / Language files
│   ├── tr.json                   # Türkçe çeviriler / Turkish translations
│   └── en.json                   # İngilizce çeviriler / English translations
├── assets/                        # Varlıklar / Assets
│   └── icons/                    # İkonlar / Icons
├── data/                          # Veri dosyaları / Data files
│   ├── study_data.json          # Çalışma verileri / Study data
│   ├── app_config.json          # Uygulama ayarları / Application settings
│   ├── notes.json               # Notlar / Notes
│   └── study_sessions.json      # Çalışma oturumları / Study sessions
├── dist/                          # Derlenmiş dosyalar / Compiled files
│   └── Crono_Ders_Takip_Sistemi.exe
├── build/                         # Build geçici dosyaları / Build temp files (gitignore)
├── main.py                        # Ana giriş noktası / Main entry point
├── build_exe.py                  # EXE build script
├── Crono_Ders_Takip_Sistemi.spec # PyInstaller spec file
├── setup.py                      # Setup script
├── requirements.txt              # Python bağımlılıkları / Dependencies
├── sözler.json                   # Motivasyon sözleri / Motivation quotes
├── pngegg.png                    # Uygulama ikonu / Application icon
├── README.md                     # Kullanıcı dokümantasyonu / User documentation
├── DEVELOPER.md                  # Bu dosya / This file
└── LICENSE                       # MIT License
```

---

## 🏗️ Kod Organizasyonu / Code Organization

### Modüler Yapı / Modular Structure

Uygulama, aşağıdaki modüllere ayrılmıştır:

The application is divided into the following modules:

#### 1. **Config Module** (`src/config/`)

Yapılandırma ve sabitler yönetimi.

Configuration and constants management.

- **`constants.py`**: 
  - Uygulama sabitleri (renkler, yollar, varsayılanlar)
  - Application constants (colors, paths, defaults)
  - Dosya yolu yardımcı fonksiyonları
  - File path helper functions

- **`settings.py`**: 
  - Kullanıcı ayarları yönetimi (JSON tabanlı)
  - User settings management (JSON-based)
  - Ayarları yükleme ve kaydetme
  - Loading and saving settings

#### 2. **UI Module** (`src/ui/`)

Kullanıcı arayüzü bileşenleri.

User interface components.

- **`main_window.py`**: 
  - Ana uygulama penceresi
  - Main application window
  - Tüm UI mantığı ve event handling
  - All UI logic and event handling
  - Widget yönetimi
  - Widget management

- **`components/dashboard.py`**: 
  - Dashboard widget bileşeni
  - Dashboard widget component
  - İstatistik gösterimi
  - Statistics display

#### 3. **Utils Module** (`src/utils/`)

Yardımcı modüller ve iş mantığı.

Utility modules and business logic.

- **`data_manager.py`**: 
  - Veri yükleme, kaydetme ve yönetim
  - Data loading, saving, and management
  - CRUD işlemleri
  - CRUD operations

- **`language.py`**: 
  - Çoklu dil desteği yönetimi
  - Multi-language support management
  - Çeviri yükleme
  - Translation loading

- **`time_tracker.py`**: 
  - Çalışma süresi takibi
  - Study time tracking
  - Oturum yönetimi
  - Session management

- **`notes_manager.py`**: 
  - Not yönetimi
  - Notes management
  - Not CRUD işlemleri
  - Note CRUD operations

- **`goal_tracker.py`**: 
  - Hedef takibi
  - Goal tracking
  - İlerleme hesaplama
  - Progress calculation

- **`analytics.py`**: 
  - İstatistiksel analizler
  - Statistical analytics
  - Verimlilik skorları
  - Productivity scores

- **`export_manager.py`**: 
  - Veri dışa aktarma (JSON, Excel, PDF)
  - Data export (JSON, Excel, PDF)
  - Format dönüştürme
  - Format conversion

- **`quote_manager.py`**: 
  - Motivasyon sözleri yönetimi
  - Motivation quotes management
  - Rastgele söz seçimi
  - Random quote selection

- **`file_utils.py`**: 
  - Dosya işlemleri yardımcıları
  - File operation helpers
  - Dosya yolu yönetimi
  - File path management

#### 4. **Graphics Module** (`src/graphics/`)

Grafik oluşturma ve yönetimi.

Chart creation and management.

- **`chart_manager.py`**: 
  - Matplotlib grafikleri oluşturma ve yönetme
  - Creating and managing Matplotlib charts
  - Tema uyumlu grafikler
  - Theme-compatible charts

---

## 🛠️ Geliştirme Ortamı / Development Environment

### Gereksinimler / Requirements

- **Python 3.8+**
- **pip** (Python paket yöneticisi)
- **Git** (İsteğe bağlı / Optional)
- **IDE** (VS Code, PyCharm, vb. / etc.)

### Kurulum Adımları / Installation Steps

1. **Repository'yi klonlayın / Clone the repository**

   ```bash
   git clone <repository-url>
   cd EJU_Takip
   ```

2. **Virtual Environment Oluşturun / Create Virtual Environment**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Bağımlılıkları Yükleyin / Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı Çalıştırın / Run the Application**

   ```bash
   python main.py
   ```

### Geliştirme Modu / Development Mode

```bash
# Uygulamayı çalıştır / Run application
python main.py

# Debug modu için / For debug mode
python -m pdb main.py

# Verbose modu / Verbose mode
python -v main.py
```

### IDE Yapılandırması / IDE Configuration

#### VS Code

`.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.analysis.typeCheckingMode": "basic"
}
```

#### PyCharm

1. File → Settings → Project → Python Interpreter
2. Virtual environment'i seçin / Select virtual environment
3. Code Style → Python → PEP 8

---

## 📝 Kod Standartları / Code Standards

### Python Kod Stili / Python Code Style

- **PEP 8** standartlarına uygun olmalı
- **Type hints** kullanımı önerilir
- **Docstrings** tüm fonksiyonlar için zorunlu
- **Modüler yapı**: Her modül tek bir sorumluluğa sahip olmalı

#### Örnek Kod / Example Code

```python
from typing import Optional, Dict, List

def example_function(param1: str, param2: int, param3: Optional[bool] = None) -> Dict[str, any]:
    """
    Fonksiyon açıklaması / Function description
    
    Bu fonksiyon örnek bir işlem yapar.
    This function performs an example operation.
    
    Args:
        param1: Açıklama / Description
        param2: Açıklama / Description
        param3: İsteğe bağlı parametre / Optional parameter
    
    Returns:
        Dict: Sonuç sözlüğü / Result dictionary
    
    Raises:
        ValueError: Parametreler geçersizse / If parameters are invalid
    
    Example:
        >>> result = example_function("test", 123)
        >>> print(result)
        {'status': 'success'}
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    result = {
        "status": "success",
        "data": {"param1": param1, "param2": param2}
    }
    
    return result
```

### Dosya Organizasyonu / File Organization

- Her modül kendi dizininde
- `__init__.py` dosyaları modül export'ları için kullanılır
- Constants ve settings ayrı modüllerde
- UI bileşenleri `components/` altında

### İsimlendirme Kuralları / Naming Conventions

- **Sınıflar / Classes**: `PascalCase` (örn: `DataManager`)
- **Fonksiyonlar / Functions**: `snake_case` (örn: `get_data()`)
- **Değişkenler / Variables**: `snake_case` (örn: `user_name`)
- **Sabitler / Constants**: `UPPER_SNAKE_CASE` (örn: `MAX_SIZE`)
- **Private**: `_leading_underscore` (örn: `_internal_method()`)

### Hata Yönetimi / Error Handling

```python
import logging

logger = logging.getLogger(__name__)

def risky_operation():
    """Örnek hata yönetimi / Example error handling"""
    try:
        # Risky operation
        result = risky_function()
        return result
    except SpecificError as e:
        # Handle specific error
        logger.error(f"Specific error occurred: {e}")
        return None
    except Exception as e:
        # Handle general error
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise
```

### Logging

```python
import logging

# Logger yapılandırması / Logger configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

---

## 🤝 Katkıda Bulunma / Contributing

### Katkı Süreci / Contribution Process

1. **Fork** yapın / Fork the repository
2. **Feature branch** oluşturun / Create a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Değişikliklerinizi commit edin** / Commit your changes
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Branch'inizi push edin** / Push your branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Pull Request** oluşturun / Create a Pull Request

### Commit Mesajları / Commit Messages

- **Format**: `type(scope): message`
- **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- **Example**: `feat(ui): add dark mode toggle button`

### Pull Request Şablonu / Pull Request Template

```markdown
## Açıklama / Description
[Değişikliklerin kısa açıklaması / Brief description of changes]

## Değişiklik Türü / Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Test Edildi mi? / Tested?
- [ ] Evet / Yes
- [ ] Hayır / No

## Ekran Görüntüleri / Screenshots
[Varsa ekleyin / Add if available]
```

---

## 📚 API Dokümantasyonu / API Documentation

### DataManager (`src/utils/data_manager.py`)

Veri yönetimi için ana sınıf.

Main class for data management.

```python
class DataManager:
    def load_data(self) -> dict:
        """Verileri yükle / Load data"""
        pass
    
    def save_data(self) -> None:
        """Verileri kaydet / Save data"""
        pass
    
    def add_subject(self, name: str, **kwargs) -> tuple[bool, str]:
        """Yeni ders ekle / Add new subject"""
        pass
    
    def update_subject(self, old_name: str, new_name: str, **kwargs) -> tuple[bool, str]:
        """Ders güncelle / Update subject"""
        pass
    
    def delete_subject(self, name: str) -> bool:
        """Ders sil / Delete subject"""
        pass
    
    def add_questions(self, subject: str, count: int) -> None:
        """Soru ekle / Add questions"""
        pass
    
    def get_statistics(self) -> dict:
        """İstatistikleri al / Get statistics"""
        pass
```

### LanguageManager (`src/utils/language.py`)

Çoklu dil desteği yönetimi.

Multi-language support management.

```python
class LanguageManager:
    def __init__(self, language: str = "tr"):
        """Dil yöneticisi başlat / Initialize language manager"""
        pass
    
    def set_language(self, lang: str) -> None:
        """Dil ayarla / Set language"""
        pass
    
    def get(self, key: str, default: str = "") -> str:
        """Çeviri al / Get translation"""
        pass
    
    def translate(self, key: str, **kwargs) -> str:
        """Çeviri yap (parametreli) / Translate (with parameters)"""
        pass
```

### ChartManager (`src/graphics/chart_manager.py`)

Grafik oluşturma ve yönetimi.

Chart creation and management.

```python
class ChartManager:
    def create_general_progress_chart(
        self, 
        master_frame, 
        data_manager, 
        theme_mode: str = 'dark'
    ) -> None:
        """Genel ilerleme grafiği oluştur / Create general progress chart"""
        pass
    
    def create_subject_comparison_chart(
        self, 
        master_frame, 
        data_manager, 
        subject: str, 
        theme_mode: str = 'dark'
    ) -> None:
        """Ders karşılaştırma grafiği oluştur / Create subject comparison chart"""
        pass
```

### Analytics (`src/utils/analytics.py`)

İstatistiksel analizler.

Statistical analytics.

```python
class Analytics:
    def __init__(self, data_manager, time_tracker, goal_tracker):
        """Analitik başlat / Initialize analytics"""
        pass
    
    def get_productivity_score(self) -> float:
        """Verimlilik skoru al / Get productivity score"""
        pass
    
    def get_study_streak(self) -> int:
        """Çalışma serisi al / Get study streak"""
        pass
    
    def get_weekly_trend(self) -> dict:
        """Haftalık trend al / Get weekly trend"""
        pass
    
    def get_recommendations(self) -> list[str]:
        """Öneriler al / Get recommendations"""
        pass
```

---

## 🧪 Test Etme / Testing

### Manuel Test / Manual Testing

```bash
# Uygulamayı çalıştır ve test et / Run and test application
python main.py

# Farklı senaryoları test et / Test different scenarios
# - Yeni ders ekleme / Adding new subject
# - Soru ekleme / Adding questions
# - Grafik görüntüleme / Viewing charts
# - Dil değiştirme / Changing language
# - Tema değiştirme / Changing theme
```

### Test Senaryoları / Test Scenarios

1. **Veri Yönetimi / Data Management**
   - Ders ekleme/silme/güncelleme
   - Veri kaydetme/yükleme
   - Veri bütünlüğü kontrolü

2. **UI Testleri / UI Tests**
   - Tüm butonların çalışması
   - Form validasyonları
   - Hata mesajları

3. **Grafik Testleri / Chart Tests**
   - Grafik oluşturma
   - Tema değişikliklerinde grafik güncelleme
   - Boş veri durumları

4. **Dil ve Tema Testleri / Language and Theme Tests**
   - Dil değiştirme
   - Tema değiştirme
   - Ayarların kalıcılığı

---

## 📦 Build ve Dağıtım / Build and Distribution

### EXE Oluşturma / Creating EXE

```bash
# PyInstaller yükle / Install PyInstaller
pip install pyinstaller

# Build script çalıştır / Run build script
python build_exe.py

# EXE dosyası dist/ klasöründe oluşturulur
# EXE file is created in dist/ folder
```

### Build Script Yapılandırması / Build Script Configuration

`build_exe.py` dosyası PyInstaller ayarlarını içerir:

The `build_exe.py` file contains PyInstaller settings:

- **Icon dosyası / Icon file**: `pngegg.png`
- **Gizli import'lar / Hidden imports**: Tüm gerekli modüller
- **Data dosyaları / Data files**: `locales/`, `data/`, `sözler.json`
- **Exclude modülleri / Exclude modules**: Gereksiz modüller

### Build Optimizasyonu / Build Optimization

- **UPX sıkıştırma**: Dosya boyutunu küçültür
- **Gereksiz modülleri hariç tut**: Build süresini kısaltır
- **Cache temizleme**: Temiz build için

---

## 🔍 Debugging

### Logging Yapılandırması / Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### Yaygın Sorunlar / Common Issues

#### 1. Import Hataları / Import Errors

**Sorun / Problem**: Modül bulunamıyor / Module not found

**Çözüm / Solution**:
- `src/` dizininin Python path'inde olduğundan emin olun
- Virtual environment aktif mi kontrol edin
- `sys.path.insert(0, ...)` kullanın

#### 2. Grafik Görüntüleme Sorunları / Chart Display Issues

**Sorun / Problem**: Grafikler görünmüyor / Charts not displaying

**Çözüm / Solution**:
- Matplotlib backend kontrolü
- Tema renkleri uyumluluğu
- DPI ayarları

#### 3. Veri Kaydetme Sorunları / Data Saving Issues

**Sorun / Problem**: Veriler kaydedilmiyor / Data not saving

**Çözüm / Solution**:
- `data/` dizini yazılabilir mi kontrol edin
- JSON format doğruluğu
- Dosya izinleri

#### 4. PyInstaller Build Sorunları / PyInstaller Build Issues

**Sorun / Problem**: EXE oluşturulamıyor / Cannot create EXE

**Çözüm / Solution**:
- Tüm bağımlılıkların yüklü olduğundan emin olun
- Hidden imports'ları kontrol edin
- Spec dosyasını kontrol edin

---

## 🎨 Yeni Özellik Ekleme / Adding New Features

### Adımlar / Steps

1. **Özellik Planlaması / Feature Planning**
   - Özellik gereksinimlerini belirleyin
   - UI/UX tasarımını planlayın
   - API tasarımını yapın

2. **Kod Geliştirme / Code Development**
   - İlgili modülde fonksiyon ekleyin
   - UI bileşenlerini güncelleyin
   - Dil dosyalarını güncelleyin

3. **Test / Testing**
   - Özelliği test edin
   - Edge case'leri kontrol edin
   - Hata senaryolarını test edin

4. **Dokümantasyon / Documentation**
   - Kod dokümantasyonu ekleyin
   - Kullanıcı dokümantasyonunu güncelleyin
   - API dokümantasyonunu güncelleyin

### Örnek: Yeni Grafik Türü Ekleme / Example: Adding New Chart Type

```python
# src/graphics/chart_manager.py
def create_weekly_progress_chart(
    self, 
    master_frame, 
    data_manager, 
    theme_mode: str = 'dark'
) -> None:
    """
    Haftalık ilerleme çizgi grafiği oluştur
    Create weekly progress line chart
    
    Args:
        master_frame: Ana frame / Main frame
        data_manager: Veri yöneticisi / Data manager
        theme_mode: Tema modu / Theme mode
    """
    # Implementation
    pass
```

### Örnek: Yeni Dil Ekleme / Example: Adding New Language

1. `locales/` dizininde yeni JSON dosyası oluşturun (örn: `fr.json`)
2. Mevcut dil dosyasından yapıyı kopyalayın
3. Tüm string'leri çevirin
4. `src/utils/language.py` dosyasında dil seçeneklerine ekleyin
5. `src/ui/main_window.py` dosyasında dil seçiciyi güncelleyin

### Örnek: Renk Şeması Özelleştirme / Example: Customizing Color Scheme

`src/config/constants.py` dosyasındaki `COLORS` dictionary'sini düzenleyin:

Edit the `COLORS` dictionary in `src/config/constants.py`:

```python
COLORS = {
    "PRIMARY": "#your-color",
    "SECONDARY": "#your-color",
    # ... diğer renkler / other colors
}
```

---

## 📝 Kod İnceleme / Code Review

### İnceleme Kriterleri / Review Criteria

- ✅ Kod standartlarına uygunluk
- ✅ Fonksiyonellik doğruluğu
- ✅ Hata yönetimi
- ✅ Performans optimizasyonu
- ✅ Dokümantasyon kalitesi
- ✅ Test kapsamı

### İnceleme Süreci / Review Process

1. Pull Request oluşturulur
2. Otomatik kontroller çalışır
3. Kod incelemesi yapılır
4. Geri bildirim verilir
5. Değişiklikler yapılır
6. Onaylanır ve merge edilir

---

## 🔐 Güvenlik / Security

### Güvenlik Prensipleri / Security Principles

- ✅ Kullanıcı verileri yerel olarak saklanır
- ✅ Veri şifreleme (gelecekte eklenebilir)
- ✅ Input validasyonu
- ✅ Hata mesajlarında hassas bilgi yok

### Güvenlik Açığı Bildirimi / Vulnerability Reporting

Güvenlik açığı bulursanız, lütfen doğrudan geliştirici ile iletişime geçin.

If you find a security vulnerability, please contact the developer directly.

---

## 📞 İletişim / Contact

Sorularınız, önerileriniz, geri dönüşleriniz, proje fikirleriniz veya takıma katılmak için:

For questions, suggestions, feedback, project ideas, or to join the team:

- 📧 **E-posta / Email**: [chasterteamaurora@gmail.com](mailto:chasterteamaurora@gmail.com)
  - Geri dönüşler ve yorumlar / Feedback and comments
  - Proje fikirleri / Project ideas
  - Takıma katılmak / Join the team
  - Teknik destek / Technical support
  - Kod inceleme istekleri / Code review requests
- 💬 **GitHub Issues**: Proje deposunda issue açın / Open an issue in the project repository
- 👤 **Developer**: Chaster
- 👥 **Team**: TEAM AURORA

---

## 📄 Lisans / License

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Happy Coding! 🚀**

Made with ❤️ by **TEAM AURORA**

[⬆ Back to Top](#-developer-documentation)

</div>
