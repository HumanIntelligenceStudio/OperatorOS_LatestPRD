"""
Agent Chain Orchestrator - OperatorOS
Coordinates multiple agents to provide comprehensive responses
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from ai_providers import ai_manager
from query_analyzer import query_analyzer

@dataclass
class AgentResponse:
    """Response from an individual agent"""
    agent_type: str
    content: str
    provider: str
    model: str
    tokens_used: int
    cost: float
    confidence_score: float
    perspective: str
    timestamp: datetime
    context_used: str = ""

@dataclass
class ChainResult:
    """Result from processing an agent chain"""
    responses: List[AgentResponse]
    synthesis: str
    total_tokens: int
    total_cost: float
    processing_time: float
    confidence_score: float
    perspectives_covered: List[str]

class AgentChainOrchestrator:
    """Orchestrates multiple agents for comprehensive responses"""
    
    def __init__(self):
        self.agent_prompts = {
            'CFO': """You are a CFO (Chief Financial Officer) AI agent with expertise in financial analysis, budgeting, and strategic financial planning. 
            
            Your role is to provide comprehensive financial perspective on the user's query. Focus on:
            - Financial implications and costs
            - Budget analysis and recommendations
            - Investment considerations
            - Risk assessment from financial perspective
            - Revenue and profitability analysis
            - Cash flow considerations
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed financial analysis and recommendations. Use clear financial reasoning and include specific actionable insights.""",
            
            'CSA': """You are a CSA (Chief Strategy Advisor) AI agent with expertise in strategic planning, market analysis, and business development.
            
            Your role is to provide comprehensive strategic perspective on the user's query. Focus on:
            - Strategic implications and opportunities
            - Market analysis and competitive landscape
            - Long-term planning and vision
            - Growth strategies and scaling
            - Competitive advantages and positioning
            - Strategic risk assessment
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed strategic analysis and recommendations. Use clear strategic reasoning and include specific actionable insights.""",
            
            'COO': """You are a COO (Chief Operating Officer) AI agent with expertise in operations management, process optimization, and execution planning.
            
            Your role is to provide comprehensive operational perspective on the user's query. Focus on:
            - Implementation roadmaps and timelines
            - Process optimization and efficiency
            - Resource allocation and management
            - Operational risk mitigation
            - Performance metrics and KPIs
            - Execution strategies and tactics
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed operational analysis and implementation plan. Use clear operational reasoning and include specific actionable steps.""",
            
            'CRO': """You are a CRO (Chief Risk Officer) AI agent with expertise in risk assessment, compliance, and protective strategies.
            
            Your role is to provide comprehensive risk perspective on the user's query. Focus on:
            - Risk identification and assessment
            - Compliance requirements and regulations
            - Threat analysis and mitigation strategies
            - Safety and security considerations
            - Contingency planning
            - Risk monitoring and management
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed risk analysis and mitigation recommendations. Use clear risk reasoning and include specific protective measures.""",
            
            'Legal_Expert': """You are a Legal Expert AI agent with expertise in legal analysis, contract review, and rights assessment.
            
            Your role is to provide comprehensive legal perspective on the user's query. Focus on:
            - Legal implications and requirements
            - Rights and obligations analysis
            - Contract and agreement considerations
            - Regulatory compliance
            - Legal risk assessment
            - Protective legal strategies
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed legal analysis and recommendations. Use clear legal reasoning and include specific actionable guidance.""",
            
            'Life_Coach': """You are a Life Coach AI agent with expertise in personal development, goal setting, and motivational guidance.
            
            Your role is to provide comprehensive personal perspective on the user's query. Focus on:
            - Personal development and growth
            - Goal setting and achievement strategies
            - Motivation and mindset optimization
            - Life balance and well-being
            - Personal readiness assessment
            - Emotional and psychological considerations
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed personal development analysis and guidance. Use clear motivational reasoning and include specific actionable steps for personal growth.""",
            
            'Career_Coach': """You are a Career Coach AI agent with expertise in professional development, job search, and career advancement.
            
            Your role is to provide comprehensive career perspective on the user's query. Focus on:
            - Career development strategies
            - Professional growth opportunities
            - Job market analysis and positioning
            - Skill development recommendations
            - Networking and relationship building
            - Career transition planning
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed career analysis and development plan. Use clear career reasoning and include specific actionable career steps.""",
            
            'Tech_Expert': """You are a Technology Expert AI agent with expertise in technology analysis, system design, and digital transformation.
            
            Your role is to provide comprehensive technical perspective on the user's query. Focus on:
            - Technology solutions and recommendations
            - System design and architecture
            - Digital transformation strategies
            - Innovation opportunities
            - Technical risk assessment
            - Implementation and integration planning
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed technical analysis and recommendations. Use clear technical reasoning and include specific actionable technical steps.""",
            
            'Therapist': """You are a Therapist AI agent with expertise in mental health, emotional support, and psychological guidance.
            
            Your role is to provide comprehensive therapeutic perspective on the user's query. Focus on:
            - Emotional and psychological well-being
            - Mental health considerations
            - Coping strategies and resilience
            - Relationship dynamics and communication
            - Stress management and self-care
            - Personal healing and growth
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed therapeutic analysis and guidance. Use clear therapeutic reasoning and include specific actionable mental health strategies.""",
            
            'Financial_Advisor': """You are a Financial Advisor AI agent with expertise in personal finance, investment planning, and wealth management.
            
            Your role is to provide comprehensive financial advisory perspective on the user's query. Focus on:
            - Personal financial planning
            - Investment strategies and portfolio management
            - Retirement and savings planning
            - Insurance and protection strategies
            - Tax optimization and planning
            - Wealth building and preservation
            
            Context from previous agents: {context}
            
            User Query: {query}
            
            Provide a detailed financial advisory analysis and recommendations. Use clear financial planning reasoning and include specific actionable financial steps."""
        }
    
    def process_chain(self, query: str, agent_chain: List[str], 
                     user_context: str = "") -> ChainResult:
        """Process a complete agent chain and return comprehensive results"""
        start_time = datetime.now()
        responses = []
        accumulated_context = user_context
        total_tokens = 0
        total_cost = 0.0
        
        try:
            # Process each agent in the chain
            for i, agent_type in enumerate(agent_chain):
                if agent_type == 'SYNTHESIZER':
                    continue  # Skip synthesizer in main chain, handle separately
                
                # Generate response from current agent
                agent_response = self._generate_agent_response(
                    agent_type, query, accumulated_context
                )
                
                if agent_response:
                    responses.append(agent_response)
                    total_tokens += agent_response.tokens_used
                    total_cost += agent_response.cost
                    
                    # Update context for next agent
                    accumulated_context += f"\n\n{agent_response.agent_type} Perspective:\n{agent_response.content}"
                    
                    logging.info(f"Agent {agent_type} completed. Tokens: {agent_response.tokens_used}, Cost: ${agent_response.cost:.4f}")
                else:
                    logging.warning(f"Agent {agent_type} failed to generate response")
            
            # Generate synthesis if multiple agents
            synthesis = ""
            if len(responses) > 1:
                synthesis = self._generate_synthesis(query, responses)
            elif len(responses) == 1:
                synthesis = responses[0].content
            else:
                synthesis = "No valid responses generated from agent chain."
            
            # Calculate metrics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            confidence_score = self._calculate_chain_confidence(responses)
            perspectives_covered = [r.perspective for r in responses]
            
            return ChainResult(
                responses=responses,
                synthesis=synthesis,
                total_tokens=total_tokens,
                total_cost=total_cost,
                processing_time=processing_time,
                confidence_score=confidence_score,
                perspectives_covered=perspectives_covered
            )
            
        except Exception as e:
            logging.error(f"Agent chain processing failed: {str(e)}")
            return ChainResult(
                responses=[],
                synthesis=f"Error processing agent chain: {str(e)}",
                total_tokens=0,
                total_cost=0.0,
                processing_time=0.0,
                confidence_score=0.0,
                perspectives_covered=[]
            )
    
    def _generate_agent_response(self, agent_type: str, query: str, 
                               context: str) -> Optional[AgentResponse]:
        """Generate response from a specific agent"""
        try:
            # Get agent capabilities and optimal provider
            capabilities = query_analyzer.get_agent_capabilities(agent_type)
            optimal_provider = capabilities.get('optimal_provider', 'anthropic')
            
            # Construct agent prompt
            if agent_type in self.agent_prompts:
                prompt = self.agent_prompts[agent_type].format(
                    context=context, query=query
                )
            else:
                # Fallback prompt for unknown agents
                prompt = f"""You are a {agent_type} AI agent providing expert analysis.
                
                Context from previous agents: {context}
                
                User Query: {query}
                
                Provide your expert perspective and actionable recommendations."""
            
            # Generate AI response
            ai_response = ai_manager.generate_response(
                prompt=prompt,
                provider=optimal_provider,
                task_type="analysis",
                max_tokens=1500
            )
            
            if ai_response.get('success'):
                return AgentResponse(
                    agent_type=agent_type,
                    content=ai_response['content'],
                    provider=ai_response['provider'],
                    model=ai_response['model'],
                    tokens_used=ai_response.get('tokens_used', 0),
                    cost=ai_response.get('cost', 0.0),
                    confidence_score=self._calculate_response_confidence(ai_response),
                    perspective=capabilities.get('strength', 'General analysis'),
                    timestamp=datetime.now(),
                    context_used=context[:200] + "..." if len(context) > 200 else context
                )
            else:
                logging.error(f"AI response failed for {agent_type}: {ai_response.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logging.error(f"Agent response generation failed for {agent_type}: {str(e)}")
            return None
    
    def _generate_synthesis(self, query: str, responses: List[AgentResponse]) -> str:
        """Generate synthesis combining all agent perspectives"""
        try:
            # Prepare synthesis prompt
            perspectives_summary = ""
            for i, response in enumerate(responses, 1):
                perspectives_summary += f"""
                {i}. {response.agent_type} Perspective ({response.perspective}):
                {response.content}
                
                """
            
            synthesis_prompt = f"""You are a Master Synthesizer AI agent responsible for combining multiple expert perspectives into one comprehensive, actionable response.
            
            Original User Query: {query}
            
            Expert Perspectives Provided:
            {perspectives_summary}
            
            Your task is to:
            1. Synthesize all perspectives into a cohesive, comprehensive answer
            2. Identify key themes and overlapping insights
            3. Highlight any conflicting viewpoints and provide balanced resolution
            4. Create a clear, actionable plan that incorporates all relevant perspectives
            5. Prioritize recommendations based on importance and feasibility
            
            Provide a well-structured synthesis that gives the user a complete, actionable response to their query. Use clear headings and bullet points for organization."""
            
            # Generate synthesis using anthropic for analytical reasoning
            synthesis_response = ai_manager.generate_response(
                prompt=synthesis_prompt,
                provider="anthropic",
                task_type="analysis",
                max_tokens=2000
            )
            
            if synthesis_response.get('success'):
                return synthesis_response['content']
            else:
                # Fallback synthesis
                return self._create_fallback_synthesis(query, responses)
                
        except Exception as e:
            logging.error(f"Synthesis generation failed: {str(e)}")
            return self._create_fallback_synthesis(query, responses)
    
    def _create_fallback_synthesis(self, query: str, responses: List[AgentResponse]) -> str:
        """Create a basic synthesis when AI synthesis fails"""
        synthesis = f"# Comprehensive Analysis: {query}\n\n"
        
        for response in responses:
            synthesis += f"## {response.agent_type} Perspective\n"
            synthesis += f"{response.content}\n\n"
        
        synthesis += "## Summary\n"
        synthesis += f"Based on {len(responses)} expert perspectives, "
        synthesis += "this analysis provides multiple viewpoints to help you make an informed decision."
        
        return synthesis
    
    def _calculate_response_confidence(self, ai_response: Dict[str, Any]) -> float:
        """Calculate confidence score for an individual response"""
        base_score = 0.7
        
        # Higher confidence for successful responses
        if ai_response.get('success'):
            base_score += 0.2
        
        # Adjust based on response length (reasonable responses are better)
        content_length = len(ai_response.get('content', ''))
        if 200 <= content_length <= 2000:
            base_score += 0.1
        elif content_length < 100:
            base_score -= 0.2
        
        return min(max(base_score, 0.0), 1.0)
    
    def _calculate_chain_confidence(self, responses: List[AgentResponse]) -> float:
        """Calculate overall confidence score for the entire chain"""
        if not responses:
            return 0.0
        
        # Average individual confidence scores
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        
        # Bonus for multiple perspectives
        perspective_bonus = min(len(responses) * 0.05, 0.15)
        
        # Penalty for failed responses
        failure_penalty = 0.0
        if len(responses) < 2:  # Expected multiple perspectives
            failure_penalty = 0.1
        
        final_score = avg_confidence + perspective_bonus - failure_penalty
        return min(max(final_score, 0.0), 1.0)
    
    def get_agent_status(self, agent_type: str) -> Dict[str, Any]:
        """Get status and capabilities of a specific agent type"""
        capabilities = query_analyzer.get_agent_capabilities(agent_type)
        
        return {
            'agent_type': agent_type,
            'available': agent_type in self.agent_prompts,
            'capabilities': capabilities,
            'optimal_provider': capabilities.get('optimal_provider', 'anthropic'),
            'specializations': capabilities.get('specializations', [])
        }
    
    def validate_agent_chain(self, agent_chain: List[str]) -> Dict[str, Any]:
        """Validate an agent chain for feasibility and optimization"""
        validation_result = {
            'valid': True,
            'issues': [],
            'recommendations': [],
            'estimated_cost': 0.0,
            'estimated_time': 0.0
        }
        
        # Check for unknown agents
        for agent in agent_chain:
            if agent not in self.agent_prompts and agent != 'SYNTHESIZER':
                validation_result['valid'] = False
                validation_result['issues'].append(f"Unknown agent type: {agent}")
        
        # Check chain length
        if len(agent_chain) > 5:
            validation_result['recommendations'].append("Consider reducing chain length for better performance")
        
        # Estimate costs and time
        validation_result['estimated_cost'] = len(agent_chain) * 0.02  # Rough estimate
        validation_result['estimated_time'] = len(agent_chain) * 5.0   # Rough estimate in seconds
        
        return validation_result

# Initialize global orchestrator
agent_orchestrator = AgentChainOrchestrator()