document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const outputSection = document.getElementById('outputSection');
    const errorSection = document.getElementById('errorSection');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorMessage = document.getElementById('errorMessage');

    // Store current repo info globally
    let currentRepoUrl = '';
    let currentIssueNumber = '';

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get input values
        const repoUrl = document.getElementById('repoUrl').value.trim();
        const issueNumber = document.getElementById('issueNumber').value.trim();
        
        // Store for GitHub link
        currentRepoUrl = repoUrl;
        currentIssueNumber = issueNumber;

        // Hide previous results/errors
        outputSection.style.display = 'none';
        errorSection.style.display = 'none';

        // Show loading state
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('loading');

        try {
            // Make API request
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    repo_url: repoUrl,
                    issue_number: parseInt(issueNumber)
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            // Validate response data
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response from server');
            }

            if (!data.summary || !data.type || !data.priority_score) {
                throw new Error('Incomplete analysis result. Missing required fields.');
            }

            // Display results
            displayResults(data);
            outputSection.style.display = 'block';

        } catch (error) {
            // Display error
            errorMessage.textContent = `❌ Error: ${error.message}`;
            errorSection.style.display = 'block';
        } finally {
            // Reset button state
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('loading');
        }
    });

    function displayResults(data) {
        let html = '';
        
        // GitHub Issue Link Header
        const issueUrl = `${currentRepoUrl}/issues/${currentIssueNumber}`;
        html += `
            <div class="issue-header">
                <h3>Analysis Complete</h3>
                <a href="${issueUrl}" target="_blank" class="view-issue-btn" title="View original issue on GitHub">
                    🔗 View Original Issue on GitHub
                </a>
            </div>
        `;

        // Summary (multi-line support)
        html += `
            <div class="result-item">
                <div class="result-label">
                    📝 Summary
                    <span class="tooltip" data-tooltip="AI-generated summary of the issue's main problem or request">
                        ℹ️
                    </span>
                </div>
                <div class="result-value summary-text">${escapeHtml(data.summary)}</div>
            </div>
        `;

        // Type
        html += `
            <div class="result-item">
                <div class="result-label">
                    🏷️ Type
                    <span class="tooltip" data-tooltip="Classification: bug, feature_request, documentation, question, or other">
                        ℹ️
                    </span>
                </div>
                <div class="result-value">
                    <span class="type-badge type-${data.type}">${formatType(data.type)}</span>
                </div>
            </div>
        `;

        // Priority Score
        html += `
            <div class="result-item">
                <div class="result-label">
                    ⚡ Priority Score
                    <span class="tooltip" data-tooltip="AI-assigned priority from 1 (low) to 5 (critical) with justification">
                        ℹ️
                    </span>
                </div>
                <div class="result-value priority-score">${escapeHtml(data.priority_score)}</div>
            </div>
        `;

        // Suggested Labels
        if (data.suggested_labels && data.suggested_labels.length > 0) {
            html += `
                <div class="result-item">
                    <div class="result-label">
                        🔖 Suggested Labels
                        <span class="tooltip" data-tooltip="AI-recommended labels for better issue organization">
                            ℹ️
                        </span>
                    </div>
                    <div class="result-value">
                        <div class="labels-container">
                            ${data.suggested_labels.map(label => 
                                `<span class="label-badge">${escapeHtml(label)}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        // Potential Impact
        if (data.potential_impact) {
            html += `
                <div class="result-item">
                    <div class="result-label">
                        💥 Potential Impact
                        <span class="tooltip" data-tooltip="Analysis of how this issue might affect users or the system">
                            ℹ️
                        </span>
                    </div>
                    <div class="result-value">
                        <div class="impact-text">${escapeHtml(data.potential_impact)}</div>
                    </div>
                </div>
            `;
        }

        // Raw JSON Output
        html += `
            <div class="result-item">
                <div class="result-label">
                    📄 Raw JSON Output
                    <span class="tooltip" data-tooltip="Complete structured response in JSON format - ready to copy for API integration">
                        ℹ️
                    </span>
                </div>
                <div class="result-value">
                    <div style="position: relative;">
                        <button onclick="copyJSON()" class="copy-json-btn" title="Copy JSON to clipboard">📋 Copy JSON</button>
                        <pre class="json-output" id="jsonOutput">${JSON.stringify(data, null, 2)}</pre>
                    </div>
                </div>
            </div>
        `;

        resultsContainer.innerHTML = html;
    }

    // Make copyJSON available globally
    window.copyJSON = function() {
        const jsonText = document.getElementById('jsonOutput').textContent;
        navigator.clipboard.writeText(jsonText).then(() => {
            const btn = document.querySelector('.copy-json-btn');
            const originalText = btn.textContent;
            btn.textContent = '✅ Copied!';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 2000);
        });
    };

    function formatType(type) {
        const typeMap = {
            'bug': 'Bug',
            'feature_request': 'Feature Request',
            'documentation': 'Documentation',
            'question': 'Question',
            'other': 'Other'
        };
        return typeMap[type] || type;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Add example button functionality
    const exampleRepos = [
        { url: 'https://github.com/facebook/react', issue: 100 },
        { url: 'https://github.com/microsoft/vscode', issue: 1000 },
        { url: 'https://github.com/python/cpython', issue: 50000 }
    ];

    // You could add example buttons if desired
});
