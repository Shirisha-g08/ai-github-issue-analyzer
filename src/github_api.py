"""
GitHub API Integration Module
Handles all interactions with GitHub API for fetching and managing issues
"""

import os
from typing import List, Dict, Optional
from github import Github, GithubException
from dotenv import load_dotenv

load_dotenv()


class GitHubAPI:
    """
    GitHubAPI class for interacting with GitHub repositories and issues.
    """
    
    def __init__(self, token: Optional[str] = None, owner: Optional[str] = None, repo: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token (optional for public repos)
            owner: Repository owner username
            repo: Repository name
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.owner = owner or os.getenv('GITHUB_REPO_OWNER')
        self.repo_name = repo or os.getenv('GITHUB_REPO_NAME')
        
        # Token is optional - works for public repos without authentication
        if self.token:
            self.client = Github(self.token)
        else:
            # Unauthenticated access (rate limit: 60 requests/hour for public repos)
            self.client = Github()
        
        self.repo = None
        
        if self.owner and self.repo_name:
            try:
                self.repo = self.client.get_repo(f"{self.owner}/{self.repo_name}")
            except GithubException as e:
                raise Exception(f"Error accessing repository {self.owner}/{self.repo_name}: {str(e)}")
    
    def get_issue(self, issue_number: int) -> Dict:
        """
        Fetch a specific issue by number.
        
        Args:
            issue_number: The issue number to fetch
            
        Returns:
            Dictionary containing issue details
        """
        if not self.repo:
            raise ValueError("Repository not set. Provide owner and repo name.")
        
        try:
            issue = self.repo.get_issue(issue_number)
            return {
                'number': issue.number,
                'title': issue.title,
                'body': issue.body,
                'state': issue.state,
                'labels': [label.name for label in issue.labels],
                'created_at': issue.created_at,
                'updated_at': issue.updated_at,
                'comments': issue.comments,
                'user': issue.user.login,
                'url': issue.html_url
            }
        except GithubException as e:
            raise Exception(f"Error fetching issue #{issue_number}: {str(e)}")
    
    def get_all_issues(self, state: str = 'open', max_issues: int = 100) -> List[Dict]:
        """
        Fetch all issues from the repository.
        
        Args:
            state: Issue state ('open', 'closed', or 'all')
            max_issues: Maximum number of issues to fetch
            
        Returns:
            List of issue dictionaries
        """
        if not self.repo:
            raise ValueError("Repository not set. Provide owner and repo name.")
        
        issues = []
        try:
            for issue in self.repo.get_issues(state=state)[:max_issues]:
                if not issue.pull_request:  # Exclude pull requests
                    issues.append({
                        'number': issue.number,
                        'title': issue.title,
                        'body': issue.body,
                        'state': issue.state,
                        'labels': [label.name for label in issue.labels],
                        'created_at': issue.created_at,
                        'updated_at': issue.updated_at,
                        'comments': issue.comments,
                        'user': issue.user.login
                    })
        except GithubException as e:
            raise Exception(f"Error fetching issues: {str(e)}")
        
        return issues
    
    def get_issue_comments(self, issue_number: int) -> List[Dict]:
        """
        Fetch all comments for a specific issue.
        
        Args:
            issue_number: The issue number
            
        Returns:
            List of comment dictionaries
        """
        if not self.repo:
            raise ValueError("Repository not set. Provide owner and repo name.")
        
        try:
            issue = self.repo.get_issue(issue_number)
            comments = []
            for comment in issue.get_comments():
                comments.append({
                    'id': comment.id,
                    'user': comment.user.login,
                    'body': comment.body,
                    'created_at': comment.created_at,
                    'updated_at': comment.updated_at
                })
            return comments
        except GithubException as e:
            raise Exception(f"Error fetching comments for issue #{issue_number}: {str(e)}")
    
    def add_labels_to_issue(self, issue_number: int, labels: List[str]) -> bool:
        """
        Add labels to an issue.
        
        Args:
            issue_number: The issue number
            labels: List of label names to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            raise ValueError("Repository not set. Provide owner and repo name.")
        
        try:
            issue = self.repo.get_issue(issue_number)
            issue.add_to_labels(*labels)
            return True
        except GithubException as e:
            print(f"Error adding labels to issue #{issue_number}: {str(e)}")
            return False
    
    def add_comment_to_issue(self, issue_number: int, comment: str) -> bool:
        """
        Add a comment to an issue.
        
        Args:
            issue_number: The issue number
            comment: Comment text to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            raise ValueError("Repository not set. Provide owner and repo name.")
        
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            return True
        except GithubException as e:
            print(f"Error adding comment to issue #{issue_number}: {str(e)}")
            return False
