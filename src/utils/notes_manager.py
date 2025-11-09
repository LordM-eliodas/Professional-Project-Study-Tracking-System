"""
Notes Manager Module
Manages notes and comments for subjects and topics
"""

import json
import os
import datetime
from ..config.constants import get_data_dir

class NotesManager:
    """Manages notes and comments"""
    
    def __init__(self):
        # Always get fresh path in case we're running from EXE
        self.notes_file = os.path.join(get_data_dir(), "notes.json")
        self.notes = self.load_notes()
    
    def load_notes(self):
        """Load notes"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_notes(self):
        """Save notes"""
        try:
            os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def add_note(self, subject_name, topic_name=None, note_text=""):
        """Add a note to subject or topic"""
        key = f"{subject_name}:{topic_name}" if topic_name else f"{subject_name}:"
        
        if key not in self.notes:
            self.notes[key] = []
        
        note = {
            "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "text": note_text,
            "date": datetime.datetime.now().isoformat(),
            "subject": subject_name,
            "topic": topic_name
        }
        
        self.notes[key].append(note)
        self.save_notes()
        return note
    
    def get_notes(self, subject_name, topic_name=None):
        """Get notes for subject or topic"""
        key = f"{subject_name}:{topic_name}" if topic_name else f"{subject_name}:"
        return self.notes.get(key, [])
    
    def delete_note(self, subject_name, topic_name, note_id):
        """Delete a note"""
        key = f"{subject_name}:{topic_name}" if topic_name else f"{subject_name}:"
        if key in self.notes:
            self.notes[key] = [n for n in self.notes[key] if n.get("id") != note_id]
            self.save_notes()
            return True
        return False
    
    def get_all_notes(self):
        """Get all notes"""
        all_notes = []
        for key, notes_list in self.notes.items():
            all_notes.extend(notes_list)
        return sorted(all_notes, key=lambda x: x.get("date", ""), reverse=True)
    
    def set_last_position(self, subject_name, position_text=""):
        """Set last position/bookmark for a subject"""
        key = f"{subject_name}:__LAST_POSITION__"
        
        position = {
            "id": "last_position",
            "text": position_text,
            "date": datetime.datetime.now().isoformat(),
            "subject": subject_name,
            "topic": None,
            "is_last_position": True
        }
        
        self.notes[key] = [position]
        self.save_notes()
        return position
    
    def get_last_position(self, subject_name):
        """Get last position/bookmark for a subject"""
        key = f"{subject_name}:__LAST_POSITION__"
        if key in self.notes and len(self.notes[key]) > 0:
            return self.notes[key][0]
        return None
    
    def delete_last_position(self, subject_name):
        """Delete last position for a subject"""
        key = f"{subject_name}:__LAST_POSITION__"
        if key in self.notes:
            del self.notes[key]
            self.save_notes()
            return True
        return False

