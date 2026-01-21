from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import re
from dotenv import load_dotenv
from src.github_api import GitHubAPI
from src.llm_analyzer import LLMAnalyzer

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for API requests

# Initialize LLM analyzer
try:
    llm_analyzer = LLMAnalyzer()
    print("✅ LLM Analyzer initialized successfully")
except ValueError as e:
    print(f"⚠️  Warning: {e}")
    print("   The app will not work without a valid Gemini API key.")
    llm_analyzer = None


def parse_github_url(url):
    """
    Extract owner and repo from GitHub URL.
    Supports formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo/
    - https://github.com/owner/repo/issues/123
    """
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, url)
    
    if match:
        owner = match.group(1)
        # Remove trailing slash and anything after (like /issues/123)
        repo = match.group(2).split('/')[0].rstrip('/')
        return owner, repo
    return None, None


@app.route('/')
def index():
    """Serve the main UI."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_issue():
    """
    API endpoint to analyze a GitHub issue using LLM.
    
    Expected JSON payload:
    {
        "repo_url": "https://github.com/owner/repo",
        "issue_number": 123
    }
    
    Returns the required JSON format.
    """
    try:
        # Check if LLM analyzer is available
        if llm_analyzer is None:
            return jsonify({
                'error': 'LLM analyzer not configured. Please set GEMINI_API_KEY environment variable. '
                        'Get your free API key at: https://makersuite.google.com/app/apikey'
            }), 503
        
        data = request.json
        repo_url = data.get('repo_url', '').strip()
        issue_number = data.get('issue_number')
        
        # Validation
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        if not issue_number:
            return jsonify({'error': 'Issue number is required'}), 400
        
        try:
            issue_number = int(issue_number)
        except ValueError:
            return jsonify({'error': 'Issue number must be a valid integer'}), 400
        
        # Parse GitHub URL
        owner, repo = parse_github_url(repo_url)
        if not owner or not repo:
            return jsonify({'error': 'Invalid GitHub URL format. Expected: https://github.com/owner/repo'}), 400
        
        # Get GitHub token (optional for public repos)
        token = os.getenv('GITHUB_TOKEN')
        
        # Initialize GitHub API (works without token for public repos)
        api = GitHubAPI(token=token, owner=owner, repo=repo)
        
        # Fetch issue
        issue = api.get_issue(issue_number)
        
        if not issue:
            return jsonify({'error': f'Issue #{issue_number} not found in {owner}/{repo}'}), 404
        
        # Fetch comments for the issue
        try:
            comments = api.get_issue_comments(issue_number)
            issue['comments_list'] = comments
        except Exception:
            # If comments fail, continue without them
            issue['comments_list'] = []
        
        # Analyze using LLM
        analysis = llm_analyzer.analyze_issue(issue)
        
        # Validate analysis result
        if not analysis or not isinstance(analysis, dict):
            return jsonify({
                'error': 'Analysis returned invalid result. Please try again.'
            }), 500
        
        # Ensure required fields exist
        required_fields = ['summary', 'type', 'priority_score', 'suggested_labels']
        missing_fields = [field for field in required_fields if field not in analysis]
        
        if missing_fields:
            return jsonify({
                'error': f'Analysis incomplete. Missing fields: {", ".join(missing_fields)}'
            }), 500
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'GitHub Issue Assistant API',
        'version': '1.0.0'
    }), 200


if __name__ == '__main__':
    # Run Flask development server
    # Note: Messages appear twice due to Flask's reloader spawning a child process
    # This is normal behavior in debug mode
    print("🚀 Starting GitHub Issue Assistant API...")
    print("📍 Server running at: http://localhost:5000")
    print("🔍 Open your browser and navigate to the URL above")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)