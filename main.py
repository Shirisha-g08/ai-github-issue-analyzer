"""
Main Application Entry Point
Demonstrates the usage of the GitHub Issue Assistant
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.github_api import GitHubAPI
from src.issue_analyzer import IssueAnalyzer
from src.classifier import IssueClassifier
from src.utils import format_issue_report, generate_statistics, save_to_json

# Load environment variables
load_dotenv()


class GitHubIssueAssistant:
    """
    Main class for the GitHub Issue Assistant application.
    """
    
    def __init__(self, token=None, owner=None, repo=None):
        """
        Initialize the GitHub Issue Assistant.
        
        Args:
            token: GitHub personal access token
            owner: Repository owner
            repo: Repository name
        """
        self.github_api = GitHubAPI(token, owner, repo)
        self.analyzer = IssueAnalyzer()
        self.classifier = IssueClassifier()
    
    def analyze_issue(self, issue_number: int, verbose: bool = True) -> dict:
        """
        Analyze a single issue comprehensively.
        
        Args:
            issue_number: The issue number to analyze
            verbose: Whether to print detailed output
            
        Returns:
            Dictionary with all analysis results
        """
        try:
            # Fetch issue
            if verbose:
                print(f"\nFetching issue #{issue_number}...")
            
            issue = self.github_api.get_issue(issue_number)
            
            # Analyze issue
            if verbose:
                print("Analyzing issue...")
            
            analysis = self.analyzer.analyze_issue(issue)
            classification = self.classifier.classify_issue(issue)
            
            # Fetch comments
            comments = self.github_api.get_issue_comments(issue_number)
            
            result = {
                'issue': issue,
                'analysis': analysis,
                'classification': classification,
                'comments': comments
            }
            
            if verbose:
                report = format_issue_report(issue, analysis, classification)
                print(report)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing issue #{issue_number}: {str(e)}")
            return None
    
    def analyze_all_issues(self, state: str = 'open', max_issues: int = 50, save_results: bool = True):
        """
        Analyze all issues in the repository.
        
        Args:
            state: Issue state ('open', 'closed', or 'all')
            max_issues: Maximum number of issues to analyze
            save_results: Whether to save results to file
        """
        try:
            print(f"\nFetching {state} issues...")
            issues = self.github_api.get_all_issues(state=state, max_issues=max_issues)
            
            if not issues:
                print("No issues found.")
                return
            
            print(f"Found {len(issues)} issues. Analyzing...")
            
            results = []
            classifications = []
            
            for i, issue in enumerate(issues, 1):
                print(f"\nAnalyzing issue {i}/{len(issues)}: #{issue['number']}")
                
                analysis = self.analyzer.analyze_issue(issue)
                classification = self.classifier.classify_issue(issue)
                
                results.append({
                    'issue_number': issue['number'],
                    'title': issue['title'],
                    'analysis': analysis,
                    'classification': classification
                })
                
                classifications.append(classification)
            
            # Generate statistics
            print("\n" + "="*60)
            print("ANALYSIS COMPLETE - STATISTICS")
            print("="*60)
            
            stats = generate_statistics(issues, classifications)
            
            print(f"\nTotal Issues: {stats['total_issues']}")
            print(f"\nIssue Types:")
            for issue_type, count in stats['types'].items():
                print(f"  {issue_type}: {count}")
            
            print(f"\nPriorities:")
            for priority, count in stats['priorities'].items():
                print(f"  {priority}: {count}")
            
            print(f"\nStates:")
            for state, count in stats['states'].items():
                print(f"  {state}: {count}")
            
            print(f"\nAverage Comments: {stats['average_comments']}")
            
            # Save results
            if save_results:
                output_file = f"issue_analysis_{state}.json"
                if save_to_json({'results': results, 'statistics': stats}, output_file):
                    print(f"\nResults saved to {output_file}")
            
            return results
            
        except Exception as e:
            print(f"Error analyzing issues: {str(e)}")
            return None
    
    def suggest_labels_for_issue(self, issue_number: int, apply_labels: bool = False) -> list:
        """
        Suggest labels for an issue and optionally apply them.
        
        Args:
            issue_number: The issue number
            apply_labels: Whether to apply the suggested labels
            
        Returns:
            List of suggested labels
        """
        try:
            issue = self.github_api.get_issue(issue_number)
            classification = self.classifier.classify_issue(issue)
            suggested_labels = classification['suggested_labels']
            
            print(f"\nSuggested labels for issue #{issue_number}:")
            for label in suggested_labels:
                print(f"  • {label}")
            
            if apply_labels:
                print("\nApplying labels...")
                success = self.github_api.add_labels_to_issue(issue_number, suggested_labels)
                if success:
                    print("Labels applied successfully!")
                else:
                    print("Failed to apply labels.")
            
            return suggested_labels
            
        except Exception as e:
            print(f"Error suggesting labels: {str(e)}")
            return []


def main():
    """
    Main function to demonstrate the GitHub Issue Assistant.
    """
    print("="*60)
    print("GITHUB ISSUE ASSISTANT")
    print("="*60)
    
    # Check for environment variables
    if not os.getenv('GITHUB_TOKEN'):
        print("\nError: GITHUB_TOKEN not set in environment variables.")
        print("Please create a .env file with your GitHub token.")
        print("\nExample .env file:")
        print("GITHUB_TOKEN=your_token_here")
        print("GITHUB_REPO_OWNER=owner_name")
        print("GITHUB_REPO_NAME=repo_name")
        return
    
    try:
        # Initialize assistant
        assistant = GitHubIssueAssistant()
        
        print("\nGitHub Issue Assistant initialized successfully!")
        print("\nAvailable commands:")
        print("1. Analyze a specific issue")
        print("2. Analyze all open issues")
        print("3. Suggest labels for an issue")
        print("4. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                issue_num = input("Enter issue number: ").strip()
                if issue_num.isdigit():
                    assistant.analyze_issue(int(issue_num))
                else:
                    print("Invalid issue number.")
            
            elif choice == '2':
                state = input("Enter state (open/closed/all) [open]: ").strip() or 'open'
                max_issues = input("Enter max issues to analyze [50]: ").strip() or '50'
                assistant.analyze_all_issues(state=state, max_issues=int(max_issues))
            
            elif choice == '3':
                issue_num = input("Enter issue number: ").strip()
                if issue_num.isdigit():
                    apply = input("Apply labels automatically? (y/n) [n]: ").strip().lower() == 'y'
                    assistant.suggest_labels_for_issue(int(issue_num), apply_labels=apply)
                else:
                    print("Invalid issue number.")
            
            elif choice == '4':
                print("\nThank you for using GitHub Issue Assistant!")
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nPlease ensure your .env file is properly configured.")


if __name__ == '__main__':
    main()
