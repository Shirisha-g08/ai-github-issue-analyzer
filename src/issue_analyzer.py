"""
Issue Analyzer Module
Analyzes GitHub issues for sentiment, generates summaries, and provides insights
"""

from typing import Dict, List
from textblob import TextBlob
import re


class IssueAnalyzer:
    """
    Analyzer for GitHub issues providing sentiment analysis, summarization, and insights.
    """
    
    def __init__(self):
        """Initialize the IssueAnalyzer."""
        pass
    
    def analyze_issue(self, issue: Dict) -> Dict:
        """
        Perform comprehensive analysis on an issue.
        
        Args:
            issue: Dictionary containing issue details
            
        Returns:
            Dictionary with analysis results
        """
        title = issue.get('title', '')
        body = issue.get('body', '') or ''
        
        # Perform various analyses
        sentiment = self.analyze_sentiment(title, body)
        summary = self.generate_summary(title, body)
        keywords = self.extract_keywords(title, body)
        complexity = self.assess_complexity(body)
        
        return {
            'issue_number': issue.get('number'),
            'sentiment': sentiment,
            'summary': summary,
            'keywords': keywords,
            'complexity': complexity,
            'engagement': self.calculate_engagement(issue)
        }
    
    def analyze_sentiment(self, title: str, body: str) -> Dict:
        """
        Analyze sentiment of issue text.
        
        Args:
            title: Issue title
            body: Issue body text
            
        Returns:
            Dictionary with sentiment scores
        """
        text = f"{title}. {body}"
        
        # Use TextBlob for sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment_label = 'positive'
        elif polarity < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'label': sentiment_label,
            'polarity': round(polarity, 2),
            'subjectivity': round(subjectivity, 2)
        }
    
    def generate_summary(self, title: str, body: str, max_length: int = 150) -> str:
        """
        Generate a concise summary of the issue.
        
        Args:
            title: Issue title
            body: Issue body text
            max_length: Maximum length of summary
            
        Returns:
            Summary string
        """
        if not body:
            return title
        
        # Extract first meaningful paragraph
        paragraphs = body.split('\n\n')
        first_paragraph = paragraphs[0] if paragraphs else body
        
        # Clean up markdown and special characters
        clean_text = re.sub(r'[#*`\[\]()]', '', first_paragraph)
        clean_text = ' '.join(clean_text.split())  # Normalize whitespace
        
        # Truncate to max length
        if len(clean_text) > max_length:
            summary = clean_text[:max_length].rsplit(' ', 1)[0] + '...'
        else:
            summary = clean_text
        
        return summary or title
    
    def extract_keywords(self, title: str, body: str, top_n: int = 5) -> List[str]:
        """
        Extract key terms from the issue.
        
        Args:
            title: Issue title
            body: Issue body text
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        text = f"{title} {body}".lower()
        
        # Remove common words and special characters
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'this', 'that', 'these', 'those', 'i', 'you', 'we', 'they', 'it'}
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Filter and count
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:top_n]]
        
        return keywords
    
    def assess_complexity(self, body: str) -> Dict:
        """
        Assess the complexity of an issue based on its description.
        
        Args:
            body: Issue body text
            
        Returns:
            Dictionary with complexity assessment
        """
        if not body:
            return {
                'level': 'simple',
                'score': 0,
                'factors': []
            }
        
        score = 0
        factors = []
        
        # Check various complexity indicators
        word_count = len(body.split())
        if word_count > 500:
            score += 2
            factors.append('lengthy description')
        elif word_count > 200:
            score += 1
            factors.append('detailed description')
        
        # Check for code blocks
        code_blocks = len(re.findall(r'```[\s\S]*?```', body))
        if code_blocks > 2:
            score += 2
            factors.append('multiple code examples')
        elif code_blocks > 0:
            score += 1
            factors.append('includes code')
        
        # Check for error messages
        if re.search(r'error|exception|traceback', body, re.IGNORECASE):
            score += 1
            factors.append('contains errors')
        
        # Check for multiple steps
        numbered_steps = len(re.findall(r'^\d+\.', body, re.MULTILINE))
        if numbered_steps > 5:
            score += 2
            factors.append('complex reproduction steps')
        elif numbered_steps > 2:
            score += 1
            factors.append('has reproduction steps')
        
        # Determine complexity level
        if score >= 5:
            level = 'complex'
        elif score >= 3:
            level = 'moderate'
        else:
            level = 'simple'
        
        return {
            'level': level,
            'score': score,
            'factors': factors
        }
    
    def calculate_engagement(self, issue: Dict) -> Dict:
        """
        Calculate engagement metrics for an issue.
        
        Args:
            issue: Issue dictionary
            
        Returns:
            Dictionary with engagement metrics
        """
        comments = issue.get('comments', 0)
        
        # Determine engagement level
        if comments >= 10:
            engagement_level = 'high'
        elif comments >= 5:
            engagement_level = 'medium'
        else:
            engagement_level = 'low'
        
        return {
            'level': engagement_level,
            'comments': comments
        }
    
    def compare_issues(self, issue1: Dict, issue2: Dict) -> Dict:
        """
        Compare two issues for similarity.
        
        Args:
            issue1: First issue dictionary
            issue2: Second issue dictionary
            
        Returns:
            Dictionary with similarity score and analysis
        """
        # Extract text
        text1 = f"{issue1.get('title', '')} {issue1.get('body', '')}"
        text2 = f"{issue2.get('title', '')} {issue2.get('body', '')}"
        
        # Extract keywords from both
        keywords1 = set(self.extract_keywords(issue1.get('title', ''), issue1.get('body', ''), 10))
        keywords2 = set(self.extract_keywords(issue2.get('title', ''), issue2.get('body', ''), 10))
        
        # Calculate Jaccard similarity
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        similarity = round(intersection / union if union > 0 else 0, 2)
        
        return {
            'similarity_score': similarity,
            'common_keywords': list(keywords1 & keywords2),
            'is_similar': similarity > 0.3
        }
