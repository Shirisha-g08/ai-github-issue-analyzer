"""
LLM Service for analyzing GitHub issues using Hugging Face models.
This module handles all AI-powered analysis using a Large Language Model.
"""

import os
import json
import requests
from typing import Dict, Optional


class LLMAnalyzer:
    """
    Handles LLM-based analysis of GitHub issues using Hugging Face Inference API.
    Uses free tier - no API key required!
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM analyzer.
        Uses Hugging Face's free inference API with multiple model fallbacks.
        """
        # Hugging Face Inference API endpoint (free tier)
        # Updated to use newer, available models
        self.api_urls = [
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
            "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
            "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct",
        ]
        self.api_url = self.api_urls[0]  # Start with first model
        
        # Optional: Use HF token for faster inference (but works without it)
        self.hf_token = api_key or os.getenv('HF_TOKEN')
        
        self.headers = {}
        if self.hf_token:
            self.headers["Authorization"] = f"Bearer {self.hf_token}"
    
    def analyze_issue(self, issue: Dict) -> Dict:
        """
        Analyze a GitHub issue using LLM and return structured insights.
        
        Args:
            issue: Dictionary containing issue details (title, body, comments, etc.)
        
        Returns:
            Dictionary with analysis results in the required format.
            Always returns a valid dictionary, uses fallback if LLM fails.
        """
        # Validate input
        if not issue or not isinstance(issue, dict):
            print("⚠️ Invalid issue data, using fallback")
            return self._get_default_analysis()
        
        # Prepare the issue context
        try:
            issue_context = self._prepare_issue_context(issue)
        except Exception as e:
            print(f"⚠️ Error preparing context: {e}, using fallback")
            return self._fallback_analysis(issue)
        
        # Create the prompt
        prompt = self._create_analysis_prompt(issue_context)
        
        # Generate analysis using Hugging Face Inference API with fallback models
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 800,  # Increased for more detailed summaries
                    "temperature": 0.5,      # Lower for more consistent, focused output
                    "return_full_text": False,
                    "top_p": 0.9
                }
            }
            
            # Try each model endpoint until one works
            last_error = None
            for model_url in self.api_urls:
                try:
                    response = requests.post(
                        model_url,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                        else:
                            generated_text = str(result)
                        print(f"✅ LLM response received from {model_url.split('/')[-1]} ({len(generated_text)} chars)")
                        
                        # Parse the JSON response
                        analysis = self._parse_llm_response(generated_text)
                        return analysis
                    elif response.status_code == 503:
                        # Model is loading, try next one
                        print(f"⚠️ Model loading ({model_url.split('/')[-1]}), trying next...")
                        last_error = f"Model loading (503)"
                        continue
                    elif response.status_code == 410:
                        # Model deprecated, try next one
                        print(f"⚠️ Model deprecated ({model_url.split('/')[-1]}), trying next...")
                        last_error = f"Model deprecated (410)"
                        continue
                    else:
                        print(f"⚠️ LLM API returned status {response.status_code} for {model_url.split('/')[-1]}, trying next...")
                        last_error = f"HTTP {response.status_code}"
                        continue
                except requests.exceptions.RequestException as req_err:
                    print(f"⚠️ Request failed for {model_url.split('/')[-1]}: {req_err}, trying next...")
                    last_error = str(req_err)
                    continue
            
            # All models failed, use fallback
            print(f"❌ All LLM models failed (last error: {last_error}), using rule-based fallback")
            return self._fallback_analysis(issue)
            
        except Exception as e:
            # If LLM fails, use fallback rule-based analysis
            print(f"LLM failed, using fallback: {e}")
        except Exception as e:
            # If LLM fails, use fallback rule-based analysis
            print(f"❌ Unexpected error in LLM analysis: {e}, using fallback")
            return self._fallback_analysis(issue)
    
    def _prepare_issue_context(self, issue: Dict) -> str:
        """
        Prepare the issue context for the LLM.
        Handles edge cases like missing comments or very long bodies.
        """
        title = issue.get('title', 'No title')
        body = issue.get('body', 'No description provided')
        state = issue.get('state', 'unknown')
        
        # Handle labels - they are already strings from GitHub API
        labels = issue.get('labels', [])
        if labels and isinstance(labels[0], dict):
            # If labels are dicts, extract names
            labels = [label.get('name', '') for label in labels]
        
        comments_list = issue.get('comments_list', [])
        
        # Truncate body if too long (keep first 4000 chars for more context)
        if body and len(body) > 4000:
            body = body[:4000] + "\n\n... [truncated for length]"
        
        # Build context
        context = f"""
Issue Title: {title}

Issue State: {state}

Issue Body:
{body}

Existing Labels: {', '.join(labels) if labels else 'None'}
"""
        
        # Add comments if available
        if comments_list:
            # Limit to first 5 comments to avoid token limits
            comments_preview = comments_list[:5]
            comments_text = "\n".join([
                f"Comment {i+1} by {c.get('user', 'unknown')}: {c.get('body', '')[:300]}"
                for i, c in enumerate(comments_preview)
            ])
            context += f"\nComments ({len(comments_list)} total, showing first {len(comments_preview)}):\n{comments_text}"
        else:
            context += "\nComments: No comments yet."
        
        return context
    
    def _create_analysis_prompt(self, issue_context: str) -> str:
        """
        Create a well-engineered prompt for the LLM.
        Uses few-shot prompting for better results.
        """
        prompt = f"""You are an expert software engineer analyzing GitHub issues. Your task is to analyze the following GitHub issue and provide a structured analysis.

{issue_context}

CRITICAL INSTRUCTIONS FOR SUMMARY:
1. DO NOT just repeat or rephrase the title
2. READ the issue body and comments carefully
3. EXPLAIN what the user is experiencing, what they tried, and what they need
4. Write 2-4 complete sentences in PLAIN TEXT (no HTML, no markdown, no special formatting)
5. Provide context that someone unfamiliar with the issue would understand

Analyze this issue and provide your response in the following JSON format:

{{
  "summary": "Write a detailed explanation here. Start by describing the problem or request in your own words based on the issue body, not just the title. Include relevant details about what causes it, how it affects users, and what outcome is desired. Use plain text only.",
  "type": "Classify as one of: bug, feature_request, documentation, question, or other",
  "priority_score": "A score from 1 (low) to 5 (critical) with justification",
  "suggested_labels": ["Array of 2-3 relevant labels"],
  "potential_impact": "Brief description of user impact (especially for bugs)"
}}

Classification Guidelines:
- bug: Something is broken, not working as expected, error messages, crashes
- feature_request: New functionality, enhancement, improvement request
- documentation: Docs are missing, unclear, or need updates
- question: User asking how to do something, seeking clarification
- other: Doesn't fit other categories

Priority Scoring:
- 5 (critical): Security issues, data loss, complete feature breakdown, affects many users
- 4 (high): Major functionality broken, significant user impact, performance issues
- 3 (medium): Minor bugs, moderate impact, workarounds available
- 2 (low): Small issues, cosmetic problems, nice-to-have features
- 1 (very low): Trivial issues, minor enhancements

Example outputs:

Example 1 - Bug:
{{
  "summary": "The application encounters a fatal error when users try to upload files exceeding 10MB in size. According to the issue description, the error occurs specifically during the file validation step, before the actual upload begins. Users report losing their file selection and having to restart the entire upload process. This is particularly problematic for users working with large media files, presentations, or datasets who depend on this functionality for their daily work.",
  "type": "bug",
  "priority_score": "4/5 - High priority: Critical functionality failure affecting file uploads, negative user experience",
  "suggested_labels": ["bug", "file-upload", "priority:high"],
  "potential_impact": "Users cannot upload larger files, blocking a core feature for users with substantial data needs"
}}

Example 2 - Feature Request:
{{
  "summary": "The user is requesting the addition of a dark mode theme option for the application interface. They explain that prolonged use of the current light theme causes significant eye strain, especially when working late at night or in low-light environments. The user notes that this feature has become a standard expectation in modern applications and would greatly benefit users with light sensitivity or those who prefer reduced screen brightness during extended work sessions.",
  "type": "feature_request",
  "priority_score": "3/5 - Medium priority: Enhances user experience and accessibility, commonly requested feature",
  "suggested_labels": ["enhancement", "UI", "accessibility"],
  "potential_impact": "Not a bug - this is a feature request that would improve user experience"
}}

REMEMBER: 
- Summary must be explanatory and detailed, NOT just a restatement of the title
- Use information from the issue body and comments
- Write in plain text without HTML tags or special formatting
- Make it understandable to someone who hasn't read the issue

Now analyze the issue above and respond with ONLY the JSON object, no additional text:"""
        
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """
        Parse the LLM response and extract the JSON.
        Handles cases where LLM adds extra text around the JSON.
        """
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in LLM response")
            
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['summary', 'type', 'priority_score', 'suggested_labels']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Strip HTML tags from text fields
            result['summary'] = self._strip_html_tags(result.get('summary', ''))
            result['priority_score'] = self._strip_html_tags(result.get('priority_score', ''))
            result['type'] = self._strip_html_tags(result.get('type', ''))
            if result.get('potential_impact'):
                result['potential_impact'] = self._strip_html_tags(result['potential_impact'])
            
            # Ensure suggested_labels is a list and strip HTML from labels
            if not isinstance(result['suggested_labels'], list):
                result['suggested_labels'] = [str(result['suggested_labels'])]
            
            result['suggested_labels'] = [self._strip_html_tags(label) for label in result['suggested_labels']]
            
            # Limit to 3 labels as per requirements
            result['suggested_labels'] = result['suggested_labels'][:3]
            
            # Ensure potential_impact exists (None for non-bugs is okay)
            if 'potential_impact' not in result:
                if result['type'] == 'bug':
                    result['potential_impact'] = "Impact assessment needed"
                else:
                    result['potential_impact'] = None
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error processing LLM response: {e}")
    
    def _strip_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from text to ensure clean plain text output.
        
        Args:
            text: Text that may contain HTML tags
            
        Returns:
            Plain text with HTML tags removed
        """
        import re
        if not text:
            return text
        
        # Remove all HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Also handle common HTML entities
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&#39;', "'")
        clean_text = clean_text.replace('&nbsp;', ' ')
        
        return clean_text.strip()
    
    def _get_default_analysis(self) -> Dict:
        """
        Return a default analysis when input is invalid or missing.
        Ensures we always return a valid response structure.
        
        Returns:
            Dictionary with default analysis values
        """
        return {
            "summary": "Unable to analyze issue. The issue data provided was invalid or incomplete.",
            "type": "other",
            "priority_score": "3/5 - Medium priority: Unable to assess, requires manual review",
            "suggested_labels": ["needs-triage", "manual-review"],
            "potential_impact": "Impact assessment not available due to insufficient data."
        }
    
    def _fallback_analysis(self, issue: Dict) -> Dict:
        """
        Fallback rule-based analysis when LLM is unavailable.
        Uses keyword matching and heuristics.
        Ensures valid output even with minimal input data.
        """
        # Validate issue input
        if not issue or not isinstance(issue, dict):
            return self._get_default_analysis()
        
        # Strip HTML tags from input with error handling
        try:
            title = self._strip_html_tags(issue.get('title', '')).lower()
            body = self._strip_html_tags(issue.get('body', '')).lower()
        except Exception:
            title = str(issue.get('title', '')).lower()
            body = str(issue.get('body', '')).lower()
        
        text = f"{title} {body}"
        
        # If no content, return default
        if not text.strip():
            result = self._get_default_analysis()
            result['summary'] = "Issue has no title or description provided."
            return result
        
        # Determine type
        if any(word in text for word in ['bug', 'error', 'crash', 'fail', 'broken', 'issue', 'problem']):
            issue_type = 'bug'
        elif any(word in text for word in ['feature', 'enhancement', 'add', 'support', 'implement']):
            issue_type = 'feature_request'
        elif any(word in text for word in ['doc', 'documentation', 'readme', 'guide', 'tutorial']):
            issue_type = 'documentation'
        elif any(word in text for word in ['how', 'what', 'why', 'question', '?']):
            issue_type = 'question'
        else:
            issue_type = 'other'
        
        # Determine priority
        if any(word in text for word in ['critical', 'urgent', 'security', 'data loss', 'crash']):
            priority = 5
            justification = "Critical issue: security, stability, or data integrity concerns"
        elif any(word in text for word in ['important', 'major', 'severe', 'blocking']):
            priority = 4
            justification = "High priority: significant impact on functionality"
        elif any(word in text for word in ['minor', 'small', 'trivial']):
            priority = 2
            justification = "Low priority: minor issue with limited impact"
        else:
            priority = 3
            justification = "Medium priority: moderate impact, should be addressed"
        
        # Generate comprehensive summary from title and body
        summary_parts = []
        
        # Start with title (use original case but strip HTML)
        if title:
            title_clean = self._strip_html_tags(issue.get('title', '')).strip()
            if title_clean:
                # Capitalize and ensure proper sentence
                if not title_clean[0].isupper():
                    title_clean = title_clean[0].upper() + title_clean[1:]
                if not title_clean.endswith('.'):
                    title_clean = title_clean + '.'
                summary_parts.append(title_clean)
        
        # Add context from body (first 1-2 sentences) - strip HTML
        body_text = self._strip_html_tags(issue.get('body', ''))
        if body_text and len(body_text) > 20:
            # Extract first meaningful sentence from body
            sentences = body_text.split('.')[:2]
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 15 and not sent.startswith('#'):  # Skip headers
                    if not sent[0].isupper() if sent else False:
                        sent = sent[0].upper() + sent[1:] if sent else sent
                    if not sent.endswith('.'):
                        sent = sent + '.'
                    summary_parts.append(sent)
                    break
        
        # Combine parts
        if summary_parts:
            summary = ' '.join(summary_parts[:3])  # Max 3 sentences
            summary = summary[:500]  # Reasonable length limit
        else:
            summary = "Issue requires attention and further investigation."
        
        # Suggest labels (2-3 labels as required)
        labels = [issue_type.replace('_', '-')]
        if priority >= 4:
            labels.append('priority:high')
        elif priority <= 2:
            labels.append('priority:low')
        else:
            labels.append('priority:medium')
        
        # Add contextual label based on keywords
        if 'ui' in text or 'interface' in text:
            labels.append('UI')
        elif 'api' in text:
            labels.append('API')
        elif 'performance' in text:
            labels.append('performance')
        elif 'security' in text:
            labels.append('security')
        
        # Ensure exactly 2-3 labels
        labels = labels[:3]
        if len(labels) < 2:
            labels.append('needs-triage')
        
        # Potential impact (only for bugs as per requirement)
        if issue_type == 'bug':
            if priority >= 4:
                impact = "This bug may significantly impact user experience and could affect core functionality."
            elif priority >= 3:
                impact = "This bug may cause inconvenience to users but does not block critical workflows."
            else:
                impact = "This bug has minimal impact on most users and represents a minor issue."
        else:
            impact = "Not a bug - impact assessment not applicable."
        
        # Strip HTML from all text fields before returning
        return {
            "summary": self._strip_html_tags(summary),
            "type": issue_type,
            "priority_score": self._strip_html_tags(f"{priority}/5 - {justification}"),
            "suggested_labels": [self._strip_html_tags(label) for label in labels[:3]],
            "potential_impact": self._strip_html_tags(impact)
        }
