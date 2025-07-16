#!/usr/bin/env python3
"""
Simple test for burn deck analysis using available providers
"""

import sys
sys.path.append('.')

from query_analyzer import query_analyzer
from agent_chain_orchestrator import agent_orchestrator

def test_burn_deck():
    query = "Create a competitive Yu-Gi-Oh! burn deck for standard format with card explanations and strategy"
    
    print("Testing burn deck analysis...")
    
    # Test query analysis
    analysis = query_analyzer.analyze_user_query(query)
    print(f"Domain: {analysis.primary_domain}")
    print(f"Agents: {analysis.agent_chain}")
    print(f"Confidence: {analysis.confidence_score}")
    
    # Test with simplified chain using only Gaming_Expert
    if 'Gaming_Expert' in analysis.agent_chain:
        print("\nTesting Gaming_Expert...")
        result = agent_orchestrator.process_chain(
            query=query,
            agent_chain=['Gaming_Expert'],
            user_context="User wants Yu-Gi-Oh! deck building advice"
        )
        print(f"Responses: {len(result.responses)}")
        if result.responses:
            print(f"Provider: {result.responses[0].provider}")
            print(f"Tokens: {result.responses[0].tokens_used}")
            print(f"Cost: ${result.responses[0].cost:.4f}")
            print(f"Content preview: {result.responses[0].content[:200]}...")
    
    return analysis

if __name__ == "__main__":
    test_burn_deck()