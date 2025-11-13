#!/usr/bin/env python3
"""
QA Agent
Monitors repository health by reviewing issues, PRs, and commits
Reports problems by creating issues
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from github import Github, Auth

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'claude-agent'))

# Import Claude CLI Agent or fallback to Anthropic SDK
try:
    from claude_cli_agent import ClaudeAgent
    USE_CLAUDE_CLI = True
except ImportError:
    print("⚠️  claude_cli_agent not available, using Anthropic SDK")
    USE_CLAUDE_CLI = False
    try:
        from anthropic import Anthropic
    except ImportError:
        print("❌ Neither claude_cli_agent nor anthropic SDK available")
        sys.exit(1)

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
REPO_NAME = os.getenv('REPO_NAME')
MAX_ISSUES_TO_REVIEW = int(os.getenv('MAX_ISSUES_TO_REVIEW', '10'))
MAX_PRS_TO_REVIEW = int(os.getenv('MAX_PRS_TO_REVIEW', '5'))
MAX_COMMITS_TO_REVIEW = int(os.getenv('MAX_COMMITS_TO_REVIEW', '10'))

print("🔍 QA Agent Starting")
print(f"📊 Will review: {MAX_ISSUES_TO_REVIEW} issues, {MAX_PRS_TO_REVIEW} PRs, {MAX_COMMITS_TO_REVIEW} commits")

# Initialize GitHub client
auth = Auth.Token(GITHUB_TOKEN)
gh = Github(auth=auth)
repo = gh.get_repo(REPO_NAME)

def gather_repository_context():
    """Gather context about recent repository activity"""
    
    print("📖 Gathering repository context...")
    
    context = {
        'issues': [],
        'pull_requests': [],
        'commits': [],
        'repo_info': {}
    }
    
    # Get repository info
    context['repo_info'] = {
        'name': repo.name,
        'description': repo.description,
        'open_issues_count': repo.open_issues_count,
        'stargazers_count': repo.stargazers_count,
        'language': repo.language
    }
    
    # Get recent issues
    print(f"📋 Reviewing {MAX_ISSUES_TO_REVIEW} recent issues...")
    issues = list(repo.get_issues(state='all', sort='updated', direction='desc'))[:MAX_ISSUES_TO_REVIEW]
    for issue in issues:
        if issue.pull_request:
            continue
        context['issues'].append({
            'number': issue.number,
            'title': issue.title,
            'state': issue.state,
            'labels': [label.name for label in issue.labels],
            'created_at': issue.created_at.isoformat(),
            'updated_at': issue.updated_at.isoformat(),
            'body': (issue.body or '')[:500]  # First 500 chars
        })
    
    # Get recent pull requests
    print(f"🔀 Reviewing {MAX_PRS_TO_REVIEW} recent pull requests...")
    prs = list(repo.get_pulls(state='all', sort='updated', direction='desc'))[:MAX_PRS_TO_REVIEW]
    for pr in prs:
        context['pull_requests'].append({
            'number': pr.number,
            'title': pr.title,
            'state': pr.state,
            'merged': pr.merged,
            'created_at': pr.created_at.isoformat(),
            'updated_at': pr.updated_at.isoformat(),
            'additions': pr.additions,
            'deletions': pr.deletions,
            'changed_files': pr.changed_files
        })
    
    # Get recent commits
    print(f"📝 Reviewing {MAX_COMMITS_TO_REVIEW} recent commits...")
    commits = list(repo.get_commits())[:MAX_COMMITS_TO_REVIEW]
    for commit in commits:
        context['commits'].append({
            'sha': commit.sha[:8],
            'message': commit.commit.message.split('\n')[0][:100],
            'author': commit.commit.author.name,
            'date': commit.commit.author.date.isoformat(),
            'files_changed': len(commit.files) if commit.files else 0
        })
    
    print(f"✅ Gathered context: {len(context['issues'])} issues, {len(context['pull_requests'])} PRs, {len(context['commits'])} commits")
    return context

def run_qa_analysis(context):
    """Run QA analysis using Claude AI"""
    
    # Build comprehensive prompt
    prompt = f"""You are a QA engineer reviewing the AutoGrow repository: {REPO_NAME}

Your job is to analyze recent activity and identify any problems, inconsistencies, or areas of concern.

## Repository Overview
- Name: {context['repo_info']['name']}
- Description: {context['repo_info']['description']}
- Open Issues: {context['repo_info']['open_issues_count']}
- Language: {context['repo_info']['language']}

## Recent Issues ({len(context['issues'])})
"""
    
    for issue in context['issues']:
        prompt += f"\n### Issue #{issue['number']}: {issue['title']}\n"
        prompt += f"- State: {issue['state']}\n"
        prompt += f"- Labels: {', '.join(issue['labels'])}\n"
        prompt += f"- Created: {issue['created_at']}\n"
        if issue['body']:
            prompt += f"- Description: {issue['body'][:200]}...\n"
    
    prompt += f"\n## Recent Pull Requests ({len(context['pull_requests'])})\n"
    for pr in context['pull_requests']:
        prompt += f"\n### PR #{pr['number']}: {pr['title']}\n"
        prompt += f"- State: {pr['state']}, Merged: {pr['merged']}\n"
        prompt += f"- Changes: +{pr['additions']} -{pr['deletions']} in {pr['changed_files']} files\n"
        prompt += f"- Updated: {pr['updated_at']}\n"
    
    prompt += f"\n## Recent Commits ({len(context['commits'])})\n"
    for commit in context['commits']:
        prompt += f"- [{commit['sha']}] {commit['message']} by {commit['author']} ({commit['files_changed']} files)\n"
    
    prompt += """

## Your Task

Analyze the above information and identify any problems or concerns:

1. **Code Quality Issues**
   - Are there PRs that should have been merged but weren't?
   - Are there stale issues or PRs?
   - Are commit messages clear and descriptive?

2. **Process Issues**
   - Are issues properly labeled?
   - Are there duplicate issues?
   - Are PRs being reviewed in a timely manner?

3. **Project Health**
   - Is the project progressing well?
   - Are there any red flags?
   - Are the AI agents working correctly?

4. **Specific Problems**
   - Any broken workflows?
   - Any security concerns?
   - Any performance issues mentioned?

Respond in this EXACT JSON format:
{
  "status": "healthy" or "warning" or "critical",
  "summary": "Brief overall assessment (max 200 chars)",
  "problems": [
    {
      "severity": "low" or "medium" or "high",
      "category": "code_quality" or "process" or "health" or "security",
      "title": "Brief problem title (max 80 chars)",
      "description": "Detailed description (max 300 chars)",
      "recommendation": "What should be done (max 200 chars)"
    }
  ],
  "positive_observations": [
    "Things that are going well (max 150 chars each)"
  ]
}

If everything looks good, return status "healthy" with empty problems array.
Output ONLY the JSON, nothing else.
"""

    print(f"📝 Prompt length: {len(prompt)} chars")
    
    # Call Claude AI
    try:
        if USE_CLAUDE_CLI:
            print("🤖 Using Claude CLI...")
            agent = ClaudeAgent(output_format="text", verbose=False)
            result = agent.query(
                prompt,
                system_prompt="You are a QA engineer. Always respond with valid JSON only."
            )
            if isinstance(result, dict) and "result" in result:
                response_text = result["result"]
            else:
                response_text = str(result)
        else:
            print("🤖 Using Anthropic API...")
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                system="You are a QA engineer. Always respond with valid JSON only.",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
        
        print(f"✅ Received response ({len(response_text)} chars)")
        return response_text
        
    except Exception as e:
        print(f"❌ Error calling Claude: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_and_act_on_results(response_text):
    """Parse QA results and create issues if needed"""
    
    import json
    
    try:
        # Clean up response
        cleaned = response_text.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        
        # Find JSON object
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = cleaned[start_idx:end_idx]
        data = json.loads(json_str)
        
        status = data.get('status', 'unknown')
        summary = data.get('summary', '')
        problems = data.get('problems', [])
        positive = data.get('positive_observations', [])
        
        print(f"\n{'='*60}")
        print(f"📊 QA Status: {status.upper()}")
        print(f"📝 Summary: {summary}")
        print(f"{'='*60}\n")
        
        # Show positive observations
        if positive:
            print("✅ Positive Observations:")
            for obs in positive:
                print(f"   ✓ {obs}")
            print()
        
        # Show problems
        if problems:
            print(f"⚠️  Found {len(problems)} problem(s):")
            for i, problem in enumerate(problems, 1):
                severity = problem.get('severity', 'unknown')
                category = problem.get('category', 'unknown')
                title = problem.get('title', 'Untitled')
                description = problem.get('description', '')
                recommendation = problem.get('recommendation', '')
                
                emoji = {'low': '🟡', 'medium': '🟠', 'high': '🔴'}.get(severity, '⚪')
                print(f"\n   {emoji} Problem {i}: {title}")
                print(f"      Severity: {severity} | Category: {category}")
                print(f"      {description}")
                if recommendation:
                    print(f"      💡 Recommendation: {recommendation}")
            
            # Create issue for problems
            if status in ['warning', 'critical']:
                create_qa_issue(status, summary, problems, positive)
        else:
            print("✅ No problems found - repository health looks good!")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse QA response as JSON: {e}")
        print(f"Response: {response_text[:500]}")
        return False
    except Exception as e:
        print(f"❌ Error processing results: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_qa_issue(status, summary, problems, positive):
    """Create a GitHub issue for QA findings"""
    
    print(f"\n📝 Creating QA issue for {status} status...")
    
    # Build issue body
    severity_emoji = {'warning': '⚠️', 'critical': '🔴'}.get(status, '⚠️')
    
    body = f"""# {severity_emoji} QA Agent Report - {status.upper()}

**Summary:** {summary}

**Scan Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 🔍 Problems Detected

"""
    
    for i, problem in enumerate(problems, 1):
        severity = problem.get('severity', 'unknown')
        category = problem.get('category', 'unknown')
        title = problem.get('title', 'Untitled')
        description = problem.get('description', '')
        recommendation = problem.get('recommendation', '')
        
        emoji = {'low': '🟡', 'medium': '🟠', 'high': '🔴'}.get(severity, '⚪')
        
        body += f"""
### {emoji} Problem {i}: {title}

**Severity:** {severity.upper()}  
**Category:** {category}

**Description:**  
{description}

**Recommendation:**  
{recommendation}

---
"""
    
    # Add positive observations if any
    if positive:
        body += "\n## ✅ Positive Observations\n\n"
        for obs in positive:
            body += f"- {obs}\n"
        body += "\n---\n"
    
    body += "\n*Generated by QA Agent*"
    
    # Determine labels
    labels = ['qa-report']
    if status == 'critical':
        labels.append('priority-high')
    elif status == 'warning':
        labels.append('priority-medium')
    
    # Add category labels
    categories = set(p.get('category', '') for p in problems)
    for cat in categories:
        if cat in ['security', 'code_quality', 'process', 'health']:
            labels.append(cat)
    
    # Create the issue
    try:
        issue_title = f"QA Report: {summary[:60]}"
        new_issue = repo.create_issue(
            title=issue_title,
            body=body,
            labels=labels
        )
        print(f"✅ Created QA issue #{new_issue.number}: {issue_title}")
        return new_issue
    except Exception as e:
        print(f"❌ Failed to create issue: {e}")
        return None

# Main execution
try:
    context = gather_repository_context()
    response = run_qa_analysis(context)
    
    if response:
        parse_and_act_on_results(response)
        print("\n🎉 QA Agent completed successfully")
    else:
        print("\n❌ QA Agent failed to get analysis")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
