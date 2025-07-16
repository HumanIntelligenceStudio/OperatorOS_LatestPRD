"""
Token Limiter - OperatorOS
Implements character/token limiting for AI providers to prevent timeouts
"""

import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenLimits:
    """Token limits for different AI providers"""
    max_tokens: int
    safe_limit: int  # 99% of max_tokens
    chars_per_token: float  # Approximate characters per token

class TokenLimiter:
    """Manages token limits for different AI providers"""
    
    def __init__(self):
        self.provider_limits = {
            'openai': TokenLimits(
                max_tokens=128000,  # GPT-4o context limit
                safe_limit=126720,  # 99% of max
                chars_per_token=4.0  # OpenAI average
            ),
            'anthropic': TokenLimits(
                max_tokens=200000,  # Claude-sonnet-4 context limit
                safe_limit=198000,  # 99% of max
                chars_per_token=3.5  # Anthropic average
            ),
            'grok': TokenLimits(
                max_tokens=128000,  # Grok context limit
                safe_limit=126720,  # 99% of max
                chars_per_token=4.0  # Similar to OpenAI
            )
        }
    
    def estimate_tokens(self, text: str, provider: str) -> int:
        """Estimate token count for given text and provider"""
        if not text:
            return 0
        
        provider_limit = self.provider_limits.get(provider.lower())
        if not provider_limit:
            # Default fallback
            return len(text) // 4
        
        return int(len(text) / provider_limit.chars_per_token)
    
    def get_safe_limit(self, provider: str) -> int:
        """Get safe token limit for provider"""
        provider_limit = self.provider_limits.get(provider.lower())
        return provider_limit.safe_limit if provider_limit else 30000
    
    def is_within_limits(self, text: str, provider: str) -> bool:
        """Check if text is within safe limits for provider"""
        estimated_tokens = self.estimate_tokens(text, provider)
        safe_limit = self.get_safe_limit(provider)
        return estimated_tokens <= safe_limit
    
    def truncate_prompt(self, system_prompt: str, user_context: str, 
                       query: str, provider: str) -> Tuple[str, str, str, bool]:
        """
        Intelligently truncate prompt components to fit within limits
        Priority: system_prompt > query > user_context
        Returns: (truncated_system, truncated_context, truncated_query, was_truncated)
        """
        safe_limit = self.get_safe_limit(provider)
        
        # Calculate token estimates
        system_tokens = self.estimate_tokens(system_prompt, provider)
        query_tokens = self.estimate_tokens(query, provider)
        context_tokens = self.estimate_tokens(user_context, provider)
        
        total_tokens = system_tokens + query_tokens + context_tokens
        
        # If within limits, return as-is
        if total_tokens <= safe_limit:
            return system_prompt, user_context, query, False
        
        logger.warning(f"Prompt exceeds safe limit ({total_tokens} > {safe_limit}). Truncating...")
        
        # Reserve tokens for system prompt and query (highest priority)
        reserved_tokens = system_tokens + query_tokens
        available_for_context = safe_limit - reserved_tokens
        
        # If system + query already exceed limit, truncate query
        if reserved_tokens > safe_limit:
            logger.warning("System prompt + query exceed limits. Truncating query...")
            available_for_query = safe_limit - system_tokens
            if available_for_query > 0:
                truncated_query = self._truncate_text(query, available_for_query, provider)
            else:
                truncated_query = query[:100]  # Minimum query
            return system_prompt, "", truncated_query, True
        
        # Truncate context to fit available space
        if available_for_context > 0:
            truncated_context = self._truncate_text(user_context, available_for_context, provider)
        else:
            truncated_context = ""
        
        logger.info(f"Truncated context from {context_tokens} to {self.estimate_tokens(truncated_context, provider)} tokens")
        
        return system_prompt, truncated_context, query, True
    
    def _truncate_text(self, text: str, max_tokens: int, provider: str) -> str:
        """Truncate text to fit within token limit"""
        if not text:
            return ""
        
        provider_limit = self.provider_limits.get(provider.lower())
        if not provider_limit:
            return text[:max_tokens * 4]  # Fallback
        
        # Calculate approximate character limit
        max_chars = int(max_tokens * provider_limit.chars_per_token)
        
        if len(text) <= max_chars:
            return text
        
        # Truncate with sliding window (keep most recent content)
        truncated = text[-max_chars:]
        
        # Try to break at word boundary for better readability
        if ' ' in truncated:
            words = truncated.split(' ')
            if len(words) > 1:
                # Remove first partial word
                truncated = ' '.join(words[1:])
        
        return truncated
    
    def truncate_context_sliding_window(self, context: str, provider: str, 
                                      max_context_tokens: int = None) -> str:
        """
        Truncate context using sliding window approach
        Keeps most recent content when context gets too large
        """
        if not context:
            return ""
        
        if max_context_tokens is None:
            # Use 50% of safe limit for context by default
            max_context_tokens = self.get_safe_limit(provider) // 2
        
        current_tokens = self.estimate_tokens(context, provider)
        
        if current_tokens <= max_context_tokens:
            return context
        
        logger.info(f"Context sliding window: {current_tokens} -> {max_context_tokens} tokens")
        
        return self._truncate_text(context, max_context_tokens, provider)
    
    def get_provider_info(self, provider: str) -> Dict:
        """Get provider limit information"""
        provider_limit = self.provider_limits.get(provider.lower())
        if not provider_limit:
            return {"error": "Unknown provider"}
        
        return {
            "max_tokens": provider_limit.max_tokens,
            "safe_limit": provider_limit.safe_limit,
            "chars_per_token": provider_limit.chars_per_token
        }
    
    def validate_prompt_size(self, prompt: str, provider: str) -> Dict:
        """Validate prompt size and return diagnostics"""
        tokens = self.estimate_tokens(prompt, provider)
        safe_limit = self.get_safe_limit(provider)
        
        return {
            "estimated_tokens": tokens,
            "safe_limit": safe_limit,
            "within_limits": tokens <= safe_limit,
            "utilization_percent": (tokens / safe_limit) * 100,
            "provider": provider
        }

# Global instance
token_limiter = TokenLimiter()