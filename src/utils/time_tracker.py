"""
Time Tracking Module
Tracks study time and session duration
"""

import datetime
import json
import os
from ..config.constants import get_data_dir

class TimeTracker:
    """Tracks study time and sessions"""
    
    def __init__(self):
        # Always get fresh path in case we're running from EXE
        self.sessions_file = os.path.join(get_data_dir(), "study_sessions.json")
        self.sessions = self.load_sessions()
    
    def load_sessions(self):
        """Load study sessions"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_sessions(self):
        """Save study sessions"""
        try:
            os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def start_session(self, subject_name):
        """Start a study session"""
        session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        session = {
            "subject": subject_name,
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None,
            "duration_minutes": 0,
            "questions_solved": 0,
            "notes": ""
        }
        self.sessions[session_id] = session
        self.save_sessions()
        return session_id
    
    def end_session(self, session_id, questions_solved=0, notes=""):
        """End a study session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            end_time = datetime.datetime.now()
            start_time = datetime.datetime.fromisoformat(session["start_time"])
            duration = (end_time - start_time).total_seconds() / 60  # minutes
            
            session["end_time"] = end_time.isoformat()
            session["duration_minutes"] = round(duration, 2)
            session["questions_solved"] = questions_solved
            session["notes"] = notes
            
            self.save_sessions()
            return session
        return None
    
    def get_today_stats(self):
        """Get today's study statistics"""
        today = datetime.date.today().isoformat()
        today_sessions = [
            s for s in self.sessions.values()
            if s.get("start_time", "").startswith(today)
        ]
        
        total_time = sum(s.get("duration_minutes", 0) for s in today_sessions)
        total_questions = sum(s.get("questions_solved", 0) for s in today_sessions)
        session_count = len(today_sessions)
        
        return {
            "total_time_minutes": total_time,
            "total_questions": total_questions,
            "session_count": session_count,
            "sessions": today_sessions
        }
    
    def get_week_stats(self):
        """Get this week's study statistics"""
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        week_sessions = []
        for session in self.sessions.values():
            start_time = session.get("start_time", "")
            if start_time:
                session_date = datetime.datetime.fromisoformat(start_time).date()
                if session_date >= week_start:
                    week_sessions.append(session)
        
        total_time = sum(s.get("duration_minutes", 0) for s in week_sessions)
        total_questions = sum(s.get("questions_solved", 0) for s in week_sessions)
        
        # Group by subject
        by_subject = {}
        for session in week_sessions:
            subject = session.get("subject", "Unknown")
            if subject not in by_subject:
                by_subject[subject] = {
                    "time": 0,
                    "questions": 0,
                    "sessions": 0
                }
            by_subject[subject]["time"] += session.get("duration_minutes", 0)
            by_subject[subject]["questions"] += session.get("questions_solved", 0)
            by_subject[subject]["sessions"] += 1
        
        return {
            "total_time_minutes": total_time,
            "total_questions": total_questions,
            "session_count": len(week_sessions),
            "by_subject": by_subject
        }
    
    def get_subject_stats(self, subject_name, days=30):
        """Get statistics for a specific subject"""
        cutoff_date = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        
        subject_sessions = [
            s for s in self.sessions.values()
            if s.get("subject") == subject_name and s.get("start_time", "").startswith(cutoff_date[:10])
        ]
        
        total_time = sum(s.get("duration_minutes", 0) for s in subject_sessions)
        total_questions = sum(s.get("questions_solved", 0) for s in subject_sessions)
        
        # Daily breakdown
        daily_stats = {}
        for session in subject_sessions:
            date = session.get("start_time", "")[:10]
            if date not in daily_stats:
                daily_stats[date] = {
                    "time": 0,
                    "questions": 0,
                    "sessions": 0
                }
            daily_stats[date]["time"] += session.get("duration_minutes", 0)
            daily_stats[date]["questions"] += session.get("questions_solved", 0)
            daily_stats[date]["sessions"] += 1
        
        return {
            "total_time_minutes": total_time,
            "total_questions": total_questions,
            "session_count": len(subject_sessions),
            "daily_stats": daily_stats,
            "average_time_per_session": total_time / len(subject_sessions) if subject_sessions else 0
        }

