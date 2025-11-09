"""
Data Management Module
"""

import json
import os
import datetime
from ..config.constants import get_data_file, DEFAULT_SUBJECTS

class DataManager:
    """Manages study data operations"""
    
    def __init__(self, data_file=None):
        # Always get fresh path in case we're running from EXE
        self.data_file = data_file or get_data_file()
        self.data = self.load_data()
        self._ensure_data_integrity()
    
    def load_data(self):
        """Load data from file"""
        if not os.path.exists(self.data_file):
            return self._create_default_data()
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Data load error: {e}")
            return self._create_default_data()
    
    def save_data(self):
        """Save data to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Data save error: {e}")
            return False
    
    def _create_default_data(self):
        """Create default data structure"""
        default_data = DEFAULT_SUBJECTS.copy()
        self.save_data()
        return default_data
    
    def _ensure_data_integrity(self):
        """Ensure data structure integrity"""
        updated = False
        for subject_name, subject_data in self.data.items():
            # Ensure all required keys exist
            if 'cozulen_soru' not in subject_data:
                subject_data['cozulen_soru'] = 0
                updated = True
            if 'hedef_soru' not in subject_data:
                subject_data['hedef_soru'] = 500
                updated = True
            if 'son_calisma_tarihi' not in subject_data:
                subject_data['son_calisma_tarihi'] = ""
                updated = True
            if 'konular' not in subject_data:
                subject_data['konular'] = []
                updated = True
            
            # Enhanced fields
            if 'category' not in subject_data:
                subject_data['category'] = ""
                updated = True
            if 'priority' not in subject_data:
                subject_data['priority'] = "medium"
                updated = True
            if 'deadline' not in subject_data:
                subject_data['deadline'] = ""
                updated = True
            if 'status' not in subject_data:
                subject_data['status'] = "active"
                updated = True
            if 'description' not in subject_data:
                subject_data['description'] = ""
                updated = True
            if 'created_date' not in subject_data:
                subject_data['created_date'] = datetime.date.today().isoformat()
                updated = True
            if 'tags' not in subject_data:
                subject_data['tags'] = []
                updated = True
            
            # Ensure topics have required fields
            for topic in subject_data.get('konular', []):
                if 'ad' not in topic:
                    topic['ad'] = ""
                if 'durum' not in topic:
                    topic['durum'] = "Yapılacak"
                if 'baslangic_tarihi' not in topic:
                    topic['baslangic_tarihi'] = "-"
                if 'bitirme_tarihi' not in topic:
                    topic['bitirme_tarihi'] = "-"
        
        if updated:
            self.save_data()
    
    def add_tag(self, subject_name, tag):
        """Add a tag to a subject/project"""
        if subject_name in self.data:
            if 'tags' not in self.data[subject_name]:
                self.data[subject_name]['tags'] = []
            if tag not in self.data[subject_name]['tags']:
                self.data[subject_name]['tags'].append(tag)
                self.save_data()
                return True
        return False
    
    def remove_tag(self, subject_name, tag):
        """Remove a tag from a subject/project"""
        if subject_name in self.data and 'tags' in self.data[subject_name]:
            if tag in self.data[subject_name]['tags']:
                self.data[subject_name]['tags'].remove(tag)
                self.save_data()
                return True
        return False
    
    def get_subjects_by_category(self, category):
        """Get all subjects in a category"""
        return {name: data for name, data in self.data.items() if data.get('category', '') == category}
    
    def get_subjects_by_priority(self, priority):
        """Get all subjects with a specific priority"""
        return {name: data for name, data in self.data.items() if data.get('priority', 'medium') == priority}
    
    def get_subjects_by_status(self, status):
        """Get all subjects with a specific status"""
        return {name: data for name, data in self.data.items() if data.get('status', 'active') == status}
    
    def get_upcoming_deadlines(self, days=7):
        """Get subjects with deadlines in the next N days"""
        today = datetime.date.today()
        cutoff = today + datetime.timedelta(days=days)
        upcoming = {}
        
        for name, data in self.data.items():
            deadline_str = data.get('deadline', '')
            if deadline_str:
                try:
                    deadline = datetime.date.fromisoformat(deadline_str)
                    if today <= deadline <= cutoff:
                        upcoming[name] = data
                except:
                    continue
        
        return upcoming
    
    def get_all_categories(self):
        """Get all unique categories"""
        categories = set()
        for data in self.data.values():
            cat = data.get('category', '')
            if cat:
                categories.add(cat)
        return sorted(list(categories))
    
    def get_all_tags(self):
        """Get all unique tags"""
        tags = set()
        for data in self.data.values():
            for tag in data.get('tags', []):
                tags.add(tag)
        return sorted(list(tags))
    
    def add_subject(self, subject_name, initial_target=500, category="", priority="medium", deadline="", status="active", description=""):
        """Add a new subject/project with enhanced features"""
        if not subject_name or not subject_name.strip():
            return False, "empty_name"
        
        subject_name = subject_name.strip()
        
        if subject_name in self.data:
            return False, "exists"
        
        self.data[subject_name] = {
            "cozulen_soru": 0,
            "hedef_soru": initial_target,
            "son_calisma_tarihi": "",
            "konular": [],
            "category": category,
            "priority": priority,  # "high", "medium", "low"
            "deadline": deadline,
            "status": status,  # "active", "completed", "on_hold", "archived"
            "description": description,
            "created_date": datetime.date.today().isoformat(),
            "tags": []
        }
        self.save_data()
        return True, "success"
    
    def delete_subject(self, subject_name):
        """Delete a subject"""
        if subject_name in self.data:
            del self.data[subject_name]
            self.save_data()
            return True
        return False
    
    def update_subject(self, old_name, new_name, new_target=None, category=None, priority=None, deadline=None, status=None, description=None):
        """Update an existing subject/project with enhanced features"""
        if not new_name or not new_name.strip():
            return False, "empty_name"
        
        new_name = new_name.strip()
        
        if old_name != new_name and new_name in self.data:
            return False, "exists"
        
        if old_name in self.data:
            subject_data = self.data.pop(old_name)
            subject_data['hedef_soru'] = new_target if new_target is not None else subject_data.get('hedef_soru', 500)
            
            # Update enhanced fields if provided
            if category is not None:
                subject_data['category'] = category
            if priority is not None:
                subject_data['priority'] = priority
            if deadline is not None:
                subject_data['deadline'] = deadline
            if status is not None:
                subject_data['status'] = status
            if description is not None:
                subject_data['description'] = description
            
            # Ensure new fields exist
            if 'category' not in subject_data:
                subject_data['category'] = ""
            if 'priority' not in subject_data:
                subject_data['priority'] = "medium"
            if 'deadline' not in subject_data:
                subject_data['deadline'] = ""
            if 'status' not in subject_data:
                subject_data['status'] = "active"
            if 'description' not in subject_data:
                subject_data['description'] = ""
            if 'created_date' not in subject_data:
                subject_data['created_date'] = datetime.date.today().isoformat()
            if 'tags' not in subject_data:
                subject_data['tags'] = []
            
            self.data[new_name] = subject_data
            self.save_data()
            return True, None
        return False, "not_found"
    
    def add_questions(self, subject_name, count):
        """Add solved questions to a subject"""
        if subject_name in self.data:
            self.data[subject_name]['cozulen_soru'] += count
            self.data[subject_name]['son_calisma_tarihi'] = datetime.date.today().strftime("%Y-%m-%d")
            self.save_data()
            return True
        return False
    
    def set_target(self, subject_name, target):
        """Set target questions for a subject"""
        if subject_name in self.data:
            self.data[subject_name]['hedef_soru'] = target
            self.save_data()
            return True
        return False
    
    def add_topic(self, subject_name, topic_name):
        """Add a new topic to a subject"""
        if subject_name not in self.data:
            return False
        
        if not topic_name or not topic_name.strip():
            return False
        
        topic_name = topic_name.strip()
        
        # Check if topic already exists
        if any(t.get('ad') == topic_name for t in self.data[subject_name]['konular']):
            return False
        
        new_topic = {
            "ad": topic_name,
            "durum": "Yapılacak",
            "baslangic_tarihi": "-",
            "bitirme_tarihi": "-"
        }
        self.data[subject_name]['konular'].append(new_topic)
        self.save_data()
        return True
    
    def update_topic_status(self, subject_name, topic_name, new_status):
        """Update topic status"""
        if subject_name not in self.data:
            return False
        
        for topic in self.data[subject_name]['konular']:
            if topic.get('ad') == topic_name:
                topic['durum'] = new_status
                today = datetime.date.today().strftime("%Y-%m-%d")
                
                if new_status == "Devam Ediyor":
                    if topic.get('baslangic_tarihi') == "-":
                        topic['baslangic_tarihi'] = today
                    topic['bitirme_tarihi'] = "-"
                elif new_status == "Tamamlandı":
                    if topic.get('baslangic_tarihi') == "-":
                        topic['baslangic_tarihi'] = today
                    topic['bitirme_tarihi'] = today
                elif new_status == "Yapılacak":
                    topic['baslangic_tarihi'] = "-"
                    topic['bitirme_tarihi'] = "-"
                
                self.save_data()
                return True
        return False
    
    def delete_topic(self, subject_name, topic_name):
        """Delete a topic from a subject"""
        if subject_name not in self.data:
            return False
        
        initial_count = len(self.data[subject_name]['konular'])
        self.data[subject_name]['konular'] = [
            t for t in self.data[subject_name]['konular'] 
            if t.get('ad') != topic_name
        ]
        
        if len(self.data[subject_name]['konular']) < initial_count:
            self.save_data()
            return True
        return False
    
    def get_statistics(self):
        """Get general statistics"""
        total_solved = sum(subject.get('cozulen_soru', 0) for subject in self.data.values())
        total_target = sum(subject.get('hedef_soru', 1) for subject in self.data.values())
        total_topics = sum(len(subject.get('konular', [])) for subject in self.data.values())
        completed_topics = sum(
            len([t for t in subject.get('konular', []) if t.get('durum') == 'Tamamlandı'])
            for subject in self.data.values()
        )
        progress = (total_solved / total_target * 100) if total_target > 0 else 0
        remaining = max(0, total_target - total_solved)
        
        return {
            "total_solved": total_solved,
            "total_target": total_target,
            "progress": progress,
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "remaining": remaining
        }
