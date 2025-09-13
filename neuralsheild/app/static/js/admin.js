document.addEventListener('DOMContentLoaded', function() {
    // Model training
    const trainBtn = document.getElementById('trainModelBtn');
    if (trainBtn) {
        trainBtn.addEventListener('click', trainModel);
    }
    
    // Toggle user status
    document.querySelectorAll('.toggle-user').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.dataset.userId;
            fetch(`/admin/user/${userId}/toggle`, {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Failed to update user status', 'error');
            });
        });
    });
    
    // Mark contact as read
    document.querySelectorAll('.mark-read').forEach(btn => {
        btn.addEventListener('click', function() {
            const contactId = this.dataset.contactId;
            fetch(`/admin/contact/${contactId}/read`, {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Failed to mark contact as read', 'error');
            });
        });
    });
});

function trainModel() {
    const trainBtn = document.getElementById('trainModelBtn');
    
    if (trainBtn) {
        trainBtn.innerHTML = '<div class="loading"></div> TRAINING';
        trainBtn.disabled = true;
    }
    
    fetch('/admin/train-model', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`Model trained successfully! Accuracy: ${(data.accuracy * 100).toFixed(2)}%`, 'success');
            // Refresh the page to show updated training logs
            setTimeout(() => location.reload(), 2000);
        } else {
            showAlert('Model training failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Model training failed', 'error');
    })
    .finally(() => {
        if (trainBtn) {
            trainBtn.innerHTML = '<i class="fas fa-cogs"></i> Train Model';
            trainBtn.disabled = false;
        }
    });
}