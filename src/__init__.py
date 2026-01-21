"""
GitHub Issue Assistant - Main Package
"""

__version__ = '1.0.0'
__author__ = 'Seedling Labs Engineering Intern'

from .github_api import GitHubAPI
from .issue_analyzer import IssueAnalyzer
from .classifier import IssueClassifier

__all__ = ['GitHubAPI', 'IssueAnalyzer', 'IssueClassifier']
