"""
Goal Tracker Module
Tracks and manages study goals and milestones
"""

import json
import os
import datetime
from ..config.constants import get_data_dir

class GoalTracker:
    """Tracks study goals and milestones"""
    
    def __init__(self):
        # Always get fresh path in case we're running from EXE
        self.goals_file = os.path.join(get_data_dir(), "goals.json")
        self.goals = self.load_goals()
    
    def load_goals(self):
        """Load goals"""
        if os.path.exists(self.goals_file):
            try:
                with open(self.goals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_goals(self):
        """Save goals"""
        try:
            os.makedirs(os.path.dirname(self.goals_file), exist_ok=True)
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump(self.goals, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def add_goal(self, subject_name, goal_type, target_value, target_date=None, description=""):
        """Add a new goal"""
        goal_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        goal = {
            "id": goal_id,
            "subject": subject_name,
            "type": goal_type,  # "questions", "time", "topics"
            "target_value": target_value,
            "current_value": 0,
            "target_date": target_date,
            "description": description,
            "created_date": datetime.date.today().isoformat(),
            "completed": False,
            "completed_date": None
        }
        
        if subject_name not in self.goals:
            self.goals[subject_name] = []
        
        self.goals[subject_name].append(goal)
        self.save_goals()
        return goal
    
    def update_goal_progress(self, subject_name, goal_type, current_value):
        """Update goal progress"""
        if subject_name in self.goals:
            for goal in self.goals[subject_name]:
                if goal["type"] == goal_type and not goal.get("completed", False):
                    goal["current_value"] = current_value
                    if current_value >= goal["target_value"]:
                        goal["completed"] = True
                        goal["completed_date"] = datetime.date.today().isoformat()
            self.save_goals()
    
    def get_goals(self, subject_name=None, include_completed=False):
        """Get goals for subject or all goals"""
        if subject_name:
            goals = self.goals.get(subject_name, [])
        else:
            goals = []
            for subject_goals in self.goals.values():
                goals.extend(subject_goals)
        
        if not include_completed:
            goals = [g for g in goals if not g.get("completed", False)]
        
        return sorted(goals, key=lambda x: x.get("target_date", ""))
    
    def get_upcoming_goals(self, days=7):
        """Get upcoming goals within specified days"""
        cutoff_date = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()
        upcoming = []
        
        for subject_goals in self.goals.values():
            for goal in subject_goals:
                if not goal.get("completed", False) and goal.get("target_date"):
                    if goal["target_date"] <= cutoff_date:
                        upcoming.append(goal)
        
        return sorted(upcoming, key=lambda x: x.get("target_date", ""))

