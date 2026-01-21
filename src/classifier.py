"""
Issue Classifier Module
Classifies GitHub issues into categories and assigns priority levels
"""

from typing import Dict, List
import re
from collections import Counter


class IssueClassifier:
    """
    Classifier for GitHub issues to categorize and prioritize them.
    """
    
    # Keywords for different issue types
    BUG_KEYWORDS = ['bug', 'error', 'issue', 'crash', 'broken', 'fail', 'exception', 'problem']
    FEATURE_KEYWORDS = ['feature', 'enhancement', 'add', 'implement', 'support', 'new', 'request']
    DOCUMENTATION_KEYWORDS = ['document', 'docs', 'readme', 'guide', 'tutorial', 'help']
    QUESTION_KEYWORDS = ['question', 'how', 'why', 'what', 'when', 'where', 'help', '?']
    
    # Priority indicators
    HIGH_PRIORITY_KEYWORDS = ['urgent', 'critical', 'blocker', 'security', 'crash', 'data loss']
    MEDIUM_PRIORITY_KEYWORDS = ['important', 'needed', 'should', 'improvement']
    LOW_PRIORITY_KEYWORDS = ['minor', 'trivial', 'nice to have', 'cosmetic', 'typo']
    
    def __init__(self):
        """Initialize the IssueClassifier."""
        pass
    
    def classify_issue(self, issue: Dict) -> Dict:
        """
        Classify an issue into type and priority.
        
        Args:
            issue: Dictionary containing issue details
            
        Returns:
            Dictionary with classification results
        """
        title = (issue.get('title', '') or '').lower()
        body = (issue.get('body', '') or '').lower()
        text = f"{title} {body}"
        
        # Determine issue type
        issue_type = self._determine_type(text)
        
        # Determine priority
        priority = self._determine_priority(text, issue)
        
        # Generate suggested labels
        suggested_labels = self._suggest_labels(issue_type, priority)
        
        return {
            'type': issue_type,
            'priority': priority,
            'suggested_labels': suggested_labels,
            'confidence': self._calculate_confidence(text, issue_type)
        }
    
    def _determine_type(self, text: str) -> str:
        """
        Determine the type of issue based on text content.
        
        Args:
            text: Combined title and body text
            
        Returns:
            Issue type string
        """
        scores = {
            'bug': sum(1 for keyword in self.BUG_KEYWORDS if keyword in text),
            'feature': sum(1 for keyword in self.FEATURE_KEYWORDS if keyword in text),
            'documentation': sum(1 for keyword in self.DOCUMENTATION_KEYWORDS if keyword in text),
            'question': sum(1 for keyword in self.QUESTION_KEYWORDS if keyword in text)
        }
        
        # Return type with highest score, default to 'other' if all scores are 0
        max_score = max(scores.values())
        if max_score == 0:
            return 'other'
        
        return max(scores, key=scores.get)
    
    def _determine_priority(self, text: str, issue: Dict) -> str:
        """
        Determine the priority of an issue.
        
        Args:
            text: Combined title and body text
            issue: Issue dictionary
            
        Returns:
            Priority level string
        """
        # Check for high priority keywords
        high_score = sum(1 for keyword in self.HIGH_PRIORITY_KEYWORDS if keyword in text)
        medium_score = sum(1 for keyword in self.MEDIUM_PRIORITY_KEYWORDS if keyword in text)
        low_score = sum(1 for keyword in self.LOW_PRIORITY_KEYWORDS if keyword in text)
        
        # Check existing labels
        existing_labels = [label.lower() for label in issue.get('labels', [])]
        if any(label in ['critical', 'urgent', 'high'] for label in existing_labels):
            return 'high'
        elif any(label in ['low', 'minor'] for label in existing_labels):
            return 'low'
        
        # Determine based on keyword scores
        if high_score > 0:
            return 'high'
        elif low_score > 0:
            return 'low'
        elif medium_score > 0 or issue.get('comments', 0) > 5:
            return 'medium'
        else:
            return 'medium'  # Default priority
    
    def _suggest_labels(self, issue_type: str, priority: str) -> List[str]:
        """
        Suggest labels based on issue type and priority.
        
        Args:
            issue_type: Type of the issue
            priority: Priority level
            
        Returns:
            List of suggested label names
        """
        labels = []
        
        # Add type label
        if issue_type == 'bug':
            labels.append('bug')
        elif issue_type == 'feature':
            labels.append('enhancement')
        elif issue_type == 'documentation':
            labels.append('documentation')
        elif issue_type == 'question':
            labels.append('question')
        
        # Add priority label
        if priority == 'high':
            labels.append('priority:high')
        elif priority == 'medium':
            labels.append('priority:medium')
        elif priority == 'low':
            labels.append('priority:low')
        
        return labels
    
    def _calculate_confidence(self, text: str, issue_type: str) -> float:
        """
        Calculate confidence score for the classification.
        
        Args:
            text: Combined title and body text
            issue_type: Classified issue type
            
        Returns:
            Confidence score between 0 and 1
        """
        keywords_map = {
            'bug': self.BUG_KEYWORDS,
            'feature': self.FEATURE_KEYWORDS,
            'documentation': self.DOCUMENTATION_KEYWORDS,
            'question': self.QUESTION_KEYWORDS
        }
        
        if issue_type not in keywords_map:
            return 0.5  # Default confidence for 'other'
        
        # Count keyword matches
        matches = sum(1 for keyword in keywords_map[issue_type] if keyword in text)
        
        # Normalize confidence score
        max_possible = len(keywords_map[issue_type])
        confidence = min(1.0, matches / (max_possible * 0.3))  # 30% threshold for full confidence
        
        return round(confidence, 2)
    
    def batch_classify(self, issues: List[Dict]) -> List[Dict]:
        """
        Classify multiple issues at once.
        
        Args:
            issues: List of issue dictionaries
            
        Returns:
            List of classification results
        """
        results = []
        for issue in issues:
            classification = self.classify_issue(issue)
            results.append({
                'issue_number': issue.get('number'),
                'title': issue.get('title'),
                **classification
            })
        
        return results
