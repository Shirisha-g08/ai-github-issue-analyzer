"""
Unit Tests for Issue Analyzer Module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.issue_analyzer import IssueAnalyzer


class TestIssueAnalyzer(unittest.TestCase):
    """Test cases for IssueAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = IssueAnalyzer()
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis with positive text."""
        sentiment = self.analyzer.analyze_sentiment(
            'Great feature!',
            'This is an amazing addition to the project.'
        )
        
        self.assertEqual(sentiment['label'], 'positive')
        self.assertGreater(sentiment['polarity'], 0)
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis with negative text."""
        sentiment = self.analyzer.analyze_sentiment(
            'Critical bug',
            'This is a terrible error that breaks everything.'
        )
        
        self.assertEqual(sentiment['label'], 'negative')
        self.assertLess(sentiment['polarity'], 0)
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis with neutral text."""
        sentiment = self.analyzer.analyze_sentiment(
            'Update documentation',
            'The readme file needs to be updated.'
        )
        
        self.assertEqual(sentiment['label'], 'neutral')
    
    def test_generate_summary(self):
        """Test summary generation."""
        body = 'This is a test issue. ' * 50
        summary = self.analyzer.generate_summary('Test', body, max_length=50)
        
        self.assertLessEqual(len(summary), 53)  # 50 + '...'
        self.assertTrue(summary.endswith('...'))
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        keywords = self.analyzer.extract_keywords(
            'Database connection error',
            'The database connection fails when trying to connect to the server.'
        )
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        self.assertIn('database', keywords)
    
    def test_assess_complexity_simple(self):
        """Test complexity assessment for simple issue."""
        complexity = self.analyzer.assess_complexity('Short description')
        
        self.assertEqual(complexity['level'], 'simple')
        self.assertEqual(complexity['score'], 0)
    
    def test_assess_complexity_moderate(self):
        """Test complexity assessment for moderate issue."""
        body = '''
        This is a test issue with code and detailed steps.
        
        Error message:
        Traceback (most recent call last):
        File "test.py", line 10, in main
            raise Exception("Critical error occurred")
        
        ```python
        def test():
            pass
        ```
        
        ```python
        def another_function():
            return None
        ```
        
        Steps to reproduce:
        1. Step one
        2. Step two
        3. Step three
        4. Step four
        5. Step five
        6. Step six
        '''
        
        complexity = self.analyzer.assess_complexity(body)
        
        # Verify the structure of the complexity assessment
        self.assertIn('level', complexity)
        self.assertIn('score', complexity)
        self.assertIn('factors', complexity)
        self.assertIsInstance(complexity['factors'], list)
        # Should detect code blocks and error message
        self.assertGreaterEqual(len(complexity['factors']), 2)
    
    def test_calculate_engagement(self):
        """Test engagement calculation."""
        issue = {'comments': 15}
        engagement = self.analyzer.calculate_engagement(issue)
        
        self.assertEqual(engagement['level'], 'high')
        self.assertEqual(engagement['comments'], 15)
    
    def test_compare_issues(self):
        """Test issue comparison."""
        issue1 = {
            'title': 'Database connection error',
            'body': 'Cannot connect to PostgreSQL database'
        }
        issue2 = {
            'title': 'Database timeout',
            'body': 'PostgreSQL connection times out'
        }
        
        comparison = self.analyzer.compare_issues(issue1, issue2)
        
        self.assertIn('similarity_score', comparison)
        self.assertIn('common_keywords', comparison)
        self.assertGreater(comparison['similarity_score'], 0)


if __name__ == '__main__':
    unittest.main()
