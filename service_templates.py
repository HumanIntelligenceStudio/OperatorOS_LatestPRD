import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app import db
from models import ServiceTemplate, SystemMetrics
from ai_providers import ai_manager

class ServiceTemplateSystem:
    def __init__(self):
        self.ai_manager = ai_manager
        self.template_categories = {
            "business_consulting": "Business Consulting",
            "marketing_strategy": "Marketing Strategy",
            "financial_planning": "Financial Planning",
            "tech_solutions": "Technology Solutions",
            "content_creation": "Content Creation",
            "automation_services": "Automation Services",
            "coaching_mentoring": "Coaching & Mentoring",
            "legal_services": "Legal Services"
        }
    
    def create_service_template(self, name: str, category: str, description: str, 
                              base_price: float = 0.0, automation_level: str = "manual") -> ServiceTemplate:
        """Create a new service template with AI-generated content"""
        try:
            template = ServiceTemplate(
                name=name,
                category=category,
                description=description,
                price=base_price,
                automation_level=automation_level,
                template_content=""  # Will be populated by AI
            )
            
            # Generate AI-powered template content
            content = self._generate_template_content(name, category, description)
            template.template_content = content
            
            db.session.add(template)
            db.session.commit()
            
            return template
            
        except Exception as e:
            logging.error(f"Failed to create service template: {str(e)}")
            db.session.rollback()
            raise
    
    def _generate_template_content(self, name: str, category: str, description: str) -> str:
        """Generate AI-powered service template content"""
        try:
            prompt = f"""
            As a professional services expert, create a comprehensive service template for:
            
            Service Name: {name}
            Category: {category}
            Description: {description}
            
            Create a detailed template that includes:
            1. Service overview and value proposition
            2. Detailed scope of work
            3. Deliverables and timeline
            4. Pricing structure and packages
            5. Client requirements and prerequisites
            6. Quality assurance processes
            7. Communication protocols
            8. Terms and conditions
            
            Format this as a professional service template that can be customized for different clients.
            """
            
            response = self.ai_manager.generate_response(prompt, task_type="planning")
            
            if response.get("success"):
                return response["content"]
            else:
                return "Template content generation failed. Please update manually."
            
        except Exception as e:
            logging.error(f"Template content generation failed: {str(e)}")
            return "Template content generation failed. Please update manually."
    
    def get_service_catalog(self) -> Dict[str, Any]:
        """Get comprehensive service catalog"""
        try:
            templates = ServiceTemplate.query.all()
            
            # Group by category
            catalog = {}
            for template in templates:
                category = template.category
                if category not in catalog:
                    catalog[category] = []
                catalog[category].append(template)
            
            # Calculate statistics
            total_templates = len(templates)
            total_usage = sum(t.usage_count for t in templates)
            avg_price = sum(t.price for t in templates) / len(templates) if templates else 0
            
            return {
                "catalog": catalog,
                "categories": self.template_categories,
                "total_templates": total_templates,
                "total_usage": total_usage,
                "average_price": round(avg_price, 2)
            }
            
        except Exception as e:
            logging.error(f"Service catalog retrieval failed: {str(e)}")
            return {"error": str(e)}
    
    def customize_template(self, template_id: int, client_requirements: str) -> Dict[str, Any]:
        """Customize a service template for specific client requirements"""
        try:
            template = ServiceTemplate.query.get(template_id)
            if not template:
                return {"error": "Template not found"}
            
            prompt = f"""
            As a professional services consultant, customize this service template for a specific client:
            
            Original Template:
            {template.template_content}
            
            Client Requirements:
            {client_requirements}
            
            Customize the template to:
            1. Address specific client needs
            2. Adjust scope and deliverables
            3. Modify pricing based on requirements
            4. Update timeline and milestones
            5. Include client-specific terms
            
            Provide a fully customized service proposal.
            """
            
            response = self.ai_manager.generate_response(prompt, task_type="planning")
            
            if response.get("success"):
                # Track usage
                template.usage_count += 1
                db.session.commit()
                
                return {
                    "success": True,
                    "customized_template": response["content"],
                    "original_template": template,
                    "provider": response.get("provider")
                }
            
            return {"error": "Failed to customize template"}
            
        except Exception as e:
            logging.error(f"Template customization failed: {str(e)}")
            return {"error": str(e)}
    
    def generate_proposal(self, template_id: int, client_name: str, 
                         project_details: str, budget_range: str = None) -> Dict[str, Any]:
        """Generate a professional proposal based on template"""
        try:
            template = ServiceTemplate.query.get(template_id)
            if not template:
                return {"error": "Template not found"}
            
            prompt = f"""
            As a professional services consultant, create a compelling proposal for:
            
            Client: {client_name}
            Project Details: {project_details}
            Budget Range: {budget_range or "Not specified"}
            
            Base Service Template:
            {template.name} - {template.description}
            
            Template Content:
            {template.template_content}
            
            Create a professional proposal that includes:
            1. Executive summary
            2. Understanding of client needs
            3. Proposed solution and approach
            4. Detailed scope and deliverables
            5. Timeline and milestones
            6. Investment and payment terms
            7. Why choose us section
            8. Next steps
            
            Make it compelling and professional.
            """
            
            response = self.ai_manager.generate_response(prompt, task_type="creative")
            
            if response.get("success"):
                # Track usage
                template.usage_count += 1
                db.session.commit()
                
                # Log proposal generation
                self._log_proposal_generation(template_id, client_name)
                
                return {
                    "success": True,
                    "proposal": response["content"],
                    "template_used": template,
                    "client_name": client_name,
                    "provider": response.get("provider")
                }
            
            return {"error": "Failed to generate proposal"}
            
        except Exception as e:
            logging.error(f"Proposal generation failed: {str(e)}")
            return {"error": str(e)}
    
    def create_default_templates(self):
        """Create default service templates for common services"""
        try:
            default_templates = [
                {
                    "name": "Business Strategy Consulting",
                    "category": "business_consulting",
                    "description": "Comprehensive business strategy development and implementation",
                    "base_price": 5000.0,
                    "automation_level": "semi-automated"
                },
                {
                    "name": "Digital Marketing Audit",
                    "category": "marketing_strategy",
                    "description": "Complete digital marketing analysis and optimization recommendations",
                    "base_price": 2500.0,
                    "automation_level": "automated"
                },
                {
                    "name": "Financial Planning & Analysis",
                    "category": "financial_planning",
                    "description": "Personal and business financial planning services",
                    "base_price": 3500.0,
                    "automation_level": "semi-automated"
                },
                {
                    "name": "Website Development & Optimization",
                    "category": "tech_solutions",
                    "description": "Custom website development and performance optimization",
                    "base_price": 4500.0,
                    "automation_level": "manual"
                },
                {
                    "name": "Content Creation Package",
                    "category": "content_creation",
                    "description": "Professional content creation for marketing and communications",
                    "base_price": 2000.0,
                    "automation_level": "automated"
                },
                {
                    "name": "Business Process Automation",
                    "category": "automation_services",
                    "description": "Workflow automation and efficiency optimization",
                    "base_price": 6000.0,
                    "automation_level": "automated"
                },
                {
                    "name": "AI Implementation & Integration Consulting",
                    "category": "tech_solutions",
                    "description": "Complete AI solution implementation for businesses - from strategy to deployment",
                    "base_price": 5000.0,
                    "automation_level": "semi-automated"
                }
            ]
            
            for template_data in default_templates:
                existing = ServiceTemplate.query.filter_by(name=template_data["name"]).first()
                if not existing:
                    self.create_service_template(**template_data)
            
            logging.info("Default service templates created")
            
        except Exception as e:
            logging.error(f"Failed to create default templates: {str(e)}")
    
    def _log_proposal_generation(self, template_id: int, client_name: str):
        """Log proposal generation for analytics"""
        try:
            metric = SystemMetrics(
                metric_type="proposal_generated",
                value=1.0,
                metadata=f"Template ID: {template_id}, Client: {client_name}"
            )
            db.session.add(metric)
            db.session.commit()
            
        except Exception as e:
            logging.error(f"Failed to log proposal generation: {str(e)}")
    
    def get_template_performance(self, template_id: int) -> Dict[str, Any]:
        """Get performance analytics for a specific template"""
        try:
            template = ServiceTemplate.query.get(template_id)
            if not template:
                return {"error": "Template not found"}
            
            # Get usage metrics
            usage_metrics = SystemMetrics.query.filter(
                SystemMetrics.metric_type == "proposal_generated",
                SystemMetrics.metadata.contains(f"Template ID: {template_id}")
            ).all()
            
            return {
                "template": template,
                "total_usage": template.usage_count,
                "recent_usage": len(usage_metrics),
                "estimated_revenue": template.price * template.usage_count,
                "performance_score": min(100, template.usage_count * 10)
            }
            
        except Exception as e:
            logging.error(f"Template performance analysis failed: {str(e)}")
            return {"error": str(e)}

# Global service template system
service_templates = ServiceTemplateSystem()
