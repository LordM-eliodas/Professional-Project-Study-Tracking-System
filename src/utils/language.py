"""
Language/Internationalization Manager
"""

import json
import os
from ..config.constants import LOCALES_DIR

class LanguageManager:
    """Manages application language and translations"""
    
    def __init__(self, language="tr"):
        self.language = language
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translations from locale files"""
        locale_file = os.path.join(LOCALES_DIR, f"{self.language}.json")
        
        if os.path.exists(locale_file):
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Translation load error: {e}")
                self.translations = self._get_default_translations()
        else:
            self.translations = self._get_default_translations()
    
    def set_language(self, language):
        """Change language"""
        self.language = language
        self.load_translations()
    
    def get(self, key, default=None):
        """Get translation for a key"""
        keys = key.split('.')
        value = self.translations
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default or key
    
    def translate(self, key, **kwargs):
        """Get translation and format with kwargs"""
        text = self.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        return text
    
    def _get_default_translations(self):
        """Get default Turkish translations if file not found"""
        return {
            "app": {
                "title": "Crono Ders Takip Sistemi",
                "team": "TEAM AURORA",
                "developer": "Chaster"
            },
            "menu": {
                "statistics": "İstatistikler",
                "export": "Dışa Aktar",
                "theme": "Tema"
            },
            "subject": {
                "select": "Bir ders seçin",
                "progress": "İlerleme",
                "solved": "Çözülen",
                "target": "Hedef",
                "questions": "Soru",
                "last_study": "Son Çalışma",
                "none": "Yok"
            },
            "actions": {
                "add_questions": "Soru Sayısı Ekle",
                "set_target": "Soru Hedefi Ayarla",
                "add_topic": "Yeni Konu Ekle",
                "add": "Ekle",
                "set": "Ayarla",
                "delete": "Sil",
                "close": "Kapat"
            },
            "topic": {
                "name": "Konu Adı",
                "status": "Durum",
                "start_date": "Başlangıç",
                "end_date": "Bitirme",
                "no_topics": "Bu derste kayıtlı konu yok. Hemen bir tane ekle!",
                "todo": "Yapılacak",
                "in_progress": "Devam Ediyor",
                "completed": "Tamamlandı"
            },
            "messages": {
                "success": "Başarılı",
                "error": "Hata",
                "question_added": "{count} soru eklendi!",
                "target_set": "Hedef {target} olarak ayarlandı.",
                "topic_added": "Konu eklendi.",
                "topic_deleted": "Konu silindi.",
                "confirm_delete": "Bu konuyu silmek istediğinize emin misiniz?",
                "invalid_number": "Lütfen geçerli, pozitif bir sayı girin!",
                "empty_topic": "Konu adı boş olamaz.",
                "topic_exists": "Bu konu zaten mevcut.",
                "export_success": "Veriler başarıyla kaydedildi!",
                "export_error": "Veri dışa aktarma sırasında bir hata oluştu."
            },
            "statistics": {
                "title": "İstatistikler",
                "general": "Genel İstatistikler",
                "by_subject": "Ders Bazlı İstatistikler",
                "total_solved": "Toplam Çözülen Soru",
                "total_target": "Toplam Hedef Soru",
                "progress": "Genel İlerleme",
                "total_topics": "Toplam Konu",
                "completed_topics": "Tamamlanan Konu",
                "remaining": "Kalan Soru"
            },
            "graph": {
                "general_progress": "Genel Soru İlerlemesi",
                "subject_comparison": "{subject} ve Diğer Dersler",
                "solved": "Çözüldü",
                "remaining": "Kaldı",
                "solved_questions": "Çözülen Soru",
                "target_questions": "Hedef Soru"
            }
        }

