#!/usr/bin/env python3
"""
Test script to demonstrate multi-agent Yu-Gi-Oh! burn deck creation
"""

import sys
import os
sys.path.append('.')

from query_analyzer import query_analyzer
from agent_chain_orchestrator import agent_orchestrator
from response_synthesizer import response_synthesizer

def test_burn_deck_analysis():
    """Test comprehensive burn deck analysis using multi-agent system"""
    
    query = """Create a competitive burn deck for Yu-Gi-Oh! Standard format 2025. I need:
    1. Complete deck list with card ratios and explanations
    2. Combo explanations and win conditions
    3. Side deck strategy for current meta
    4. Matchup analysis against top tier decks
    5. Budget alternatives and tournament considerations
    
    Focus on modern burn strategies that can compete in the current meta."""
    
    print("🔍 Analyzing query to determine expert requirements...")
    
    # Step 1: Analyze the query
    analysis = query_analyzer.analyze_user_query(query)
    
    print(f"📊 Query Analysis Results:")
    print(f"   Primary Domain: {analysis.primary_domain}")
    print(f"   Required Perspectives: {analysis.required_perspectives}")
    print(f"   Complexity Level: {analysis.complexity_level}")
    print(f"   Agent Chain: {analysis.agent_chain}")
    print(f"   Confidence Score: {analysis.confidence_score:.2f}")
    print(f"   Estimated Tokens: {analysis.estimated_tokens}")
    
    # Step 2: Process the agent chain
    print(f"\n🤖 Processing agent chain with {len(analysis.agent_chain)} experts...")
    
    chain_result = agent_orchestrator.process_chain(
        query=query,
        agent_chain=analysis.agent_chain,
        user_context="User is looking for competitive Yu-Gi-Oh! deck building advice"
    )
    
    print(f"✅ Chain processing completed:")
    print(f"   Agents Responded: {len(chain_result.responses)}")
    print(f"   Total Tokens: {chain_result.total_tokens}")
    print(f"   Total Cost: ${chain_result.total_cost:.4f}")
    print(f"   Processing Time: {chain_result.processing_time:.2f}s")
    print(f"   Confidence Score: {chain_result.confidence_score:.2f}")
    
    # Step 3: Synthesize responses
    print(f"\n🔄 Synthesizing responses from multiple experts...")
    
    synthesis_result = response_synthesizer.synthesize_agent_responses(
        chain_result.responses, query
    )
    
    print(f"📋 Synthesis Results:")
    print(f"   Quality: {synthesis_result.synthesis_quality}")
    print(f"   Word Count: {synthesis_result.word_count}")
    print(f"   Key Insights: {len(synthesis_result.key_insights)}")
    print(f"   Action Items: {len(synthesis_result.action_items)}")
    print(f"   Confidence Score: {synthesis_result.confidence_score:.2f}")
    
    # Step 4: Display results
    print(f"\n" + "="*80)
    print("📝 COMPREHENSIVE BURN DECK ANALYSIS")
    print("="*80)
    
    print(synthesis_result.comprehensive_answer)
    
    if synthesis_result.key_insights:
        print(f"\n" + "="*50)
        print("💡 KEY INSIGHTS")
        print("="*50)
        for i, insight in enumerate(synthesis_result.key_insights, 1):
            print(f"{i}. {insight.content}")
            print(f"   Source: {', '.join(insight.source_agents)}")
            print(f"   Priority: {insight.priority}")
            print()
    
    if synthesis_result.action_items:
        print(f"\n" + "="*50)
        print("✅ ACTION ITEMS")
        print("="*50)
        for i, action in enumerate(synthesis_result.action_items, 1):
            print(f"{i}. {action}")
    
    # Step 5: Display individual agent responses
    print(f"\n" + "="*80)
    print("👥 INDIVIDUAL EXPERT PERSPECTIVES")
    print("="*80)
    
    for response in chain_result.responses:
        print(f"\n🎯 {response.agent_type} Analysis ({response.provider} - {response.model})")
        print(f"Perspective: {response.perspective}")
        print(f"Confidence: {response.confidence_score:.2f}")
        print(f"Tokens: {response.tokens_used} | Cost: ${response.cost:.4f}")
        print("-" * 60)
        print(response.content)
    
    return {
        'analysis': analysis,
        'chain_result': chain_result,
        'synthesis_result': synthesis_result
    }

if __name__ == "__main__":
    print("🚀 Starting Multi-Agent Yu-Gi-Oh! Burn Deck Analysis")
    print("=" * 80)
    
    try:
        results = test_burn_deck_analysis()
        print(f"\n✅ Analysis completed successfully!")
        print(f"Total processing time: {results['chain_result'].processing_time:.2f}s")
        print(f"Total cost: ${results['chain_result'].total_cost:.4f}")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()