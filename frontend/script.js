// Technical SEO Audit Tool - JavaScript

const API_URL = 'http://localhost:8000';
let currentAuditId = null;
let pollInterval = null;

function setUrl(url) {
    document.getElementById('urlInput').value = url;
}

async function startAudit() {
    const url = document.getElementById('urlInput').value.trim();
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }

    // Validate URL format
    try {
        new URL(url);
    } catch (e) {
        alert('Please enter a valid URL (must include http:// or https://)');
        return;
    }

    // Reset UI
    document.getElementById('results').classList.remove('active');
    document.getElementById('error').style.display = 'none';
    document.getElementById('loading').classList.add('active');
    document.getElementById('startAudit').disabled = true;

    try {
        // Start audit
        const response = await fetch(`${API_URL}/audit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            throw new Error('Failed to start audit');
        }

        const data = await response.json();
        currentAuditId = data.audit_id;

        // Poll for results
        pollForResults();

    } catch (error) {
        showError('Failed to start audit: ' + error.message);
        document.getElementById('loading').classList.remove('active');
        document.getElementById('startAudit').disabled = false;
    }
}

async function pollForResults() {
    if (!currentAuditId) return;

    try {
        const response = await fetch(`${API_URL}/audit/${currentAuditId}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch results');
        }

        const audit = await response.json();

        if (audit.status === 'completed' && audit.results) {
            // Show results
            clearInterval(pollInterval);
            displayResults(audit.results);
            document.getElementById('loading').classList.remove('active');
            document.getElementById('startAudit').disabled = false;
        } else if (audit.status === 'failed') {
            clearInterval(pollInterval);
            showError('Audit failed: ' + (audit.error || 'Unknown error'));
            document.getElementById('loading').classList.remove('active');
            document.getElementById('startAudit').disabled = false;
        } else {
            // Keep polling
            pollInterval = setTimeout(pollForResults, 2000);
        }

    } catch (error) {
        clearInterval(pollInterval);
        showError('Failed to fetch results: ' + error.message);
        document.getElementById('loading').classList.remove('active');
        document.getElementById('startAudit').disabled = false;
    }
}

function displayResults(results) {
    document.getElementById('results').classList.add('active');
    document.getElementById('auditUrl').textContent = `URL: ${results.url}`;
    document.getElementById('pageCount').textContent = results.pages_crawled;

    // Display summary
    const summaryHtml = `
        <div class="summary-card">
            <div class="summary-label">Pages Crawled</div>
            <div class="summary-value">${results.pages_crawled}</div>
        </div>
        <div class="summary-card ${results.summary.missing_title > 0 ? 'error' : ''}">
            <div class="summary-label">Missing Title</div>
            <div class="summary-value">${results.summary.missing_title}</div>
        </div>
        <div class="summary-card ${results.summary.missing_meta_description > 0 ? 'warning' : ''}">
            <div class="summary-label">Missing Meta Desc</div>
            <div class="summary-value">${results.summary.missing_meta_description}</div>
        </div>
        <div class="summary-card ${results.summary.multiple_h1 > 0 ? 'warning' : ''}">
            <div class="summary-label">Multiple H1</div>
            <div class="summary-value">${results.summary.multiple_h1}</div>
        </div>
        <div class="summary-card ${results.summary.noindex_pages > 0 ? 'warning' : ''}">
            <div class="summary-label">Noindex Pages</div>
            <div class="summary-value">${results.summary.noindex_pages}</div>
        </div>
        <div class="summary-card ${results.summary.non_200_pages > 0 ? 'error' : ''}">
            <div class="summary-label">Non-200 Pages</div>
            <div class="summary-value">${results.summary.non_200_pages}</div>
        </div>
    `;
    document.getElementById('summary').innerHTML = summaryHtml;

    // Display pages
    const pagesHtml = results.pages.map((page, index) => `
        <div class="page-item">
            <div class="page-header" onclick="togglePageDetails(${index})">
                <span class="page-url">${page.url}</span>
                <span class="status-badge ${page.status_code === 200 ? 'status-success' : 'status-error'}">
                    ${page.status_code}
                </span>
                ${page.issues && page.issues.length > 0 ? `<span class="issues-count">${page.issues.length} issues</span>` : ''}
            </div>
            <div class="page-details" id="details-${index}">
                <div class="detail-row">
                    <div class="detail-label">Title</div>
                    <div class="detail-value">${page.title || '(missing)'} ${page.title_length ? `(${page.title_length} chars)` : ''}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Meta Description</div>
                    <div class="detail-value">${page.meta_description || '(missing)'} ${page.meta_description_length ? `(${page.meta_description_length} chars)` : ''}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">H1 Count</div>
                    <div class="detail-value">${page.h1_count}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Canonical</div>
                    <div class="detail-value">${page.canonical_present ? ' Present' : ' Missing'}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Noindex</div>
                    <div class="detail-value">${page.noindex ? ' Yes' : 'No'}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Page Size</div>
                    <div class="detail-value">${page.page_size_kb} KB</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Internal Links</div>
                    <div class="detail-value">${page.internal_links}</div>
                </div>
                ${page.issues && page.issues.length > 0 ? `
                    <div class="issues-list">
                        <strong>Issues Detected:</strong>
                        ${page.issues.map(issue => `<div class="issue-item">${issue.replace(/_/g, ' ')}</div>`).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
    document.getElementById('pagesList').innerHTML = pagesHtml;
}

function togglePageDetails(index) {
    const details = document.getElementById(`details-${index}`);
    details.classList.toggle('active');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Handle Enter key in input
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('urlInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            startAudit();
        }
    });
});
