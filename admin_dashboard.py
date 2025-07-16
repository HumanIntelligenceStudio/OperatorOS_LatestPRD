import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app import db
from models import User, Goal, Task, AIConversation, BusinessProcess, FinancialData, ServiceTemplate, Payment, SystemMetrics
from ai_providers import ai_manager

class AdminDashboardSystem:
    def __init__(self):
        self.ai_manager = ai_manager
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get comprehensive admin dashboard overview"""
        try:
            # User statistics
            total_users = User.query.count()
            new_users_today = User.query.filter(
                User.created_at >= datetime.now().date()
            ).count()
            
            # Goal and task statistics
            total_goals = Goal.query.count()
            active_goals = Goal.query.filter_by(status='active').count()
            completed_goals = Goal.query.filter_by(status='completed').count()
            total_tasks = Task.query.count()
            completed_tasks = Task.query.filter_by(completed=True).count()
            
            # AI usage statistics
            total_conversations = AIConversation.query.count()
            conversations_today = AIConversation.query.filter(
                AIConversation.created_at >= datetime.now().date()
            ).count()
            
            # Business process statistics
            total_processes = BusinessProcess.query.count()
            active_processes = BusinessProcess.query.filter_by(status='active').count()
            total_revenue = db.session.query(db.func.sum(BusinessProcess.revenue_generated)).scalar() or 0
            
            # Financial data statistics
            total_financial_entries = FinancialData.query.count()
            
            # Service template statistics
            total_templates = ServiceTemplate.query.count()
            template_usage = db.session.query(db.func.sum(ServiceTemplate.usage_count)).scalar() or 0
            
            # Payment statistics
            total_payments = Payment.query.count()
            successful_payments = Payment.query.filter_by(status='completed').count()
            total_payment_amount = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
            
            return {
                "users": {
                    "total": total_users,
                    "new_today": new_users_today,
                    "growth_rate": self._calculate_growth_rate("users")
                },
                "goals": {
                    "total": total_goals,
                    "active": active_goals,
                    "completed": completed_goals,
                    "completion_rate": (completed_goals / total_goals * 100) if total_goals > 0 else 0
                },
                "tasks": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                },
                "ai_usage": {
                    "total_conversations": total_conversations,
                    "conversations_today": conversations_today,
                    "provider_distribution": self._get_provider_distribution()
                },
                "business_processes": {
                    "total": total_processes,
                    "active": active_processes,
                    "total_revenue": round(total_revenue, 2)
                },
                "financial_data": {
                    "total_entries": total_financial_entries
                },
                "service_templates": {
                    "total": total_templates,
                    "usage_count": template_usage
                },
                "payments": {
                    "total": total_payments,
                    "successful": successful_payments,
                    "total_amount": round(total_payment_amount, 2),
                    "success_rate": (successful_payments / total_payments * 100) if total_payments > 0 else 0
                },
                "system_health": self._get_system_health()
            }
            
        except Exception as e:
            logging.error(f"Admin dashboard overview failed: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_growth_rate(self, metric_type: str) -> float:
        """Calculate growth rate for a specific metric"""
        try:
            if metric_type == "users":
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                
                today_count = User.query.filter(User.created_at >= today).count()
                yesterday_count = User.query.filter(
                    User.created_at >= yesterday,
                    User.created_at < today
                ).count()
                
                if yesterday_count > 0:
                    return round(((today_count - yesterday_count) / yesterday_count) * 100, 2)
                
            return 0.0
            
        except Exception as e:
            logging.error(f"Growth rate calculation failed: {str(e)}")
            return 0.0
    
    def _get_provider_distribution(self) -> Dict[str, int]:
        """Get AI provider usage distribution"""
        try:
            providers = db.session.query(
                AIConversation.provider,
                db.func.count(AIConversation.id)
            ).group_by(AIConversation.provider).all()
            
            return {provider: count for provider, count in providers}
            
        except Exception as e:
            logging.error(f"Provider distribution calculation failed: {str(e)}")
            return {}
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # Check database connectivity
            db_health = True
            try:
                db.session.execute(db.text("SELECT 1"))
            except:
                db_health = False
            
            # Check AI providers
            ai_health = len(self.ai_manager.providers) > 0
            
            # Get recent error metrics
            error_metrics = SystemMetrics.query.filter(
                SystemMetrics.metric_type == "error",
                SystemMetrics.timestamp >= datetime.now() - timedelta(hours=24)
            ).count()
            
            return {
                "database": db_health,
                "ai_providers": ai_health,
                "error_count_24h": error_metrics,
                "status": "healthy" if db_health and ai_health and error_metrics < 10 else "degraded"
            }
            
        except Exception as e:
            logging.error(f"System health check failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def get_user_analytics(self, limit: int = 100) -> Dict[str, Any]:
        """Get detailed user analytics"""
        try:
            # Get user activity data
            users = User.query.order_by(User.created_at.desc()).limit(limit).all()
            
            # Calculate user engagement metrics
            user_analytics = []
            for user in users:
                goals_count = Goal.query.filter_by(user_id=user.id).count()
                conversations_count = AIConversation.query.filter_by(user_id=user.id).count()
                payments_count = Payment.query.filter_by(user_id=user.id).count()
                
                user_analytics.append({
                    "user": user,
                    "goals": goals_count,
                    "conversations": conversations_count,
                    "payments": payments_count,
                    "engagement_score": goals_count * 2 + conversations_count + payments_count * 5
                })
            
            # Sort by engagement score
            user_analytics.sort(key=lambda x: x["engagement_score"], reverse=True)
            
            return {
                "user_analytics": user_analytics,
                "total_users": len(users),
                "average_engagement": sum(u["engagement_score"] for u in user_analytics) / len(user_analytics) if user_analytics else 0
            }
            
        except Exception as e:
            logging.error(f"User analytics failed: {str(e)}")
            return {"error": str(e)}
    
    def get_ai_usage_analytics(self) -> Dict[str, Any]:
        """Get AI usage analytics"""
        try:
            # Get conversation statistics
            conversations = AIConversation.query.all()
            
            # Provider usage
            provider_stats = {}
            model_stats = {}
            total_cost = 0
            total_tokens = 0
            
            for conv in conversations:
                # Provider statistics
                provider = conv.provider
                if provider not in provider_stats:
                    provider_stats[provider] = {"count": 0, "cost": 0, "tokens": 0}
                
                provider_stats[provider]["count"] += 1
                provider_stats[provider]["cost"] += conv.cost or 0
                provider_stats[provider]["tokens"] += conv.tokens_used or 0
                
                # Model statistics
                model = conv.model
                if model not in model_stats:
                    model_stats[model] = {"count": 0, "cost": 0}
                
                model_stats[model]["count"] += 1
                model_stats[model]["cost"] += conv.cost or 0
                
                total_cost += conv.cost or 0
                total_tokens += conv.tokens_used or 0
            
            # Get clarity ratings
            clarity_ratings = AIConversation.query.filter(
                AIConversation.clarity_rating.isnot(None)
            ).all()
            
            avg_clarity = sum(c.clarity_rating for c in clarity_ratings) / len(clarity_ratings) if clarity_ratings else 0
            
            return {
                "total_conversations": len(conversations),
                "provider_stats": provider_stats,
                "model_stats": model_stats,
                "total_cost": round(total_cost, 2),
                "total_tokens": total_tokens,
                "average_clarity": round(avg_clarity, 2),
                "clarity_ratings_count": len(clarity_ratings)
            }
            
        except Exception as e:
            logging.error(f"AI usage analytics failed: {str(e)}")
            return {"error": str(e)}
    
    def get_revenue_analytics(self) -> Dict[str, Any]:
        """Get revenue analytics"""
        try:
            # Business process revenue
            processes = BusinessProcess.query.all()
            process_revenue = sum(p.revenue_generated for p in processes)
            
            # Payment revenue
            payments = Payment.query.filter_by(status='completed').all()
            payment_revenue = sum(p.amount for p in payments)
            
            total_revenue = process_revenue + payment_revenue
            
            # Monthly revenue trends
            monthly_revenue = self._calculate_monthly_revenue()
            
            # Revenue by source
            revenue_sources = {
                "automated_processes": round(process_revenue, 2),
                "direct_payments": round(payment_revenue, 2)
            }
            
            return {
                "total_revenue": round(total_revenue, 2),
                "process_revenue": round(process_revenue, 2),
                "payment_revenue": round(payment_revenue, 2),
                "monthly_trends": monthly_revenue,
                "revenue_sources": revenue_sources
            }
            
        except Exception as e:
            logging.error(f"Revenue analytics failed: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_monthly_revenue(self) -> Dict[str, float]:
        """Calculate monthly revenue trends"""
        try:
            payments = Payment.query.filter_by(status='completed').all()
            
            monthly_data = {}
            
            for payment in payments:
                month_key = payment.created_at.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += payment.amount
            
            return monthly_data
            
        except Exception as e:
            logging.error(f"Monthly revenue calculation failed: {str(e)}")
            return {}
    
    def generate_admin_report(self) -> Dict[str, Any]:
        """Generate comprehensive admin report"""
        try:
            overview = self.get_dashboard_overview()
            user_analytics = self.get_user_analytics()
            ai_analytics = self.get_ai_usage_analytics()
            revenue_analytics = self.get_revenue_analytics()
            
            # Generate AI-powered insights
            context = f"""
            System Overview:
            - Total Users: {overview['users']['total']}
            - Total Goals: {overview['goals']['total']}
            - Total AI Conversations: {overview['ai_usage']['total_conversations']}
            - Total Revenue: ${overview['business_processes']['total_revenue']:,.2f}
            
            User Engagement:
            - Average Engagement Score: {user_analytics.get('average_engagement', 0):.2f}
            
            AI Usage:
            - Total Cost: ${ai_analytics.get('total_cost', 0):,.2f}
            - Average Clarity Rating: {ai_analytics.get('average_clarity', 0):.2f}
            
            Revenue:
            - Total Revenue: ${revenue_analytics.get('total_revenue', 0):,.2f}
            """
            
            prompt = f"""
            As a business analytics expert, provide executive insights on this platform's performance:
            
            {context}
            
            Provide analysis on:
            1. Platform growth and user engagement
            2. AI usage efficiency and cost optimization
            3. Revenue generation and opportunities
            4. Key performance indicators and trends
            5. Recommendations for improvement
            6. Risk assessment and mitigation strategies
            
            Be specific and actionable in your recommendations.
            """
            
            ai_insights = self.ai_manager.generate_response(prompt, task_type="analysis")
            
            return {
                "overview": overview,
                "user_analytics": user_analytics,
                "ai_analytics": ai_analytics,
                "revenue_analytics": revenue_analytics,
                "ai_insights": ai_insights.get("content", "Analysis not available"),
                "report_generated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Admin report generation failed: {str(e)}")
            return {"error": str(e)}

# Global admin dashboard system
admin_dashboard = AdminDashboardSystem()
