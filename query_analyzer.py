"""
Query Analysis Engine - OperatorOS
Analyzes user queries to determine expertise requirements and optimal agent chains
"""

import re
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from ai_providers import ai_manager

@dataclass
class QueryAnalysis:
    """Analysis result for a user query"""
    primary_domain: str
    required_perspectives: List[str]
    complexity_level: str
    agent_chain: List[str]
    synthesis_needed: bool
    confidence_score: float
    estimated_tokens: int

class QueryAnalyzer:
    """Analyzes user queries to determine optimal agent chains"""
    
    def __init__(self):
        self.domain_keywords = {
            'business': ['business', 'startup', 'company', 'revenue', 'profit', 'market', 'competition', 'strategy'],
            'financial': ['money', 'financial', 'budget', 'investment', 'savings', 'debt', 'cash', 'income'],
            'legal': ['legal', 'law', 'contract', 'divorce', 'rights', 'lawsuit', 'attorney', 'court'],
            'health': ['health', 'medical', 'doctor', 'therapy', 'mental', 'wellness', 'fitness'],
            'career': ['job', 'career', 'work', 'employment', 'resume', 'interview', 'promotion'],
            'education': ['learn', 'study', 'course', 'degree', 'school', 'university', 'training'],
            'technology': ['tech', 'software', 'code', 'programming', 'app', 'system', 'digital'],
            'personal': ['personal', 'life', 'relationship', 'family', 'home', 'lifestyle'],
            'gaming': ['gaming', 'game', 'deck', 'card', 'yugioh', 'yu-gi-oh', 'strategy', 'competitive', 'tournament', 'meta', 'burn']
        }
        
        self.agent_specializations = {
            'CFO': ['financial', 'business', 'investment', 'budget'],
            'CSA': ['strategy', 'business', 'market', 'competition'],
            'COO': ['operations', 'business', 'process', 'management'],
            'CRO': ['risk', 'business', 'financial', 'legal'],
            'Legal_Expert': ['legal', 'law', 'contract', 'rights'],
            'Financial_Advisor': ['financial', 'investment', 'budget', 'money'],
            'Therapist': ['mental', 'personal', 'relationship', 'health'],
            'Career_Coach': ['career', 'job', 'work', 'employment'],
            'Business_Coach': ['business', 'startup', 'strategy', 'growth'],
            'Life_Coach': ['personal', 'life', 'goals', 'lifestyle'],
            'Tech_Expert': ['technology', 'software', 'digital', 'system'],
            'Child_Psychologist': ['family', 'children', 'parenting', 'education']
        }
        
        self.complexity_indicators = {
            'high': ['complex', 'comprehensive', 'detailed', 'thorough', 'complete', 'multiple', 'all aspects'],
            'medium': ['analyze', 'evaluate', 'assess', 'consider', 'review', 'examine'],
            'low': ['simple', 'quick', 'basic', 'brief', 'what is', 'how to']
        }
    
    def analyze_user_query(self, user_input: str) -> QueryAnalysis:
        """
        Analyze user query to identify what types of expertise are needed
        """
        try:
            # Clean and normalize input
            query_lower = user_input.lower()
            
            # Determine primary domain
            primary_domain = self._identify_primary_domain(query_lower)
            
            # Assess complexity level
            complexity_level = self._assess_complexity(query_lower)
            
            # Identify required perspectives
            required_perspectives = self._identify_required_perspectives(query_lower, primary_domain)
            
            # Build agent chain
            agent_chain = self._build_agent_chain(required_perspectives, complexity_level)
            
            # Determine if synthesis is needed
            synthesis_needed = len(agent_chain) > 1
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(query_lower, agent_chain)
            
            # Estimate token usage
            estimated_tokens = self._estimate_token_usage(complexity_level, len(agent_chain))
            
            return QueryAnalysis(
                primary_domain=primary_domain,
                required_perspectives=required_perspectives,
                complexity_level=complexity_level,
                agent_chain=agent_chain,
                synthesis_needed=synthesis_needed,
                confidence_score=confidence_score,
                estimated_tokens=estimated_tokens
            )
            
        except Exception as e:
            logging.error(f"Query analysis failed: {str(e)}")
            # Return default analysis for fallback
            return QueryAnalysis(
                primary_domain="general",
                required_perspectives=["general"],
                complexity_level="medium",
                agent_chain=["Life_Coach"],
                synthesis_needed=False,
                confidence_score=0.5,
                estimated_tokens=1000
            )
    
    def _identify_primary_domain(self, query: str) -> str:
        """Identify the primary domain of the query"""
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                domain_scores[domain] = score
        
        if not domain_scores:
            return "general"
        
        return max(domain_scores, key=domain_scores.get)
    
    def _assess_complexity(self, query: str) -> str:
        """Assess the complexity level of the query"""
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in query for indicator in indicators):
                return level
        
        # Default complexity based on query length
        word_count = len(query.split())
        if word_count > 30:
            return "high"
        elif word_count > 10:
            return "medium"
        else:
            return "low"
    
    def _identify_required_perspectives(self, query: str, primary_domain: str) -> List[str]:
        """Identify what perspectives are needed for comprehensive analysis"""
        perspectives = set()
        
        # Add primary domain perspective
        perspectives.add(primary_domain)
        
        # Check for specific perspective keywords
        perspective_keywords = {
            'financial': ['money', 'cost', 'budget', 'financial', 'investment', 'profit', 'revenue'],
            'legal': ['legal', 'rights', 'law', 'contract', 'lawsuit', 'attorney'],
            'strategic': ['strategy', 'plan', 'approach', 'direction', 'vision'],
            'operational': ['operations', 'process', 'implementation', 'execution', 'workflow'],
            'risk': ['risk', 'danger', 'threat', 'safety', 'security', 'protection'],
            'personal': ['personal', 'emotional', 'mental', 'psychological', 'feelings'],
            'technical': ['technical', 'technology', 'system', 'software', 'digital']
        }
        
        for perspective, keywords in perspective_keywords.items():
            if any(keyword in query for keyword in keywords):
                perspectives.add(perspective)
        
        return list(perspectives)
    
    def _build_agent_chain(self, perspectives: List[str], complexity: str) -> List[str]:
        """Build optimal agent chain based on required perspectives"""
        agent_chain = []
        
        # Map perspectives to agents
        perspective_to_agent = {
            'financial': 'CFO',
            'business': 'CSA',
            'strategic': 'CSA',
            'operational': 'COO',
            'risk': 'CRO',
            'legal': 'Legal_Expert',
            'personal': 'Life_Coach',
            'career': 'Career_Coach',
            'technical': 'Tech_Expert',
            'health': 'Therapist',
            'gaming': 'Gaming_Expert'
        }
        
        # Add agents based on perspectives
        for perspective in perspectives:
            if perspective in perspective_to_agent:
                agent = perspective_to_agent[perspective]
                if agent not in agent_chain:
                    agent_chain.append(agent)
        
        # Ensure minimum one agent
        if not agent_chain:
            agent_chain = ['Life_Coach']
        
        # Add synthesizer for complex queries with multiple agents
        if complexity == 'high' and len(agent_chain) > 1:
            agent_chain.append('SYNTHESIZER')
        
        # Limit chain length for performance
        if len(agent_chain) > 5:
            agent_chain = agent_chain[:5]
        
        return agent_chain
    
    def _calculate_confidence_score(self, query: str, agent_chain: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        base_score = 0.7
        
        # Higher confidence for specific domains
        domain_matches = sum(1 for keywords in self.domain_keywords.values() 
                           for keyword in keywords if keyword in query)
        domain_bonus = min(domain_matches * 0.05, 0.2)
        
        # Higher confidence for appropriate chain length
        chain_length_bonus = 0.1 if 1 <= len(agent_chain) <= 3 else 0.0
        
        # Lower confidence for very long or very short queries
        word_count = len(query.split())
        length_penalty = 0.0
        if word_count < 3 or word_count > 100:
            length_penalty = 0.1
        
        final_score = base_score + domain_bonus + chain_length_bonus - length_penalty
        return min(max(final_score, 0.0), 1.0)
    
    def _estimate_token_usage(self, complexity: str, chain_length: int) -> int:
        """Estimate total token usage for the agent chain"""
        base_tokens = {
            'low': 500,
            'medium': 1000,
            'high': 2000
        }
        
        tokens_per_agent = base_tokens.get(complexity, 1000)
        total_tokens = tokens_per_agent * chain_length
        
        # Add synthesis tokens if needed
        if chain_length > 1:
            total_tokens += 500
        
        return total_tokens
    
    def get_agent_capabilities(self, agent_type: str) -> Dict[str, Any]:
        """Get capabilities and specializations for an agent type"""
        capabilities = {
            'CFO': {
                'specializations': ['financial analysis', 'budgeting', 'investment planning', 'cost optimization'],
                'optimal_provider': 'grok',
                'strength': 'Financial expertise and quantitative analysis'
            },
            'CSA': {
                'specializations': ['strategic planning', 'market analysis', 'competitive intelligence', 'business development'],
                'optimal_provider': 'openai',
                'strength': 'Strategic thinking and analytical reasoning'
            },
            'COO': {
                'specializations': ['operations management', 'process optimization', 'project management', 'execution planning'],
                'optimal_provider': 'openai',
                'strength': 'Operational excellence and systematic thinking'
            },
            'CRO': {
                'specializations': ['risk assessment', 'compliance', 'security analysis', 'threat mitigation'],
                'optimal_provider': 'grok',
                'strength': 'Risk analysis and protective strategies'
            },
            'Legal_Expert': {
                'specializations': ['legal analysis', 'contract review', 'rights assessment', 'compliance guidance'],
                'optimal_provider': 'openai',
                'strength': 'Legal knowledge and analytical precision'
            },
            'Life_Coach': {
                'specializations': ['personal development', 'goal setting', 'motivation', 'life planning'],
                'optimal_provider': 'openai',
                'strength': 'Personal guidance and motivational support'
            },
            'Career_Coach': {
                'specializations': ['career development', 'job search', 'professional growth', 'networking'],
                'optimal_provider': 'openai',
                'strength': 'Career guidance and professional development'
            },
            'Tech_Expert': {
                'specializations': ['technology analysis', 'system design', 'digital transformation', 'innovation'],
                'optimal_provider': 'openai',
                'strength': 'Technical expertise and systematic analysis'
            },
            'Gaming_Expert': {
                'specializations': ['gaming strategy', 'competitive analysis', 'deck building', 'meta analysis'],
                'optimal_provider': 'openai',
                'strength': 'Gaming expertise and strategic analysis'
            }
        }
        
        return capabilities.get(agent_type, {
            'specializations': ['general guidance'],
            'optimal_provider': 'anthropic',
            'strength': 'General problem-solving and analysis'
        })

# Initialize global analyzer
query_analyzer = QueryAnalyzer()