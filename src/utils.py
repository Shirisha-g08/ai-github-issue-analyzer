"""
Utility Functions Module
Helper functions for the GitHub Issue Assistant
"""

from typing import Dict, List
from datetime import datetime
import json


def format_timestamp(timestamp) -> str:
    """
    Format a timestamp to a readable string.
    
    Args:
        timestamp: Datetime object or string
        
    Returns:
        Formatted string
    """
    if isinstance(timestamp, str):
        return timestamp
    
    if hasattr(timestamp, 'strftime'):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    return str(timestamp)


def calculate_age_days(created_at) -> int:
    """
    Calculate the age of an issue in days.
    
    Args:
        created_at: Creation timestamp
        
    Returns:
        Age in days
    """
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    age = datetime.now(created_at.tzinfo) - created_at
    return age.days


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'


def save_to_json(data: Dict or List, filename: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: Output filename
        
    Returns:
        True if successful
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving to JSON: {str(e)}")
        return False


def load_from_json(filename: str) -> Dict or List or None:
    """
    Load data from a JSON file.
    
    Args:
        filename: Input filename
        
    Returns:
        Loaded data or None if error
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading from JSON: {str(e)}")
        return None


def format_issue_report(issue: Dict, analysis: Dict, classification: Dict) -> str:
    """
    Format a comprehensive issue report.
    
    Args:
        issue: Issue dictionary
        analysis: Analysis results
        classification: Classification results
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("="*60)
    report.append(f"ISSUE #{issue.get('number')}: {issue.get('title')}")
    report.append("="*60)
    report.append(f"\nState: {issue.get('state')}")
    report.append(f"Author: {issue.get('user')}")
    report.append(f"Created: {format_timestamp(issue.get('created_at'))}")
    report.append(f"URL: {issue.get('url', 'N/A')}")
    
    report.append(f"\n--- Classification ---")
    report.append(f"Type: {classification.get('type')}")
    report.append(f"Priority: {classification.get('priority')}")
    report.append(f"Suggested Labels: {', '.join(classification.get('suggested_labels', []))}")
    report.append(f"Confidence: {classification.get('confidence')}")
    
    report.append(f"\n--- Analysis ---")
    sentiment = analysis.get('sentiment', {})
    report.append(f"Sentiment: {sentiment.get('label')} (polarity: {sentiment.get('polarity')})")
    report.append(f"Complexity: {analysis.get('complexity', {}).get('level')}")
    report.append(f"Engagement: {analysis.get('engagement', {}).get('level')} ({analysis.get('engagement', {}).get('comments')} comments)")
    
    report.append(f"\n--- Summary ---")
    report.append(analysis.get('summary', 'No summary available'))
    
    report.append(f"\n--- Keywords ---")
    report.append(', '.join(analysis.get('keywords', [])))
    
    if analysis.get('complexity', {}).get('factors'):
        report.append(f"\n--- Complexity Factors ---")
        for factor in analysis['complexity']['factors']:
            report.append(f"  • {factor}")
    
    report.append("\n" + "="*60)
    
    return '\n'.join(report)


def generate_statistics(issues: List[Dict], classifications: List[Dict]) -> Dict:
    """
    Generate statistics from multiple issues.
    
    Args:
        issues: List of issues
        classifications: List of classifications
        
    Returns:
        Statistics dictionary
    """
    if not issues:
        return {}
    
    # Count by type
    types = {}
    priorities = {}
    states = {}
    
    for classification in classifications:
        issue_type = classification.get('type', 'unknown')
        priority = classification.get('priority', 'unknown')
        types[issue_type] = types.get(issue_type, 0) + 1
        priorities[priority] = priorities.get(priority, 0) + 1
    
    for issue in issues:
        state = issue.get('state', 'unknown')
        states[state] = states.get(state, 0) + 1
    
    # Calculate averages
    total_comments = sum(issue.get('comments', 0) for issue in issues)
    avg_comments = round(total_comments / len(issues), 2) if issues else 0
    
    return {
        'total_issues': len(issues),
        'types': types,
        'priorities': priorities,
        'states': states,
        'average_comments': avg_comments
    }
