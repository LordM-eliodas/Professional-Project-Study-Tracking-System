"""
Export Manager Module
Handles data export in various formats (JSON, Excel, PDF)
"""

import json
import os
import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ExportManager:
    """Manages data export in various formats"""
    
    def __init__(self, data_manager, time_tracker, notes_manager, goal_tracker):
        self.data_manager = data_manager
        self.time_tracker = time_tracker
        self.notes_manager = notes_manager
        self.goal_tracker = goal_tracker
    
    def export_to_json(self, file_path):
        """Export all data to JSON"""
        export_data = {
            "study_data": self.data_manager.data,
            "study_sessions": self.time_tracker.sessions,
            "notes": self.notes_manager.notes,
            "goals": self.goal_tracker.goals,
            "export_date": datetime.datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)
        return True
    
    def export_to_excel(self, file_path):
        """Export data to Excel file"""
        if not PANDAS_AVAILABLE:
            return False, "pandas library is not installed"
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Study data sheet
                study_data = []
                for subject, data in self.data_manager.data.items():
                    study_data.append({
                        "Subject": subject,
                        "Solved Questions": data.get('cozulen_soru', 0),
                        "Target Questions": data.get('hedef_soru', 0),
                        "Progress %": round((data.get('cozulen_soru', 0) / data.get('hedef_soru', 1) * 100) if data.get('hedef_soru', 1) > 0 else 0, 2),
                        "Last Study": data.get('son_calisma_tarihi', ''),
                        "Topics Count": len(data.get('konular', []))
                    })
                
                df_study = pd.DataFrame(study_data)
                df_study.to_excel(writer, sheet_name='Study Data', index=False)
                
                # Sessions sheet
                sessions_data = []
                for session_id, session in self.time_tracker.sessions.items():
                    sessions_data.append({
                        "Date": session.get('start_time', '')[:10],
                        "Subject": session.get('subject', ''),
                        "Duration (min)": session.get('duration_minutes', 0),
                        "Questions Solved": session.get('questions_solved', 0),
                        "Notes": session.get('notes', '')
                    })
                
                if sessions_data:
                    df_sessions = pd.DataFrame(sessions_data)
                    df_sessions.to_excel(writer, sheet_name='Study Sessions', index=False)
                
                # Goals sheet
                goals_data = []
                for subject, goals in self.goal_tracker.goals.items():
                    for goal in goals:
                        goals_data.append({
                            "Subject": subject,
                            "Type": goal.get('type', ''),
                            "Target": goal.get('target_value', 0),
                            "Current": goal.get('current_value', 0),
                            "Progress %": round((goal.get('current_value', 0) / goal.get('target_value', 1) * 100) if goal.get('target_value', 1) > 0 else 0, 2),
                            "Target Date": goal.get('target_date', ''),
                            "Completed": goal.get('completed', False)
                        })
                
                if goals_data:
                    df_goals = pd.DataFrame(goals_data)
                    df_goals.to_excel(writer, sheet_name='Goals', index=False)
            
            return True, "Export successful"
        except Exception as e:
            return False, str(e)
    
    def export_to_pdf(self, file_path):
        """Export report to PDF"""
        if not REPORTLAB_AVAILABLE:
            return False, "reportlab library is not installed"
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=30,
            )
            story.append(Paragraph("Crono Ders Takip Sistemi - Study Report", title_style))
            story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Statistics
            stats = self.data_manager.get_statistics()
            stats_data = [
                ['Metric', 'Value'],
                ['Total Solved Questions', f"{stats['total_solved']:,}"],
                ['Total Target Questions', f"{stats['total_target']:,}"],
                ['Overall Progress', f"{stats['progress']:.1f}%"],
                ['Total Topics', f"{stats['total_topics']}"],
                ['Completed Topics', f"{stats['completed_topics']}"],
            ]
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(Paragraph("Statistics", styles['Heading2']))
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Subject details
            story.append(Paragraph("Subject Details", styles['Heading2']))
            subject_data = []
            subject_data.append(['Subject', 'Solved', 'Target', 'Progress %', 'Topics'])
            
            for subject, data in self.data_manager.data.items():
                solved = data.get('cozulen_soru', 0)
                target = data.get('hedef_soru', 1)
                progress = round((solved / target * 100) if target > 0 else 0, 1)
                topics = len(data.get('konular', []))
                subject_data.append([subject, str(solved), str(target), f"{progress}%", str(topics)])
            
            subject_table = Table(subject_data)
            subject_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(subject_table)
            
            doc.build(story)
            return True, "PDF export successful"
        except Exception as e:
            return False, str(e)

