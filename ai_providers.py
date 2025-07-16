import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# AI Provider imports
from openai import OpenAI
import anthropic
from anthropic import Anthropic
from token_limiter import token_limiter

# <important_code_snippet_instructions>
# The newest OpenAI model is "gpt-4o", not "gpt-4". 
# gpt-4o was released after your knowledge cutoff.
# Always prefer using gpt-4o as it is the latest model.
# The newest Anthropic model is "claude-sonnet-4-20250514", not "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022" nor "claude-3-sonnet-20240229". 
# If the user doesn't specify a model, always prefer using "claude-sonnet-4-20250514" as it is the latest model.
# </important_code_snippet_instructions>

class AIProviderManager:
    def __init__(self):
        self.providers = {}
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize all available AI providers"""
        # OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            self.providers['openai'] = OpenAI(api_key=openai_key)
            logging.info("OpenAI provider initialized")
        
        # Anthropic
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.providers['anthropic'] = Anthropic(api_key=anthropic_key)
            logging.info("Anthropic provider initialized")
        
        # Grok (xAI)
        xai_key = os.environ.get('XAI_API_KEY')
        if xai_key:
            self.providers['grok'] = OpenAI(base_url="https://api.x.ai/v1", api_key=xai_key)
            logging.info("Grok provider initialized")
    
    def get_best_provider(self, task_type: str = "general") -> str:
        """Intelligent routing based on task type"""
        task_routing = {
            "analysis": "anthropic",
            "creative": "openai", 
            "reasoning": "grok",
            "coding": "anthropic",
            "financial": "grok",
            "planning": "anthropic",
            "general": "anthropic"
        }
        
        preferred = task_routing.get(task_type, "anthropic")
        
        # Fallback logic
        if preferred in self.providers:
            return preferred
        elif "anthropic" in self.providers:
            return "anthropic"
        elif "openai" in self.providers:
            return "openai"
        elif "grok" in self.providers:
            return "grok"
        else:
            raise Exception("No AI providers available")
    
    def generate_response(self, prompt: str, provider: str = None, task_type: str = "general", 
                         model: str = None, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate AI response with intelligent routing and token limiting"""
        try:
            if not provider:
                provider = self.get_best_provider(task_type)
            
            if provider not in self.providers:
                raise Exception(f"Provider {provider} not available")
            
            # Check and truncate prompt if necessary
            if not token_limiter.is_within_limits(prompt, provider):
                logging.warning(f"Prompt exceeds limits for {provider}. Truncating...")
                # For single prompt, treat as user context
                _, truncated_prompt, _, was_truncated = token_limiter.truncate_prompt(
                    system_prompt="", user_context=prompt, query="", provider=provider
                )
                if was_truncated:
                    logging.info(f"Prompt truncated for {provider}")
                prompt = truncated_prompt
            
            start_time = datetime.now()
            
            if provider == "openai":
                response = self._generate_openai_response(prompt, model or "gpt-4o", max_tokens)
            elif provider == "anthropic":
                response = self._generate_anthropic_response(prompt, model or "claude-sonnet-4-20250514", max_tokens)
            elif provider == "grok":
                response = self._generate_grok_response(prompt, model or "grok-2-1212", max_tokens)
            else:
                raise Exception(f"Unknown provider: {provider}")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "provider": provider,
                "model": response["model"],
                "content": response["content"],
                "tokens_used": response.get("tokens_used", 0),
                "cost": response.get("cost", 0),
                "response_time": response_time,
                "success": True
            }
            
        except Exception as e:
            logging.error(f"AI generation failed: {str(e)}")
            return {
                "provider": provider,
                "error": str(e),
                "success": False
            }
    
    def _generate_openai_response(self, prompt: str, model: str, max_tokens: int) -> Dict[str, Any]:
        """Generate OpenAI response"""
        client = self.providers['openai']
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        
        return {
            "model": model,
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "cost": self._calculate_openai_cost(model, response.usage.total_tokens)
        }
    
    def _generate_anthropic_response(self, prompt: str, model: str, max_tokens: int) -> Dict[str, Any]:
        """Generate Anthropic response"""
        client = self.providers['anthropic']
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "model": model,
            "content": response.content[0].text,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "cost": self._calculate_anthropic_cost(model, response.usage.input_tokens, response.usage.output_tokens)
        }
    
    def _generate_grok_response(self, prompt: str, model: str, max_tokens: int) -> Dict[str, Any]:
        """Generate Grok response"""
        client = self.providers['grok']
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        
        return {
            "model": model,
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "cost": self._calculate_grok_cost(model, response.usage.total_tokens)
        }
    
    def _calculate_openai_cost(self, model: str, tokens: int) -> float:
        """Calculate OpenAI cost based on model and tokens (2025 pricing)"""
        # OpenAI 2025 pricing per 1k tokens
        rates = {
            "gpt-4o": 0.000015,  # $0.015 per 1k tokens
            "gpt-4": 0.00003,    # $0.03 per 1k tokens
            "gpt-3.5-turbo": 0.000002  # $0.002 per 1k tokens
        }
        return rates.get(model, 0.000015) * (tokens / 1000)
    
    def _calculate_anthropic_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate Anthropic cost based on model and tokens (2025 pricing)"""
        # Anthropic 2025 pricing per 1k tokens
        rates = {
            "claude-sonnet-4-20250514": {"input": 0.015, "output": 0.075},  # $0.015 input, $0.075 output
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}  # $0.003 input, $0.015 output
        }
        rate = rates.get(model, {"input": 0.015, "output": 0.075})
        return (rate["input"] * input_tokens + rate["output"] * output_tokens) / 1000
    
    def _calculate_grok_cost(self, model: str, tokens: int) -> float:
        """Calculate Grok cost based on model and tokens (2025 pricing)"""
        # xAI Grok 2025 pricing per 1k tokens
        rates = {
            "grok-2-1212": 0.010,  # $0.010 per 1k tokens
            "grok-2-vision-1212": 0.015,  # $0.015 per 1k tokens
            "grok-beta": 0.005  # $0.005 per 1k tokens
        }
        return rates.get(model, 0.010) * (tokens / 1000)
    
    def create_specialized_expert(self, field: str, expertise_level: str = "expert") -> str:
        """Create a specialized AI expert for any field"""
        expert_prompt = f"""
        You are now a world-class {expertise_level} in {field}. You have:
        - Deep theoretical knowledge and practical experience
        - Access to cutting-edge research and industry best practices
        - Ability to provide actionable insights and solutions
        - Experience working with professionals and organizations
        - Understanding of current trends and future developments

        Your role is to provide expert-level guidance, analysis, and recommendations in {field}.
        Always consider practical implications, cost-effectiveness, and real-world constraints.
        
        Respond with high-quality, professional advice that demonstrates your expertise.
        """
        return expert_prompt
    
    def get_goal_breakdown(self, goal: str, timeline: str = "3 months") -> Dict[str, Any]:
        """Break down any goal into actionable tasks"""
        prompt = f"""
        As an expert goal achievement strategist, break down this goal into a comprehensive action plan:
        
        Goal: {goal}
        Timeline: {timeline}
        
        Provide a detailed breakdown including:
        1. Key milestones with specific deadlines
        2. Actionable tasks for each milestone
        3. Required resources and skills
        4. Potential obstacles and mitigation strategies
        5. Success metrics and tracking methods
        6. Risk assessment and contingency plans
        
        Format as a structured plan with clear priorities and dependencies.
        """
        
        return self.generate_response(prompt, task_type="planning")

# Global AI manager instance
ai_manager = AIProviderManager()
