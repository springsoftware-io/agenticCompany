#!/usr/bin/env python3
"""
Specialized Agents Demo

This example demonstrates how to use the specialized agents
(Marketing, Product, Sales) in various scenarios.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from github import Github
from agents import (
    MarketingAgent,
    ProductAgent,
    SalesAgent,
    AgentConfig,
    BaseIssueAgent
)
from logging_config import get_logger

logger = get_logger(__name__)


def example_1_basic_usage():
    """Example 1: Basic usage of each agent"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Setup (you would use real credentials)
    github_token = os.getenv("GITHUB_TOKEN", "demo_token")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    
    # Initialize GitHub
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "owner/repo"))
    
    # Create and run marketing agent
    print("\n📊 Running Marketing Agent...")
    marketing = MarketingAgent(
        repo=repo,
        anthropic_api_key=anthropic_key,
        dry_mode=True  # Test mode
    )
    marketing.check_and_generate()
    
    # Create and run product agent
    print("\n🚀 Running Product Agent...")
    product = ProductAgent(
        repo=repo,
        anthropic_api_key=anthropic_key,
        dry_mode=True
    )
    product.check_and_generate()
    
    # Create and run sales agent
    print("\n💰 Running Sales Agent...")
    sales = SalesAgent(
        repo=repo,
        anthropic_api_key=anthropic_key,
        dry_mode=True
    )
    sales.check_and_generate()


def example_2_custom_configuration():
    """Example 2: Using custom configurations"""
    print("\n" + "=" * 60)
    print("Example 2: Custom Configuration")
    print("=" * 60)
    
    github_token = os.getenv("GITHUB_TOKEN", "demo_token")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "owner/repo"))
    
    # Custom marketing configuration
    marketing_config = AgentConfig(
        domain="marketing",
        default_labels=["marketing", "growth", "priority"],
        min_issues=5,  # Maintain 5 marketing issues
        focus_areas=[
            "SEO optimization",
            "Content marketing",
            "Social media campaigns"
        ],
        priority_keywords=["seo", "content", "social"]
    )
    
    marketing = MarketingAgent(
        repo=repo,
        anthropic_api_key=anthropic_key,
        custom_config=marketing_config,
        dry_mode=True
    )
    
    print(f"Marketing Agent Config:")
    print(f"  Domain: {marketing.config.domain}")
    print(f"  Labels: {marketing.config.default_labels}")
    print(f"  Min Issues: {marketing.config.min_issues}")
    print(f"  Focus Areas: {len(marketing.config.focus_areas)}")


def example_3_batch_processing():
    """Example 3: Running all agents in batch"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Processing")
    print("=" * 60)
    
    github_token = os.getenv("GITHUB_TOKEN", "demo_token")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "owner/repo"))
    
    # Define all agents
    agents = [
        ("Marketing", MarketingAgent),
        ("Product", ProductAgent),
        ("Sales", SalesAgent)
    ]
    
    results = {}
    
    for name, AgentClass in agents:
        print(f"\n🔄 Processing {name} Agent...")
        
        agent = AgentClass(
            repo=repo,
            anthropic_api_key=anthropic_key,
            dry_mode=True
        )
        
        result = agent.check_and_generate()
        results[name] = result
        
        status = "✅ Generated" if result else "ℹ️  Skipped"
        print(f"   {status}")
    
    # Summary
    print("\n" + "-" * 60)
    print("Batch Processing Summary:")
    for name, result in results.items():
        status = "Generated issues" if result else "No action needed"
        print(f"  {name}: {status}")


def example_4_conditional_execution():
    """Example 4: Conditional execution based on repository state"""
    print("\n" + "=" * 60)
    print("Example 4: Conditional Execution")
    print("=" * 60)
    
    github_token = os.getenv("GITHUB_TOKEN", "demo_token")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "owner/repo"))
    
    # Get repository info
    print(f"\nRepository: {repo.full_name}")
    print(f"Stars: {repo.stargazers_count}")
    print(f"Open Issues: {repo.open_issues_count}")
    
    # Conditional logic based on repository state
    if repo.stargazers_count > 100:
        print("\n🎯 High visibility repo - Running marketing agent")
        marketing = MarketingAgent(
            repo=repo,
            anthropic_api_key=anthropic_key,
            dry_mode=True
        )
        marketing.check_and_generate()
    
    if repo.open_issues_count < 10:
        print("\n🚀 Low issue count - Running all agents")
        for AgentClass in [MarketingAgent, ProductAgent, SalesAgent]:
            agent = AgentClass(
                repo=repo,
                anthropic_api_key=anthropic_key,
                dry_mode=True
            )
            agent.check_and_generate()


def example_5_error_handling():
    """Example 5: Proper error handling"""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    github_token = os.getenv("GITHUB_TOKEN", "demo_token")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    
    try:
        g = Github(github_token)
        repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "owner/repo"))
        
        marketing = MarketingAgent(
            repo=repo,
            anthropic_api_key=anthropic_key,
            dry_mode=True
        )
        
        result = marketing.check_and_generate()
        
        if result:
            print("✅ Successfully generated marketing issues")
        else:
            print("ℹ️  No marketing issues needed")
            
    except Exception as e:
        logger.error(f"Error running marketing agent: {e}")
        print(f"❌ Error: {e}")
        # Handle error appropriately
        # - Log to monitoring system
        # - Send alert
        # - Retry with backoff
        # - Graceful degradation


def example_6_custom_agent():
    """Example 6: Creating a custom agent"""
    print("\n" + "=" * 60)
    print("Example 6: Custom Agent")
    print("=" * 60)
    
    from typing import Dict
    
    class EngineeringAgent(BaseIssueAgent):
        """Custom agent for engineering tasks"""
        
        def get_agent_config(self) -> AgentConfig:
            return AgentConfig(
                domain="engineering",
                default_labels=["engineering", "technical"],
                min_issues=3,
                focus_areas=[
                    "Code quality improvements",
                    "Technical debt reduction",
                    "Performance optimization",
                    "Infrastructure improvements"
                ],
                priority_keywords=["performance", "optimization", "refactor"]
            )
        
        def build_domain_prompt(self, context: Dict) -> str:
            config = self.get_agent_config()
            
            prompt = f"""
🔧 ENGINEERING FOCUS AREAS:
{chr(10).join([f"  • {area}" for area in config.focus_areas])}

Your task is to identify {context['needed']} engineering improvements.

Consider:
1. **Code Quality**: What can be refactored or improved?
2. **Performance**: Where are the bottlenecks?
3. **Technical Debt**: What needs to be addressed?
4. **Infrastructure**: How can we improve reliability?

Focus on actionable engineering tasks.
"""
            return prompt
    
    # Use the custom agent
    github_token = os.getenv("GITHUB_TOKEN", "demo_token")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "owner/repo"))
    
    print("\n🔧 Running Custom Engineering Agent...")
    engineering = EngineeringAgent(
        repo=repo,
        anthropic_api_key=anthropic_key,
        dry_mode=True
    )
    
    print(f"Domain: {engineering.config.domain}")
    print(f"Labels: {engineering.config.default_labels}")
    print(f"Focus Areas: {engineering.config.focus_areas}")


def example_7_monitoring_and_metrics():
    """Example 7: Monitoring agent performance"""
    print("\n" + "=" * 60)
    print("Example 7: Monitoring and Metrics")
    print("=" * 60)
    
    github_token = os.getenv("GITHUB_TOKEN", "demo_token")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "demo_key")
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "owner/repo"))
    
    marketing = MarketingAgent(
        repo=repo,
        anthropic_api_key=anthropic_key,
        dry_mode=True
    )
    
    # Check rate limiter status before running
    can_generate, reason = marketing.rate_limiter.can_generate()
    print(f"\nCan generate: {can_generate}")
    if not can_generate:
        print(f"Reason: {reason}")
    
    # Get rate limiter statistics
    stats = marketing.rate_limiter.get_statistics()
    print(f"\nRate Limiter Statistics:")
    print(f"  Issues today: {stats.get('issues_today', 0)}")
    print(f"  Issues this hour: {stats.get('issues_this_hour', 0)}")
    print(f"  Duplicate rate: {stats.get('duplicate_rate', 0):.1%}")
    
    # Run agent
    result = marketing.check_and_generate()
    
    # Check outcome tracker
    overall_stats = marketing.outcome_tracker.get_overall_stats()
    print(f"\nOutcome Tracker Statistics:")
    print(f"  Total attempts: {overall_stats.get('total_attempts', 0)}")
    print(f"  Success rate: {overall_stats.get('success_rate', 0):.1%}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Specialized Agents Demo")
    print("=" * 60)
    
    examples = [
        ("Basic Usage", example_1_basic_usage),
        ("Custom Configuration", example_2_custom_configuration),
        ("Batch Processing", example_3_batch_processing),
        ("Conditional Execution", example_4_conditional_execution),
        ("Error Handling", example_5_error_handling),
        ("Custom Agent", example_6_custom_agent),
        ("Monitoring and Metrics", example_7_monitoring_and_metrics),
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nNote: Set GITHUB_TOKEN and ANTHROPIC_API_KEY to run examples")
    print("      Examples run in dry mode by default (no actual issues created)")
    
    # Uncomment to run specific examples:
    # example_1_basic_usage()
    # example_2_custom_configuration()
    # example_3_batch_processing()
    # example_4_conditional_execution()
    # example_5_error_handling()
    # example_6_custom_agent()
    # example_7_monitoring_and_metrics()


if __name__ == "__main__":
    main()
