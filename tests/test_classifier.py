"""
Unit Tests for Issue Classifier Module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.classifier import IssueClassifier


class TestIssueClassifier(unittest.TestCase):
    """Test cases for IssueClassifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = IssueClassifier()
    
    def test_classify_bug_issue(self):
        """Test classification of bug issues."""
        issue = {
            'title': 'Critical bug in login',
            'body': 'Application crashes when trying to login',
            'labels': [],
            'comments': 3
        }
        
        classification = self.classifier.classify_issue(issue)
        
        self.assertEqual(classification['type'], 'bug')
        self.assertIn('bug', classification['suggested_labels'])
    
    def test_classify_feature_issue(self):
        """Test classification of feature requests."""
        issue = {
            'title': 'Add new export feature',
            'body': 'Please implement CSV export functionality',
            'labels': [],
            'comments': 2
        }
        
        classification = self.classifier.classify_issue(issue)
        
        self.assertEqual(classification['type'], 'feature')
        self.assertIn('enhancement', classification['suggested_labels'])
    
    def test_classify_documentation_issue(self):
        """Test classification of documentation issues."""
        issue = {
            'title': 'Update API documentation',
            'body': 'The API docs need to be updated with new endpoints',
            'labels': [],
            'comments': 1
        }
        
        classification = self.classifier.classify_issue(issue)
        
        self.assertEqual(classification['type'], 'documentation')
        self.assertIn('documentation', classification['suggested_labels'])
    
    def test_classify_question_issue(self):
        """Test classification of questions."""
        issue = {
            'title': 'How to configure database?',
            'body': 'What is the correct way to set up the database connection?',
            'labels': [],
            'comments': 0
        }
        
        classification = self.classifier.classify_issue(issue)
        
        self.assertEqual(classification['type'], 'question')
        self.assertIn('question', classification['suggested_labels'])
    
    def test_determine_high_priority(self):
        """Test high priority detection."""
        issue = {
            'title': 'Critical security vulnerability',
            'body': 'Urgent: Security issue needs immediate attention',
            'labels': [],
            'comments': 10
        }
        
        classification = self.classifier.classify_issue(issue)
        
        self.assertEqual(classification['priority'], 'high')
        self.assertIn('priority:high', classification['suggested_labels'])
    
    def test_determine_low_priority(self):
        """Test low priority detection."""
        issue = {
            'title': 'Minor typo in UI',
            'body': 'There is a small typo in the button label',
            'labels': [],
            'comments': 0
        }
        
        classification = self.classifier.classify_issue(issue)
        
        self.assertEqual(classification['priority'], 'low')
        self.assertIn('priority:low', classification['suggested_labels'])
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        issue = {
            'title': 'Bug report error crash',
            'body': 'The application has a critical bug that causes crashes',
            'labels': [],
            'comments': 5
        }
        
        classification = self.classifier.classify_issue(issue)
        
        self.assertIn('confidence', classification)
        self.assertGreater(classification['confidence'], 0)
        self.assertLessEqual(classification['confidence'], 1.0)
    
    def test_batch_classify(self):
        """Test batch classification."""
        issues = [
            {
                'number': 1,
                'title': 'Bug in feature X',
                'body': 'Error occurs when using feature X',
                'labels': [],
                'comments': 2
            },
            {
                'number': 2,
                'title': 'Add feature Y',
                'body': 'Please implement feature Y',
                'labels': [],
                'comments': 1
            }
        ]
        
        results = self.classifier.batch_classify(issues)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['issue_number'], 1)
        self.assertEqual(results[0]['type'], 'bug')
        self.assertEqual(results[1]['issue_number'], 2)
        self.assertEqual(results[1]['type'], 'feature')


if __name__ == '__main__':
    unittest.main()
