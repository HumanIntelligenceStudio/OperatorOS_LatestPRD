import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app import db
from models import FinancialData, User, SystemMetrics
from ai_providers import ai_manager

class FinancialAnalysisSystem:
    def __init__(self):
        self.ai_manager = ai_manager
    
    def process_bank_data(self, user_id: str, csv_data: str) -> Dict[str, Any]:
        """Process uploaded bank statement CSV data"""
        try:
            # Parse CSV data
            lines = csv_data.strip().split('\n')
            headers = lines[0].split(',')
            
            processed_entries = []
            
            for line in lines[1:]:
                values = line.split(',')
                if len(values) >= 4:  # Basic validation
                    entry = {
                        'date': values[0],
                        'description': values[1],
                        'amount': float(values[2]),
                        'category': values[3] if len(values) > 3 else 'other'
                    }
                    processed_entries.append(entry)
            
            # Store in database
            for entry in processed_entries:
                financial_data = FinancialData(
                    user_id=user_id,
                    data_type='bank_statement',
                    category=entry['category'],
                    amount=entry['amount'],
                    date=datetime.strptime(entry['date'], '%Y-%m-%d').date(),
                    description=entry['description']
                )
                db.session.add(financial_data)
            
            db.session.commit()
            
            # Generate AI analysis
            analysis_result = self._generate_financial_analysis(user_id, processed_entries)
            
            return {
                "success": True,
                "processed_entries": len(processed_entries),
                "analysis": analysis_result
            }
            
        except Exception as e:
            logging.error(f"Bank data processing failed: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}
    
    def _generate_financial_analysis(self, user_id: str, entries: List[Dict]) -> Dict[str, Any]:
        """Generate AI-powered financial analysis"""
        try:
            # Prepare data summary for AI analysis
            total_income = sum(entry['amount'] for entry in entries if entry['amount'] > 0)
            total_expenses = sum(abs(entry['amount']) for entry in entries if entry['amount'] < 0)
            net_income = total_income - total_expenses
            
            # Category breakdown
            categories = {}
            for entry in entries:
                category = entry['category']
                if category not in categories:
                    categories[category] = 0
                categories[category] += abs(entry['amount'])
            
            # Prepare context for AI analysis
            context = f"""
            Financial Data Analysis:
            
            Total Income: ${total_income:,.2f}
            Total Expenses: ${total_expenses:,.2f}
            Net Income: ${net_income:,.2f}
            
            Expense Categories:
            {chr(10).join(f"- {cat}: ${amount:,.2f}" for cat, amount in categories.items())}
            
            Transaction Count: {len(entries)}
            """
            
            prompt = f"""
            As a CFO-level financial analyst, provide comprehensive analysis of this financial data:
            
            {context}
            
            Provide detailed insights on:
            1. Financial health assessment
            2. Spending patterns and trends
            3. Areas for cost optimization
            4. Investment opportunities
            5. Risk assessment
            6. Actionable recommendations
            7. Digital nomad readiness score (1-10)
            
            Be specific and provide quantitative insights where possible.
            """
            
            response = self.ai_manager.generate_response(prompt, task_type="financial")
            
            if response.get("success"):
                # Store analysis result
                analysis_data = FinancialData(
                    user_id=user_id,
                    data_type='analysis',
                    category='cfo_analysis',
                    amount=net_income,
                    date=datetime.now().date(),
                    description='AI-generated financial analysis',
                    analysis_result=response["content"]
                )
                db.session.add(analysis_data)
                db.session.commit()
                
                return {
                    "success": True,
                    "analysis": response["content"],
                    "provider": response.get("provider"),
                    "financial_metrics": {
                        "total_income": total_income,
                        "total_expenses": total_expenses,
                        "net_income": net_income,
                        "categories": categories
                    }
                }
            
            return {"error": "Failed to generate analysis"}
            
        except Exception as e:
            logging.error(f"Financial analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def get_financial_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive financial dashboard data"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get financial data from last 12 months
            one_year_ago = datetime.now().date() - timedelta(days=365)
            financial_data = FinancialData.query.filter(
                FinancialData.user_id == user_id,
                FinancialData.date >= one_year_ago
            ).all()
            
            # Calculate key metrics
            total_income = sum(fd.amount for fd in financial_data if fd.amount > 0)
            total_expenses = sum(abs(fd.amount) for fd in financial_data if fd.amount < 0)
            net_income = total_income - total_expenses
            
            # Monthly trends
            monthly_data = self._calculate_monthly_trends(financial_data)
            
            # Category analysis
            category_breakdown = self._analyze_categories(financial_data)
            
            # Get latest analysis
            latest_analysis = FinancialData.query.filter(
                FinancialData.user_id == user_id,
                FinancialData.data_type == 'analysis'
            ).order_by(FinancialData.created_at.desc()).first()
            
            return {
                "user": user,
                "total_income": round(total_income, 2),
                "total_expenses": round(total_expenses, 2),
                "net_income": round(net_income, 2),
                "monthly_trends": monthly_data,
                "category_breakdown": category_breakdown,
                "latest_analysis": latest_analysis.analysis_result if latest_analysis else None,
                "data_points": len(financial_data)
            }
            
        except Exception as e:
            logging.error(f"Financial dashboard failed: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_monthly_trends(self, financial_data: List[FinancialData]) -> Dict[str, Any]:
        """Calculate monthly financial trends"""
        try:
            monthly_data = {}
            
            for fd in financial_data:
                month_key = fd.date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'income': 0, 'expenses': 0}
                
                if fd.amount > 0:
                    monthly_data[month_key]['income'] += fd.amount
                else:
                    monthly_data[month_key]['expenses'] += abs(fd.amount)
            
            # Calculate net income for each month
            for month in monthly_data:
                monthly_data[month]['net'] = monthly_data[month]['income'] - monthly_data[month]['expenses']
            
            return monthly_data
            
        except Exception as e:
            logging.error(f"Monthly trends calculation failed: {str(e)}")
            return {}
    
    def _analyze_categories(self, financial_data: List[FinancialData]) -> Dict[str, float]:
        """Analyze spending by category"""
        try:
            categories = {}
            
            for fd in financial_data:
                if fd.amount < 0:  # Only expenses
                    category = fd.category or 'other'
                    if category not in categories:
                        categories[category] = 0
                    categories[category] += abs(fd.amount)
            
            return categories
            
        except Exception as e:
            logging.error(f"Category analysis failed: {str(e)}")
            return {}
    
    def generate_investment_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate AI-powered investment recommendations"""
        try:
            # Get user's financial data
            dashboard_data = self.get_financial_dashboard(user_id)
            
            if "error" in dashboard_data:
                return dashboard_data
            
            context = f"""
            Financial Profile:
            - Net Income: ${dashboard_data['net_income']:,.2f}
            - Total Income: ${dashboard_data['total_income']:,.2f}
            - Total Expenses: ${dashboard_data['total_expenses']:,.2f}
            - Data Points: {dashboard_data['data_points']}
            
            Category Breakdown:
            {chr(10).join(f"- {cat}: ${amount:,.2f}" for cat, amount in dashboard_data['category_breakdown'].items())}
            """
            
            prompt = f"""
            As an investment advisor, provide personalized investment recommendations based on this financial profile:
            
            {context}
            
            Provide specific recommendations for:
            1. Emergency fund planning
            2. Short-term investment opportunities
            3. Long-term wealth building strategies
            4. Risk assessment and portfolio allocation
            5. Tax optimization strategies
            6. Passive income opportunities
            7. Digital nomad-friendly investment options
            
            Include specific dollar amounts and timeframes where appropriate.
            """
            
            response = self.ai_manager.generate_response(prompt, task_type="financial")
            
            if response.get("success"):
                # Store investment recommendations
                investment_data = FinancialData(
                    user_id=user_id,
                    data_type='investment_recommendation',
                    category='investment_advice',
                    amount=dashboard_data['net_income'],
                    date=datetime.now().date(),
                    description='AI-generated investment recommendations',
                    analysis_result=response["content"]
                )
                db.session.add(investment_data)
                db.session.commit()
                
                return {
                    "success": True,
                    "recommendations": response["content"],
                    "provider": response.get("provider"),
                    "financial_context": dashboard_data
                }
            
            return {"error": "Failed to generate investment recommendations"}
            
        except Exception as e:
            logging.error(f"Investment recommendations failed: {str(e)}")
            return {"error": str(e)}
    
    def generate_nomad_readiness_score(self, user_id: str) -> Dict[str, Any]:
        """Generate digital nomad readiness score"""
        try:
            dashboard_data = self.get_financial_dashboard(user_id)
            
            if "error" in dashboard_data:
                return dashboard_data
            
            context = f"""
            Financial Profile for Digital Nomad Assessment:
            - Net Income: ${dashboard_data['net_income']:,.2f}
            - Monthly Average Income: ${dashboard_data['net_income']/12:,.2f}
            - Monthly Average Expenses: ${dashboard_data['total_expenses']/12:,.2f}
            - Financial Stability: {dashboard_data['data_points']} data points
            """
            
            prompt = f"""
            As a digital nomad financial advisor, assess this person's readiness for the nomadic lifestyle:
            
            {context}
            
            Provide:
            1. Digital nomad readiness score (1-10)
            2. Financial stability assessment
            3. Recommended savings targets
            4. Location-specific budget recommendations
            5. Income diversification strategies
            6. Risk mitigation plan
            7. Timeline for nomad transition
            
            Be specific about financial requirements and actionable steps.
            """
            
            response = self.ai_manager.generate_response(prompt, task_type="financial")
            
            if response.get("success"):
                return {
                    "success": True,
                    "assessment": response["content"],
                    "provider": response.get("provider"),
                    "financial_data": dashboard_data
                }
            
            return {"error": "Failed to generate nomad readiness assessment"}
            
        except Exception as e:
            logging.error(f"Nomad readiness assessment failed: {str(e)}")
            return {"error": str(e)}

# Global financial analysis system
financial_system = FinancialAnalysisSystem()
