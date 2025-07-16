import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app import db
from models import Goal, Task, User
from ai_providers import ai_manager

class GoalAchievementSystem:
    def __init__(self):
        self.ai_manager = ai_manager
    
    def create_goal(self, user_id: str, title: str, description: str, target_date: datetime = None, priority: str = "medium") -> Goal:
        """Create a new goal with AI-powered task breakdown"""
        try:
            goal = Goal(
                user_id=user_id,
                title=title,
                description=description,
                target_date=target_date or datetime.now() + timedelta(days=90),
                priority=priority
            )
            db.session.add(goal)
            db.session.commit()
            
            # Generate AI-powered task breakdown
            self._generate_task_breakdown(goal)
            
            return goal
            
        except Exception as e:
            logging.error(f"Failed to create goal: {str(e)}")
            db.session.rollback()
            raise
    
    def _generate_task_breakdown(self, goal: Goal) -> List[Task]:
        """Generate AI-powered task breakdown for a goal"""
        try:
            timeline = self._calculate_timeline(goal.target_date)
            breakdown_response = self.ai_manager.get_goal_breakdown(goal.description, timeline)
            
            if not breakdown_response.get("success"):
                logging.error(f"Failed to generate task breakdown: {breakdown_response.get('error')}")
                return []
            
            # Parse AI response and create tasks
            tasks = self._parse_task_breakdown(breakdown_response["content"], goal.id)
            
            return tasks
            
        except Exception as e:
            logging.error(f"Task breakdown generation failed: {str(e)}")
            return []
    
    def _calculate_timeline(self, target_date: datetime) -> str:
        """Calculate timeline string for AI processing"""
        if not target_date:
            return "3 months"
        
        days_remaining = (target_date - datetime.now()).days
        
        if days_remaining <= 30:
            return "1 month"
        elif days_remaining <= 90:
            return "3 months"
        elif days_remaining <= 180:
            return "6 months"
        else:
            return "1 year"
    
    def _parse_task_breakdown(self, ai_response: str, goal_id: int) -> List[Task]:
        """Parse AI response and create task objects"""
        tasks = []
        
        try:
            # Simple parsing - in production, this would be more sophisticated
            lines = ai_response.split('\n')
            current_task = None
            
            for line in lines:
                line = line.strip()
                
                # Look for task indicators
                if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                    task_title = line[2:].strip()
                    
                    if task_title and len(task_title) > 3:
                        task = Task(
                            goal_id=goal_id,
                            title=task_title[:200],  # Truncate if too long
                            description=task_title,
                            priority="medium",
                            estimated_hours=self._estimate_task_hours(task_title)
                        )
                        db.session.add(task)
                        tasks.append(task)
            
            db.session.commit()
            
        except Exception as e:
            logging.error(f"Task parsing failed: {str(e)}")
            db.session.rollback()
        
        return tasks
    
    def _estimate_task_hours(self, task_title: str) -> int:
        """Estimate hours for a task based on keywords"""
        keywords = task_title.lower()
        
        if any(word in keywords for word in ['research', 'analyze', 'study', 'learn']):
            return 4
        elif any(word in keywords for word in ['create', 'build', 'develop', 'design']):
            return 8
        elif any(word in keywords for word in ['plan', 'organize', 'schedule']):
            return 2
        elif any(word in keywords for word in ['implement', 'execute', 'complete']):
            return 6
        else:
            return 3
    
    def update_goal_progress(self, goal_id: int) -> float:
        """Update goal progress based on completed tasks"""
        try:
            goal = Goal.query.get(goal_id)
            if not goal:
                return 0.0
            
            tasks = Task.query.filter_by(goal_id=goal_id).all()
            if not tasks:
                return 0.0
            
            completed_tasks = sum(1 for task in tasks if task.completed)
            progress = (completed_tasks / len(tasks)) * 100
            
            goal.completion_percentage = int(progress)
            db.session.commit()
            
            return progress
            
        except Exception as e:
            logging.error(f"Progress update failed: {str(e)}")
            return 0.0
    
    def get_goal_insights(self, goal_id: int) -> Dict[str, Any]:
        """Get AI-powered insights about goal progress"""
        try:
            goal = Goal.query.get(goal_id)
            if not goal:
                return {"error": "Goal not found"}
            
            tasks = Task.query.filter_by(goal_id=goal_id).all()
            
            # Prepare context for AI analysis
            context = f"""
            Goal: {goal.title}
            Description: {goal.description}
            Target Date: {goal.target_date}
            Current Progress: {goal.completion_percentage}%
            
            Tasks Status:
            """
            
            for task in tasks:
                status = "Completed" if task.completed else "Pending"
                context += f"- {task.title}: {status}\n"
            
            prompt = f"""
            As a goal achievement expert, analyze this goal and provide insights:
            
            {context}
            
            Please provide:
            1. Progress assessment
            2. Potential bottlenecks or risks
            3. Recommendations for improvement
            4. Motivation and encouragement
            5. Next priority actions
            
            Be specific and actionable.
            """
            
            response = self.ai_manager.generate_response(prompt, task_type="analysis")
            
            return {
                "success": response.get("success", False),
                "insights": response.get("content", ""),
                "provider": response.get("provider", ""),
                "goal_progress": goal.completion_percentage
            }
            
        except Exception as e:
            logging.error(f"Goal insights failed: {str(e)}")
            return {"error": str(e)}
    
    def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}
            
            goals = Goal.query.filter_by(user_id=user_id).all()
            
            # Calculate statistics
            total_goals = len(goals)
            active_goals = len([g for g in goals if g.status == 'active'])
            completed_goals = len([g for g in goals if g.status == 'completed'])
            
            avg_progress = 0
            if goals:
                avg_progress = sum(g.completion_percentage for g in goals) / len(goals)
            
            # Get recent tasks
            recent_tasks = []
            for goal in goals:
                tasks = Task.query.filter_by(goal_id=goal.id).order_by(Task.created_at.desc()).limit(5).all()
                recent_tasks.extend(tasks)
            
            recent_tasks.sort(key=lambda x: x.created_at, reverse=True)
            recent_tasks = recent_tasks[:10]
            
            # Get AI conversation data
            from models import AIConversation
            ai_conversations = AIConversation.query.filter_by(user_id=user_id).all()
            total_ai_cost = sum(conv.cost or 0 for conv in ai_conversations)
            
            return {
                "user": user,
                "total_goals": total_goals,
                "active_goals": active_goals,
                "completed_goals": completed_goals,
                "average_progress": round(avg_progress, 1),
                "goals": goals,
                "recent_tasks": recent_tasks,
                "ai_conversations": len(ai_conversations),
                "total_ai_cost": total_ai_cost
            }
            
        except Exception as e:
            logging.error(f"Dashboard data retrieval failed: {str(e)}")
            return {"error": str(e)}
    
    def complete_task(self, task_id: int, user_id: str) -> Dict[str, Any]:
        """Mark a task as completed and update goal progress"""
        try:
            task = Task.query.get(task_id)
            if not task:
                return {"error": "Task not found"}
            
            goal = Goal.query.get(task.goal_id)
            if not goal or goal.user_id != user_id:
                return {"error": "Unauthorized"}
            
            task.completed = True
            task.updated_at = datetime.now()
            db.session.commit()
            
            # Update goal progress
            new_progress = self.update_goal_progress(task.goal_id)
            
            return {
                "success": True,
                "task": task,
                "goal_progress": new_progress,
                "message": f"Task completed! Goal is now {new_progress:.1f}% complete."
            }
            
        except Exception as e:
            logging.error(f"Task completion failed: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}

# Global goal achievement system
goal_system = GoalAchievementSystem()
