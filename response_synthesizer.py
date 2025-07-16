"""
Response Synthesizer - OperatorOS
Advanced synthesis engine that combines multiple agent perspectives into comprehensive responses
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from ai_providers import ai_manager
from agent_chain_orchestrator import AgentResponse

@dataclass
class SynthesisInsight:
    """Individual insight extracted from agent responses"""
    content: str
    source_agents: List[str]
    insight_type: str  # 'overlap', 'conflict', 'unique', 'action'
    confidence: float
    priority: int

@dataclass
class SynthesisResult:
    """Complete synthesis result with structured analysis"""
    comprehensive_answer: str
    key_insights: List[SynthesisInsight]
    action_items: List[str]
    conflicting_viewpoints: List[Dict[str, Any]]
    consensus_points: List[str]
    confidence_score: float
    synthesis_quality: str
    word_count: int
    processing_time: float

class ResponseSynthesizer:
    """Advanced response synthesizer that creates comprehensive, actionable responses"""
    
    def __init__(self):
        self.synthesis_templates = {
            'business_comprehensive': """# 🎯 Comprehensive Business Analysis

## Executive Summary
{executive_summary}

## 💰 Financial Perspective
{financial_analysis}

## 📊 Strategic Analysis
{strategic_analysis}

## ⚙️ Operational Considerations
{operational_analysis}

## ⚠️ Risk Assessment
{risk_analysis}

## 🎬 Action Plan
{action_plan}

## 📋 Next Steps
{next_steps}""",
            
            'personal_comprehensive': """# 🌟 Comprehensive Personal Guidance

## Overview
{overview}

## 🧠 Personal Development Perspective
{personal_analysis}

## 💼 Career Implications
{career_analysis}

## 💰 Financial Considerations
{financial_analysis}

## 🔮 Strategic Recommendations
{strategic_analysis}

## 🎯 Action Plan
{action_plan}

## 🚀 Next Steps
{next_steps}""",
            
            'legal_comprehensive': """# ⚖️ Comprehensive Legal Analysis

## Legal Overview
{legal_overview}

## 🏛️ Legal Perspective
{legal_analysis}

## 💰 Financial Implications
{financial_analysis}

## 🎯 Strategic Considerations
{strategic_analysis}

## ⚠️ Risk Mitigation
{risk_analysis}

## 📋 Action Items
{action_items}

## 🔄 Next Steps
{next_steps}""",
            
            'general_comprehensive': """# 🎯 Comprehensive Analysis

## Summary
{summary}

## Key Perspectives
{perspectives}

## Important Considerations
{considerations}

## Recommended Actions
{actions}

## Next Steps
{next_steps}"""
        }
    
    def synthesize_agent_responses(self, agent_responses: List[AgentResponse], 
                                 user_query: str = "") -> SynthesisResult:
        """
        Combine multiple agent perspectives into one comprehensive answer
        
        Features:
        - Identify overlapping insights
        - Highlight conflicting viewpoints
        - Create action-oriented synthesis
        - Maintain each agent's unique perspective
        """
        start_time = datetime.now()
        
        try:
            # Analyze responses for insights
            insights = self._extract_insights(agent_responses)
            
            # Identify overlaps and conflicts
            overlaps = self._identify_overlapping_insights(insights)
            conflicts = self._identify_conflicting_viewpoints(agent_responses)
            
            # Generate structured synthesis
            synthesis = self._generate_structured_synthesis(
                agent_responses, user_query, insights, overlaps, conflicts
            )
            
            # Extract action items
            action_items = self._extract_action_items(agent_responses)
            
            # Calculate quality metrics
            confidence_score = self._calculate_synthesis_confidence(agent_responses, insights)
            quality_rating = self._assess_synthesis_quality(synthesis, agent_responses)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return SynthesisResult(
                comprehensive_answer=synthesis,
                key_insights=insights,
                action_items=action_items,
                conflicting_viewpoints=conflicts,
                consensus_points=overlaps,
                confidence_score=confidence_score,
                synthesis_quality=quality_rating,
                word_count=len(synthesis.split()),
                processing_time=processing_time
            )
            
        except Exception as e:
            logging.error(f"Response synthesis failed: {str(e)}")
            return self._create_fallback_synthesis(agent_responses, user_query)
    
    def _extract_insights(self, responses: List[AgentResponse]) -> List[SynthesisInsight]:
        """Extract key insights from agent responses"""
        insights = []
        
        for response in responses:
            # Extract key points using AI analysis
            insight_prompt = f"""Analyze this expert response and extract the top 3 most important insights:

            Expert: {response.agent_type}
            Content: {response.content}
            
            For each insight, provide:
            1. The insight in 1-2 sentences
            2. Why it's important
            3. Priority level (1-5)
            
            Format as numbered list."""
            
            try:
                ai_response = ai_manager.generate_response(
                    prompt=insight_prompt,
                    provider="anthropic",
                    task_type="analysis",
                    max_tokens=500
                )
                
                if ai_response.get('success'):
                    extracted_insights = self._parse_insights(
                        ai_response['content'], response.agent_type
                    )
                    insights.extend(extracted_insights)
                    
            except Exception as e:
                logging.warning(f"Insight extraction failed for {response.agent_type}: {str(e)}")
        
        return insights
    
    def _parse_insights(self, ai_content: str, agent_type: str) -> List[SynthesisInsight]:
        """Parse AI-extracted insights into structured format"""
        insights = []
        
        # Simple regex parsing for numbered insights
        insight_pattern = r'(\d+)\.\s*([^.]+\.)\s*([^.]+\.)?'
        matches = re.findall(insight_pattern, ai_content)
        
        for i, match in enumerate(matches[:3]):  # Limit to top 3
            insight_content = match[1]
            if match[2]:
                insight_content += " " + match[2]
            
            insights.append(SynthesisInsight(
                content=insight_content.strip(),
                source_agents=[agent_type],
                insight_type='unique',
                confidence=0.8,
                priority=i + 1
            ))
        
        return insights
    
    def _identify_overlapping_insights(self, insights: List[SynthesisInsight]) -> List[str]:
        """Identify overlapping insights across different agents"""
        overlaps = []
        
        # Simple keyword-based overlap detection
        for i, insight1 in enumerate(insights):
            for j, insight2 in enumerate(insights[i+1:], i+1):
                if insight1.source_agents[0] != insight2.source_agents[0]:
                    # Check for similar keywords
                    words1 = set(insight1.content.lower().split())
                    words2 = set(insight2.content.lower().split())
                    
                    overlap_ratio = len(words1.intersection(words2)) / len(words1.union(words2))
                    
                    if overlap_ratio > 0.3:  # 30% word overlap threshold
                        overlap_text = f"Both {insight1.source_agents[0]} and {insight2.source_agents[0]} emphasize: {insight1.content}"
                        if overlap_text not in overlaps:
                            overlaps.append(overlap_text)
        
        return overlaps
    
    def _identify_conflicting_viewpoints(self, responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """Identify conflicting viewpoints between agents"""
        conflicts = []
        
        # Use AI to identify conflicts
        if len(responses) > 1:
            conflict_prompt = f"""Analyze these expert responses and identify any conflicting viewpoints or disagreements:

            {chr(10).join([f"{r.agent_type}: {r.content[:500]}..." for r in responses])}
            
            If there are conflicts, describe them clearly. If no conflicts, respond with "No significant conflicts identified."
            
            Format conflicts as:
            CONFLICT: [Brief description]
            AGENT A: [Position]
            AGENT B: [Position]
            RESOLUTION: [Balanced perspective]"""
            
            try:
                ai_response = ai_manager.generate_response(
                    prompt=conflict_prompt,
                    provider="anthropic",
                    task_type="analysis",
                    max_tokens=800
                )
                
                if ai_response.get('success') and "No significant conflicts" not in ai_response['content']:
                    conflicts = self._parse_conflicts(ai_response['content'])
                    
            except Exception as e:
                logging.warning(f"Conflict identification failed: {str(e)}")
        
        return conflicts
    
    def _parse_conflicts(self, ai_content: str) -> List[Dict[str, Any]]:
        """Parse AI-identified conflicts into structured format"""
        conflicts = []
        
        # Simple parsing for conflict structure
        conflict_blocks = ai_content.split('CONFLICT:')
        
        for block in conflict_blocks[1:]:  # Skip first empty block
            lines = block.strip().split('\n')
            if len(lines) >= 4:
                conflict_desc = lines[0].strip()
                agent_a = lines[1].replace('AGENT A:', '').strip()
                agent_b = lines[2].replace('AGENT B:', '').strip()
                resolution = lines[3].replace('RESOLUTION:', '').strip()
                
                conflicts.append({
                    'description': conflict_desc,
                    'position_a': agent_a,
                    'position_b': agent_b,
                    'resolution': resolution
                })
        
        return conflicts
    
    def _generate_structured_synthesis(self, responses: List[AgentResponse], 
                                     user_query: str, insights: List[SynthesisInsight],
                                     overlaps: List[str], conflicts: List[Dict[str, Any]]) -> str:
        """Generate a structured, comprehensive synthesis"""
        
        # Determine synthesis template based on agent types
        agent_types = [r.agent_type for r in responses]
        template_key = self._select_synthesis_template(agent_types)
        
        # Prepare synthesis components
        synthesis_components = self._prepare_synthesis_components(
            responses, user_query, insights, overlaps, conflicts
        )
        
        # Generate final synthesis using AI
        synthesis_prompt = f"""Create a comprehensive synthesis combining these expert perspectives:

        Original Query: {user_query}
        
        Expert Responses:
        {chr(10).join([f"{r.agent_type}: {r.content}" for r in responses])}
        
        Key Insights:
        {chr(10).join([f"- {insight.content}" for insight in insights])}
        
        Overlapping Points:
        {chr(10).join([f"- {overlap}" for overlap in overlaps])}
        
        Conflicting Viewpoints:
        {chr(10).join([f"- {conflict['description']}: {conflict['resolution']}" for conflict in conflicts])}
        
        Create a well-structured, comprehensive response that:
        1. Addresses the user's query directly
        2. Integrates all expert perspectives
        3. Provides clear, actionable recommendations
        4. Maintains professional tone
        5. Uses clear headings and organization
        
        Make it comprehensive but concise, focusing on actionable value."""
        
        try:
            ai_response = ai_manager.generate_response(
                prompt=synthesis_prompt,
                provider="anthropic",
                task_type="analysis",
                max_tokens=2500
            )
            
            if ai_response.get('success'):
                return ai_response['content']
            else:
                return self._create_manual_synthesis(responses, user_query)
                
        except Exception as e:
            logging.error(f"AI synthesis generation failed: {str(e)}")
            return self._create_manual_synthesis(responses, user_query)
    
    def _select_synthesis_template(self, agent_types: List[str]) -> str:
        """Select appropriate synthesis template based on agent types"""
        if any(agent in ['CFO', 'CSA', 'COO', 'CRO'] for agent in agent_types):
            return 'business_comprehensive'
        elif any(agent in ['Legal_Expert'] for agent in agent_types):
            return 'legal_comprehensive'
        elif any(agent in ['Life_Coach', 'Career_Coach'] for agent in agent_types):
            return 'personal_comprehensive'
        else:
            return 'general_comprehensive'
    
    def _prepare_synthesis_components(self, responses: List[AgentResponse], 
                                    user_query: str, insights: List[SynthesisInsight],
                                    overlaps: List[str], conflicts: List[Dict[str, Any]]) -> Dict[str, str]:
        """Prepare components for synthesis template"""
        components = {}
        
        # Group responses by type
        for response in responses:
            if response.agent_type == 'CFO':
                components['financial_analysis'] = response.content
            elif response.agent_type == 'CSA':
                components['strategic_analysis'] = response.content
            elif response.agent_type == 'COO':
                components['operational_analysis'] = response.content
            elif response.agent_type == 'CRO':
                components['risk_analysis'] = response.content
            elif response.agent_type == 'Legal_Expert':
                components['legal_analysis'] = response.content
            elif response.agent_type == 'Life_Coach':
                components['personal_analysis'] = response.content
            elif response.agent_type == 'Career_Coach':
                components['career_analysis'] = response.content
        
        # Add summary components
        components['summary'] = f"Analysis of: {user_query}"
        components['perspectives'] = "\n".join([f"- **{r.agent_type}**: {r.perspective}" for r in responses])
        
        return components
    
    def _create_manual_synthesis(self, responses: List[AgentResponse], user_query: str) -> str:
        """Create manual synthesis when AI synthesis fails"""
        synthesis = f"# Comprehensive Analysis: {user_query}\n\n"
        
        # Executive summary
        synthesis += "## Executive Summary\n"
        synthesis += f"Based on analysis from {len(responses)} expert perspectives, here's a comprehensive response to your query.\n\n"
        
        # Individual perspectives
        synthesis += "## Expert Perspectives\n\n"
        for response in responses:
            synthesis += f"### {response.agent_type} Analysis\n"
            synthesis += f"**Provider**: {response.provider}\n"
            synthesis += f"**Focus**: {response.perspective}\n\n"
            synthesis += f"{response.content}\n\n"
        
        # Action items
        synthesis += "## Recommended Actions\n"
        synthesis += "Based on all expert perspectives, consider these key actions:\n"
        
        action_items = self._extract_action_items(responses)
        for i, action in enumerate(action_items[:5], 1):
            synthesis += f"{i}. {action}\n"
        
        return synthesis
    
    def _extract_action_items(self, responses: List[AgentResponse]) -> List[str]:
        """Extract actionable items from agent responses"""
        action_items = []
        
        for response in responses:
            # Simple extraction of action-oriented sentences
            sentences = response.content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(keyword in sentence.lower() for keyword in 
                      ['should', 'recommend', 'suggest', 'consider', 'need to', 'must', 'action']):
                    if len(sentence) > 20 and len(sentence) < 200:
                        action_items.append(sentence + '.')
        
        return list(set(action_items))  # Remove duplicates
    
    def _calculate_synthesis_confidence(self, responses: List[AgentResponse], 
                                      insights: List[SynthesisInsight]) -> float:
        """Calculate confidence score for the synthesis"""
        if not responses:
            return 0.0
        
        # Base confidence from individual responses
        avg_response_confidence = sum(r.confidence_score for r in responses) / len(responses)
        
        # Bonus for multiple perspectives
        perspective_bonus = min(len(responses) * 0.1, 0.3)
        
        # Bonus for quality insights
        insight_bonus = min(len(insights) * 0.02, 0.1)
        
        # Penalty for very short responses
        total_content_length = sum(len(r.content) for r in responses)
        if total_content_length < 500:
            length_penalty = 0.2
        else:
            length_penalty = 0.0
        
        final_confidence = avg_response_confidence + perspective_bonus + insight_bonus - length_penalty
        return min(max(final_confidence, 0.0), 1.0)
    
    def _assess_synthesis_quality(self, synthesis: str, responses: List[AgentResponse]) -> str:
        """Assess the quality of the synthesis"""
        word_count = len(synthesis.split())
        
        if word_count < 200:
            return "Basic"
        elif word_count < 500:
            return "Good"
        elif word_count < 1000:
            return "Excellent"
        else:
            return "Comprehensive"
    
    def _create_fallback_synthesis(self, responses: List[AgentResponse], user_query: str) -> SynthesisResult:
        """Create fallback synthesis when main process fails"""
        fallback_content = f"# Analysis: {user_query}\n\n"
        
        if responses:
            fallback_content += "## Expert Perspectives\n\n"
            for response in responses:
                fallback_content += f"**{response.agent_type}**: {response.content[:300]}...\n\n"
        else:
            fallback_content += "No expert responses available."
        
        return SynthesisResult(
            comprehensive_answer=fallback_content,
            key_insights=[],
            action_items=[],
            conflicting_viewpoints=[],
            consensus_points=[],
            confidence_score=0.3,
            synthesis_quality="Basic",
            word_count=len(fallback_content.split()),
            processing_time=0.0
        )
    
    def get_synthesis_statistics(self) -> Dict[str, Any]:
        """Get statistics about synthesis performance"""
        return {
            'available_templates': list(self.synthesis_templates.keys()),
            'supported_agents': ['CFO', 'CSA', 'COO', 'CRO', 'Legal_Expert', 'Life_Coach', 'Career_Coach'],
            'synthesis_capabilities': [
                'Conflict resolution',
                'Insight extraction',
                'Action item generation',
                'Perspective integration',
                'Quality assessment'
            ]
        }

# Initialize global synthesizer
response_synthesizer = ResponseSynthesizer()