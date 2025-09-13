document.addEventListener('DOMContentLoaded', function() {
    // API Key Management
    const generateBtn = document.getElementById('generateApiKeyBtn');
    const copyBtn = document.getElementById('copyApiKeyBtn');
    const apiKeyValue = document.getElementById('apiKeyValue');
    
    if (generateBtn) {
        generateBtn.addEventListener('click', generateApiKey);
    }
    
    if (copyBtn) {
        copyBtn.addEventListener('click', copyApiKey);
    }
    
    // Tab functionality
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Update active tab link
            tabLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });
});

function generateApiKey() {
    const generateBtn = document.getElementById('generateApiKeyBtn');
    const apiKeyDisplay = document.getElementById('apiKeyValue');
    const copyBtn = document.getElementById('copyApiKeyBtn');
    
    if (generateBtn) {
        generateBtn.innerHTML = '<div class="loading"></div> GENERATING';
        generateBtn.disabled = true;
    }
    
    fetch('/api/generate-key', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert('Failed to generate API key: ' + data.error, 'error');
        } else {
            if (apiKeyDisplay) {
                apiKeyDisplay.textContent = data.api_key;
            }
            if (copyBtn) {
                copyBtn.disabled = false;
            }
            showAlert('API key generated successfully!', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Failed to generate API key', 'error');
    })
    .finally(() => {
        if (generateBtn) {
            generateBtn.innerHTML = '<i class="fas fa-key"></i> Generate New API Key';
            generateBtn.disabled = false;
        }
    });
}

function copyApiKey() {
    const apiKey = document.getElementById('apiKeyValue').textContent;
    navigator.clipboard.writeText(apiKey).then(() => {
        showAlert('API key copied to clipboard!', 'success');
    }).catch(err => {
        showAlert('Failed to copy API key', 'error');
    });
}