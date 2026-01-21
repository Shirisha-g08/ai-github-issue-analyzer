"""
Unit Tests for GitHub API Module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.github_api import GitHubAPI


class TestGitHubAPI(unittest.TestCase):
    """Test cases for GitHubAPI class."""
    
    @patch('src.github_api.Github')
    def setUp(self, mock_github):
        """Set up test fixtures."""
        self.mock_github = mock_github
        self.api = GitHubAPI(token='test_token', owner='test_owner', repo='test_repo')
    
    def test_initialization(self):
        """Test GitHubAPI initialization."""
        self.assertIsNotNone(self.api)
        self.assertEqual(self.api.owner, 'test_owner')
        self.assertEqual(self.api.repo_name, 'test_repo')
    
    def test_initialization_without_token(self):
        """Test that initialization without token raises error."""
        with self.assertRaises(ValueError):
            GitHubAPI(token=None, owner='test', repo='test')
    
    @patch('src.github_api.Github')
    def test_get_issue(self, mock_github):
        """Test fetching a single issue."""
        # Mock issue object
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = 'Test Issue'
        mock_issue.body = 'Test body'
        mock_issue.state = 'open'
        mock_issue.labels = []
        mock_issue.created_at = '2024-01-01'
        mock_issue.updated_at = '2024-01-01'
        mock_issue.comments = 5
        mock_issue.user.login = 'testuser'
        mock_issue.html_url = 'https://github.com/test/test/issues/1'
        
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_issue.return_value = mock_issue
        
        api = GitHubAPI(token='test_token', owner='test_owner', repo='test_repo')
        api.repo = mock_repo
        
        issue = api.get_issue(1)
        
        self.assertEqual(issue['number'], 1)
        self.assertEqual(issue['title'], 'Test Issue')
        self.assertEqual(issue['state'], 'open')
    
    def test_get_issue_without_repo(self):
        """Test get_issue raises error when repo not set."""
        api = GitHubAPI(token='test_token')
        api.repo = None
        
        with self.assertRaises(ValueError):
            api.get_issue(1)


class TestGitHubAPIIntegration(unittest.TestCase):
    """Integration tests for GitHubAPI."""
    
    def test_mock_workflow(self):
        """Test complete workflow with mocked data."""
        # This test demonstrates how the API would work
        # In real scenarios, you would use actual GitHub credentials
        pass


if __name__ == '__main__':
    unittest.main()
