// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Prediction Form Logic ---
    const predictionForm = document.getElementById('prediction-form');
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const resultDiv = document.getElementById('result');
            
            // Show loading state
            resultDiv.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center;">
                    <div class="loading"></div>
                    <p>Analyzing driver data...</p>
                </div>
            `;
            
            fetch('/predict', { 
                method: 'POST', 
                body: formData 
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        resultDiv.innerHTML = `
                            <div class="status-error">
                                <p>Error: ${data.error}</p>
                            </div>
                        `;
                    } else {
                        const outcomeClass = data.outcome === 'Claim Likely' ? 'prediction-likely' : 'prediction-unlikely';
                        resultDiv.innerHTML = `
                            <p><strong>Prediction:</strong> <span class="${outcomeClass}">${data.outcome}</span></p>
                            <p class="probability"><strong>Probability:</strong> ${data.probability}</p>
                            ${data.outcome === 'Claim Likely' ? 
                                '<div class="status-warning" style="margin-top: 1rem;"><p>This driver shows higher risk factors for claims.</p></div>' : 
                                '<div class="status-success" style="margin-top: 1rem;"><p>This driver shows lower risk factors for claims.</p></div>'
                            }
                        `;
                    }
                })
                .catch(error => {
                    console.error('Prediction Error:', error);
                    resultDiv.innerHTML = `
                        <div class="status-error">
                            <p>Failed to process prediction. Please try again.</p>
                        </div>
                    `;
                });
        });
    }

    // --- License Scanner Logic ---
    const scanButton = document.getElementById('scan-button');
    if (scanButton) {
        scanButton.addEventListener('click', () => {
            const uploader = document.getElementById('license-uploader');
            const statusDiv = document.getElementById('scan-status');
            
            if (uploader.files.length === 0) {
                statusDiv.innerHTML = `
                    <div class="status-warning">
                        <p>Please select an image file first.</p>
                    </div>
                `;
                return;
            }
            
            const scanFormData = new FormData();
            scanFormData.append('license_image', uploader.files[0]);
            
            statusDiv.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center;">
                    <div class="loading"></div>
                    <p>Processing license image...</p>
                </div>
            `;
            
            scanButton.disabled = true;
            scanButton.textContent = 'Processing...';

            fetch('/scan-license', { 
                method: 'POST', 
                body: scanFormData 
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'db_success') {
                        statusDiv.innerHTML = `
                            <div class="status-success">
                                <p> Record found in database! Filling form. </p>
                            </div>
                        `;
                        autofillForm(data.parsed_data);
                    } else if (data.status === 'ocr_success') {
                        statusDiv.innerHTML = `
                            <div class="status-info">
                                <p>✓ New user detected. Filling form from scan.</p>
                            </div>
                        `;
                        autofillForm(data.parsed_data);
                    } else {
                        statusDiv.innerHTML = `
                            <div class="status-error">
                                <p>Error: ${data.error || 'Failed to process license'}</p>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Scan Error:', error);
                    statusDiv.innerHTML = `
                        <div class="status-error">
                            <p>Failed to communicate with the server.</p>
                        </div>
                    `;
                })
                .finally(() => {
                    scanButton.disabled = false;
                    scanButton.textContent = 'Scan & Auto-fill';
                });
        });
    }
});

function autofillForm(dataToFill) {
    console.log("Autofill data:", dataToFill);
    for (const key in dataToFill) {
        const formElement = document.querySelector(`[name="${key}"]`);
        if (formElement) {
            formElement.value = dataToFill[key];
            // Trigger change event for select elements
            if (formElement.tagName === 'SELECT') {
                const event = new Event('change');
                formElement.dispatchEvent(event);
            }
        }
    }
}