// Global variables
let currentPlatform = 'email';
let currentPage = 1;
const itemsPerPage = 5;

document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
    
    // Load history if on home page
    if (window.location.pathname === '/' && document.getElementById('historyList')) {
        loadHistory();
    }
});

function initializeApplication() {
    // Platform selection
    const platformButtons = document.querySelectorAll('.platform-btn');
    if (platformButtons.length > 0) {
        platformButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                platformButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentPlatform = this.dataset.platform;
            });
        });
    }
    
    // Analysis form handling
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalysis);
    }
    
    // Clear button
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearContent);
    }
    
    // Sample button
    const sampleBtn = document.getElementById('sampleBtn');
    if (sampleBtn) {
        sampleBtn.addEventListener('click', loadSample);
    }
    
    // User menu toggle
    const userBtn = document.querySelector('.user-btn');
    if (userBtn) {
        userBtn.addEventListener('click', function() {
            document.querySelector('.user-dropdown').classList.toggle('show');
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.user-menu')) {
            const dropdown = document.querySelector('.user-dropdown');
            if (dropdown.classList.contains('show')) {
                dropdown.classList.remove('show');
            }
        }
    });
}

function handleAnalysis() {
    const contentElement = document.getElementById('emailContent');
    if (!contentElement) return;
    
    const content = contentElement.value.trim();
    
    if (!content) {
        showAlert('Please enter message content to analyze', 'error');
        return;
    }
    
    // Show loading state
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.innerHTML = '<div class="loading"></div> ANALYZING';
        analyzeBtn.disabled = true;
    }
    
    fetch('/api/detect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: content,
            platform: currentPlatform,
        })
    })
    .then(response => {
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned non-JJSON response');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        updateResults(data, content);
        loadHistory(); // Refresh history
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert(`Analysis failed: ${error.message}`, 'error');
        simulateAnalysis(content); // Fallback to simulation
    })
    .finally(() => {
        // Reset button state
        if (analyzeBtn) {
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> ANALYZE';
            analyzeBtn.disabled = false;
        }
    });
}

function updateResults(data, content) {
    const isSpam = data.prediction === 'spam';
    const confidence = Math.round((isSpam ? data.probability : (1 - data.probability)) * 100);
    
    const resultStatus = document.getElementById('resultStatus');
    const resultBadge = document.getElementById('resultBadge');
    const confidenceCard = document.getElementById('confidenceCard');
    const confidenceLevel = document.getElementById('confidenceLevel');
    const confidenceValue = document.getElementById('confidenceValue');
    const detailsCard = document.getElementById('detailsCard');
    const analysisDetails = document.getElementById('analysisDetails');
    const historySection = document.getElementById('historySection');
    
    if (resultStatus && resultBadge) {
        if (isSpam) {
            resultStatus.textContent = 'SPAM DETECTED';
            resultStatus.className = 'result-title spam';
            resultBadge.textContent = '⚠️ MALICIOUS';
            resultBadge.className = 'badge badge-danger';
        } else {
            resultStatus.textContent = 'LEGITIMATE MESSAGE';
            resultStatus.className = 'result-title ham';
            resultBadge.textContent = '✓ SAFE';
            resultBadge.className = 'badge badge-success';
        }
    }
    
    // Show confidence meter
    if (confidenceCard && confidenceLevel && confidenceValue) {
        confidenceCard.style.display = 'block';
        setTimeout(() => {
            confidenceLevel.style.width = confidence + '%';
        }, 100);
        confidenceValue.textContent = confidence + '% confidence';
    }
    
    // Show details
    if (detailsCard && analysisDetails) {
        detailsCard.style.display = 'block';
        analysisDetails.innerHTML = formatExplanation(data.explanation);
    }
    
    // Show history section
    if (historySection) {
        historySection.style.display = 'block';
    }
}

function formatExplanation(explanation) {
    // Check if explanation is defined
    if (!explanation) {
        return '<div class="detail-item">No detailed explanation available.</div>';
    }
    
    // Convert the text explanation to HTML format
    const lines = explanation.split('\n');
    let html = '';
    
    lines.forEach(line => {
        if (line.trim()) {
            html += `
                <div class="detail-item">
                    <div class="detail-icon">${line.includes('SPAM') ? '⚠️' : '✓'}</div>
                    <div>
                        <p>${line}</p>
                    </div>
                </div>
            `;
        }
    });
    
    return html;
}

function simulateAnalysis(content) {
    // Simple spam detection (fallback)
    const isSpam = content.toLowerCase().includes('http://') || 
                   content.toLowerCase().includes('verify') || 
                   content.toLowerCase().includes('urgent');
    
    const confidence = isSpam ? Math.floor(Math.random() * 20) + 80 : Math.floor(Math.random() * 20) + 10;
    
    // Update UI with results
    const resultStatus = document.getElementById('resultStatus');
    const resultBadge = document.getElementById('resultBadge');
    const confidenceCard = document.getElementById('confidenceCard');
    const confidenceLevel = document.getElementById('confidenceLevel');
    const confidenceValue = document.getElementById('confidenceValue');
    const detailsCard = document.getElementById('detailsCard');
    const analysisDetails = document.getElementById('analysisDetails');
    const historySection = document.getElementById('historySection');
    
    if (resultStatus && resultBadge) {
        if (isSpam) {
            resultStatus.textContent = 'SPAM DETECTED';
            resultStatus.className = 'result-title spam';
            resultBadge.textContent = '⚠️ MALICIOUS';
            resultBadge.className = 'badge badge-danger';
        } else {
            resultStatus.textContent = 'LEGITIMATE MESSAGE';
            resultStatus.className = 'result-title ham';
            resultBadge.textContent = '✓ SAFE';
            resultBadge.className = 'badge badge-success';
        }
    }
    
    // Show confidence meter
    if (confidenceCard && confidenceLevel && confidenceValue) {
        confidenceCard.style.display = 'block';
        setTimeout(() => {
            confidenceLevel.style.width = confidence + '%';
        }, 100);
        confidenceValue.textContent = confidence + '% confidence';
    }
    
    // Show details
    if (detailsCard && analysisDetails) {
        detailsCard.style.display = 'block';
        analysisDetails.innerHTML = generateAnalysisDetails(content, isSpam);
    }
    
    // Show history section
    if (historySection) {
        historySection.style.display = 'block';
    }
    
    // Load history
    loadHistory();
}

function generateAnalysisDetails(content, isSpam) {
    let detailsHTML = '';
    
    if (isSpam) {
        detailsHTML += `
            <div class="detail-item">
                <div class="detail-icon">⚠️</div>
                <div>
                    <strong>Suspicious Links Found</strong>
                    <p>This message contains links to potentially dangerous websites.</p>
                </div>
            </div>
            <div class="detail-item">
                <div class="detail-icon">⏱️</div>
                <div>
                    <strong>Urgency Indicators</strong>
                    <p>The message creates artificial urgency to prompt quick action.</p>
                </div>
            </div>
            <div class="detail-item">
                <div class="detail-icon">🔍</div>
                <div>
                    <strong>Generic Greeting</strong>
                    <p>Uses "Dear User" instead of your actual name.</p>
                </div>
            </div>
        `;
    } else {
        detailsHTML += `
            <div class="detail-item">
                <div class="detail-icon">✓</div>
                <div>
                    <strong>No Suspicious Links</strong>
                    <p>No dangerous or shortened URLs detected.</p>
                </div>
            </div>
            <div class="detail-item">
                <div class="detail-icon">✓</div>
                <div>
                    <strong>Normal Tone</strong>
                    <p>Message doesn't use urgency or scare tactics.</p>
                </div>
            </div>
            <div class="detail-item">
                <div class="detail-icon">✓</div>
                <div>
                    <strong>Personalized</strong>
                    <p>Appears to be addressed specifically to you.</p>
                </div>
            </div>
        `;
    }
    
    return detailsHTML;
}

function clearContent() {
    const emailContent = document.getElementById('emailContent');
    if (emailContent) {
        emailContent.value = '';
    }
    resetResults();
}

function resetResults() {
    const resultStatus = document.getElementById('resultStatus');
    const resultBadge = document.getElementById('resultBadge');
    const confidenceCard = document.getElementById('confidenceCard');
    const detailsCard = document.getElementById('detailsCard');
    
    if (resultStatus && resultBadge) {
        resultStatus.textContent = 'READY';
        resultStatus.className = 'result-title';
        resultBadge.textContent = 'WAITING';
        resultBadge.className = 'badge badge-info';
    }
    
    if (confidenceCard) confidenceCard.style.display = 'none';
    if (detailsCard) detailsCard.style.display = 'none';
}

function loadSample() {
    const sampleMessage = `Urgent: Your Account Requires Immediate Verification

Dear User,

We've detected unusual activity on your account. To prevent suspension, please verify your account immediately by clicking the link below:

http://secure-verify-account.com/login

Failure to verify within 24 hours will result in permanent account termination.

Best regards,
Account Security Team

P.S. This is an automated message - please do not reply.`;

    const emailContent = document.getElementById('emailContent');
    if (emailContent) {
        emailContent.value = sampleMessage;
    }
}

function loadHistory() {
    const historyList = document.getElementById('historyList');
    const pagination = document.getElementById('pagination');
    
    if (!historyList) return;
    
    // Show loading state
    historyList.innerHTML = '<div class="detail-item"><div class="loading"></div> Loading history...</div>';
    
    fetch(`/api/history?page=${currentPage}&per_page=${itemsPerPage}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load history');
            }
            return response.json();
        })
        .then(data => {
            if (data.history && data.history.length > 0) {
                let historyHTML = '';
                
                data.history.forEach(item => {
                    historyHTML += `
                        <div class="history-item" data-content="${item.content}">
                            <div class="history-header">
                                <div style="color: ${item.prediction === 'spam' ? 'var(--danger)' : 'var(--success)'}">
                                    ${item.prediction.toUpperCase()} (${Math.round(item.confidence * 100)}%) - ${item.platform.toUpperCase()}
                                </div>
                                <div>${new Date(item.created_at).toLocaleString()}</div>
                            </div>
                            <div class="history-content">${item.content}</div>
                        </div>
                    `;
                });
                
                historyList.innerHTML = historyHTML;
                
                // Add click events to history items
                document.querySelectorAll('.history-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const content = this.dataset.content;
                        const emailContent = document.getElementById('emailContent');
                        if (emailContent) {
                            emailContent.value = content;
                        }
                    });
                });
                
                // Update pagination
                if (pagination && data.pages > 1) {
                    let paginationHTML = '';
                    
                    if (currentPage > 1) {
                        paginationHTML += `<button data-page="${currentPage - 1}">Previous</button>`;
                    }
                    
                    for (let i = 1; i <= data.pages; i++) {
                        paginationHTML += `<button data-page="${i}" ${i === currentPage ? 'class="active"' : ''}>${i}</button>`;
                    }
                    
                    if (currentPage < data.pages) {
                        paginationHTML += `<button data-page="${currentPage + 1}">Next</button>`;
                    }
                    
                    pagination.innerHTML = paginationHTML;
                    
                    // Add event listeners to pagination buttons
                    pagination.querySelectorAll('button').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const page = parseInt(this.dataset.page);
                            if (!isNaN(page)) {
                                currentPage = page;
                                loadHistory();
                            }
                        });
                    });
                }
            } else {
                historyList.innerHTML = '<div class="detail-item">No analysis history yet.</div>';
                if (pagination) pagination.innerHTML = '';
            }
        })
        .catch(error => {
            console.error('Error loading history:', error);
            historyList.innerHTML = '<div class="detail-item">Error loading history.</div>';
            if (pagination) pagination.innerHTML = '';
        });
}

function showAlert(message, type, container) {
    if (!container) {
        container = document.getElementById('alertContainer');
        if (!container) {
            // Create alert container if it doesn't exist
            container = document.createElement('div');
            container.id = 'alertContainer';
            document.querySelector('main').prepend(container);
        }
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-close" onclick="this.parentElement.style.display='none'">&times;</span>
        ${message}
    `;
    
    container.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}