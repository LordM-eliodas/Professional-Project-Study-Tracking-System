"""
Analytics Module
Provides advanced analytics and insights
"""

import datetime
from collections import defaultdict

class Analytics:
    """Provides advanced analytics"""
    
    def __init__(self, data_manager, time_tracker, goal_tracker):
        self.data_manager = data_manager
        self.time_tracker = time_tracker
        self.goal_tracker = goal_tracker
    
    def get_productivity_score(self, days=7):
        """Calculate productivity score based on multiple factors"""
        week_stats = self.time_tracker.get_week_stats()
        data_stats = self.data_manager.get_statistics()
        
        # Factors
        time_factor = min(week_stats["total_time_minutes"] / (7 * 60), 1.0)  # Normalize to 7 hours/day
        questions_factor = min(data_stats["total_solved"] / 1000, 1.0)  # Normalize to 1000 questions
        progress_factor = data_stats["progress"] / 100
        completion_factor = data_stats["completed_topics"] / max(data_stats["total_topics"], 1)
        
        # Weighted score
        score = (
            time_factor * 0.25 +
            questions_factor * 0.25 +
            progress_factor * 0.25 +
            completion_factor * 0.25
        ) * 100
        
        return round(score, 1)
    
    def get_study_streak(self):
        """Calculate current study streak"""
        sessions = self.time_tracker.sessions
        if not sessions:
            return 0
        
        # Get all unique dates with sessions
        dates = set()
        for session in sessions.values():
            if session.get("start_time"):
                try:
                    date = session["start_time"][:10]
                    dates.add(date)
                except:
                    continue
        
        if not dates:
            return 0
        
        dates = sorted(list(dates), reverse=True)
        
        # Calculate streak
        streak = 0
        today = datetime.date.today()
        for i, date_str in enumerate(dates):
            try:
                date = datetime.date.fromisoformat(date_str)
                expected_date = today - datetime.timedelta(days=i)
                if date == expected_date:
                    streak += 1
                else:
                    break
            except:
                break
        
        return streak
    
    def get_weekly_trend(self):
        """Get weekly study trend"""
        today = datetime.date.today()
        weeks = []
        
        for i in range(4):  # Last 4 weeks
            week_start = today - datetime.timedelta(days=today.weekday() + (i * 7))
            week_end = week_start + datetime.timedelta(days=6)
            
            week_sessions = []
            for s in self.time_tracker.sessions.values():
                if s.get("start_time"):
                    try:
                        session_date = s["start_time"][:10]
                        if week_start.isoformat() <= session_date <= week_end.isoformat():
                            week_sessions.append(s)
                    except:
                        continue
            
            total_time = sum(s.get("duration_minutes", 0) for s in week_sessions)
            total_questions = sum(s.get("questions_solved", 0) for s in week_sessions)
            
            weeks.append({
                "week": f"Week {4-i}",
                "start_date": week_start.isoformat(),
                "end_date": week_end.isoformat(),
                "total_time": total_time,
                "total_questions": total_questions,
                "sessions": len(week_sessions)
            })
        
        return list(reversed(weeks))
    
    def get_subject_performance(self, subject_name):
        """Get performance metrics for a subject"""
        subject_data = self.data_manager.data.get(subject_name, {})
        subject_stats = self.time_tracker.get_subject_stats(subject_name, days=30)
        
        solved = subject_data.get('cozulen_soru', 0)
        target = subject_data.get('hedef_soru', 1)
        progress = (solved / target * 100) if target > 0 else 0
        
        # Calculate efficiency (questions per hour)
        total_hours = subject_stats["total_time_minutes"] / 60
        efficiency = solved / total_hours if total_hours > 0 else 0
        
        # Calculate completion rate
        topics = subject_data.get('konular', [])
        completed_topics = len([t for t in topics if t.get('durum') == 'Tamamlandı'])
        completion_rate = (completed_topics / len(topics) * 100) if topics else 0
        
        return {
            "progress_percentage": progress,
            "efficiency": round(efficiency, 2),  # questions per hour
            "completion_rate": completion_rate,
            "total_time_hours": round(total_hours, 2),
            "average_session_time": round(subject_stats.get("average_time_per_session", 0), 2),
            "consistency_score": self._calculate_consistency(subject_stats.get("daily_stats", {}))
        }
    
    def _calculate_consistency(self, daily_stats):
        """Calculate consistency score based on daily study patterns"""
        if not daily_stats:
            return 0
        
        # Count days with study
        study_days = len([d for d in daily_stats.values() if d.get("time", 0) > 0])
        total_days = len(daily_stats)
        
        consistency = (study_days / total_days * 100) if total_days > 0 else 0
        return round(consistency, 1)
    
    def get_recommendations(self):
        """Get study recommendations"""
        recommendations = []
        stats = self.data_manager.get_statistics()
        week_stats = self.time_tracker.get_week_stats()
        
        # Check for low activity
        if week_stats["total_time_minutes"] < 300:  # Less than 5 hours
            recommendations.append({
                "type": "warning",
                "message": "Bu hafta çalışma süreniz düşük. Daha fazla zaman ayırmayı düşünün.",
                "priority": "high"
            })
        
        # Check for incomplete goals
        upcoming_goals = self.goal_tracker.get_upcoming_goals(days=7)
        if upcoming_goals:
            recommendations.append({
                "type": "info",
                "message": f"{len(upcoming_goals)} hedefiniz yaklaşıyor. Hızlandırın!",
                "priority": "medium"
            })
        
        # Check for low progress subjects
        for subject_name, subject_data in self.data_manager.data.items():
            solved = subject_data.get('cozulen_soru', 0)
            target = subject_data.get('hedef_soru', 1)
            progress = (solved / target * 100) if target > 0 else 0
            
            if progress < 20 and target > 0:
                recommendations.append({
                    "type": "suggestion",
                    "message": f"{subject_name} dersinde ilerleme düşük. Daha fazla çalışma yapın.",
                    "priority": "low",
                    "subject": subject_name
                })
        
        return recommendations
