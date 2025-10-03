document.addEventListener('DOMContentLoaded', function() {
    initializeBootstrapComponents();
    initializeFormValidation();
    initializeWorkLogCalculator();
    initializeDeleteConfirmations();
    initializeFilters();
    initializeSortableTables();
    initializeMobileMenu();
    initializeSmoothScrolling();
    initializeFormAutoSave();
    initializeSubscriptionCalculator();
    initializeCategoryDeleteConfirmation();
    initializeWorkLogHourlyRate();
    initializeInvoiceForm();
    initializeMileageCalculator();
    initializeTwoFactorAuth();
    initializeClockDashboard();
});

// Bootstrap Components Initialization
function initializeBootstrapComponents() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Form Validation
function initializeFormValidation() {
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Work Log Calculator
function initializeWorkLogCalculator() {
    var hoursInput = document.querySelector('input[name="hours_worked"]');
    var rateInput = document.querySelector('input[name="hourly_rate"]');
    var totalInput = document.querySelector('input[name="total_amount"]');

    if (hoursInput && rateInput && totalInput) {
        function calculateTotal() {
            const hours = parseFloat(hoursInput.value) || 0;
            const rate = parseFloat(rateInput.value) || 0;
            const total = hours * rate;
            totalInput.value = total.toFixed(2);
        }

        hoursInput.addEventListener('input', calculateTotal);
        rateInput.addEventListener('input', calculateTotal);
    }
}

// Delete Confirmations
function initializeDeleteConfirmations() {
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
}

// Filter Functionality
function initializeFilters() {
    var filterInputs = document.querySelectorAll('.filter-input');
    filterInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const filterValue = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(filterValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// Sortable Tables
function initializeSortableTables() {
    var sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            const isAscending = this.classList.contains('asc');

            rows.sort(function(a, b) {
                const aValue = a.children[columnIndex].textContent.trim();
                const bValue = b.children[columnIndex].textContent.trim();
                
                if (isAscending) {
                    return bValue.localeCompare(aValue);
                } else {
                    return aValue.localeCompare(bValue);
                }
            });

            // Clear existing sort classes
            sortableHeaders.forEach(h => h.classList.remove('asc', 'desc'));
            
            // Add sort class
            this.classList.add(isAscending ? 'desc' : 'asc');

            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

// Mobile Menu
function initializeMobileMenu() {
    var navbarToggler = document.querySelector('.navbar-toggler');
    var navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

// Smooth Scrolling
function initializeSmoothScrolling() {
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Form Auto-save
function initializeFormAutoSave() {
    var formInputs = document.querySelectorAll('form input, form textarea, form select');
    formInputs.forEach(function(input) {
        const formId = input.closest('form').id || 'default-form';
        const inputKey = `${formId}-${input.name}`;
        
        // Load saved value
        const savedValue = localStorage.getItem(inputKey);
        if (savedValue && input.type !== 'password') {
            try {
                // Check if the input supports value setting and is in a valid state
                if (input.type !== 'file' && input.type !== 'submit' && input.type !== 'button' && input.type !== 'reset') {
                    // Validate that the input is not disabled or readonly
                    if (!input.disabled && !input.readOnly) {
                        input.value = savedValue;
                    }
                }
            } catch (error) {
                // Silently handle InvalidStateError and other value setting errors
                console.warn('Could not restore saved value for input:', input.name, error.message);
            }
        }
        
        // Save on input
        input.addEventListener('input', function() {
            if (input.type !== 'password' && input.type !== 'file' && input.type !== 'submit' && input.type !== 'button' && input.type !== 'reset') {
                try {
                    localStorage.setItem(inputKey, input.value);
                } catch (error) {
                    console.warn('Could not save value for input:', input.name, error.message);
                }
            }
        });
    });

    // Clear saved form data on successful submission
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const formId = this.id || 'default-form';
            const inputs = this.querySelectorAll('input, textarea, select');
            
            inputs.forEach(function(input) {
                if (input.name && input.type !== 'password') {
                    localStorage.removeItem(`${formId}-${input.name}`);
                }
            });
        });
    });
}

// Subscription Billing Date Calculator
function initializeSubscriptionCalculator() {
    // Look for subscription form fields by their actual names or Django form IDs
    var dateField = document.querySelector('input[name="date"]') || 
                   document.querySelector('input[id*="date"]') ||
                   document.querySelector('input[type="date"]');
    var billingCycleField = document.querySelector('select[name="billing_cycle"]') || 
                           document.querySelector('select[id*="billing_cycle"]');
    var nextBillingDateField = document.querySelector('input[name="next_billing_date"]') || 
                               document.querySelector('input[id*="next_billing_date"]');

    if (dateField && billingCycleField && nextBillingDateField) {
        function calculateNextBillingDate() {
            const selectedDate = new Date(dateField.value);
            const billingCycle = billingCycleField.value;
            
            if (!selectedDate || isNaN(selectedDate.getTime()) || !billingCycle) {
                return;
            }
            
            let nextDate = new Date(selectedDate);
            
            switch(billingCycle) {
                case 'DAILY':
                    nextDate.setDate(nextDate.getDate() + 1);
                    break;
                case 'WEEKLY':
                    nextDate.setDate(nextDate.getDate() + 7);
                    break;
                case 'MONTHLY':
                    nextDate.setMonth(nextDate.getMonth() + 1);
                    break;
                case 'QUARTERLY':
                    nextDate.setMonth(nextDate.getMonth() + 3);
                    break;
                case 'YEARLY':
                    nextDate.setFullYear(nextDate.getFullYear() + 1);
                    break;
            }
            
            // Format the date as YYYY-MM-DD for the input field
            const year = nextDate.getFullYear();
            const month = String(nextDate.getMonth() + 1).padStart(2, '0');
            const day = String(nextDate.getDate()).padStart(2, '0');
            const formattedDate = `${year}-${month}-${day}`;
            
            nextBillingDateField.value = formattedDate;
        }
        
        // Calculate when date or billing cycle changes
        dateField.addEventListener('change', calculateNextBillingDate);
        billingCycleField.addEventListener('change', calculateNextBillingDate);
        
        // Calculate initial value if both fields have values
        if (dateField.value && billingCycleField.value) {
            calculateNextBillingDate();
        }
    }
}

// Category Deletion Confirmation
function initializeCategoryDeleteConfirmation() {
    const replacementSelect = document.getElementById('replacement_category');
    const deleteBtn = document.getElementById('deleteBtn');
    
    if (replacementSelect && deleteBtn) {
        function updateDeleteButton() {
            if (replacementSelect.value && replacementSelect.value !== '') {
                deleteBtn.disabled = false;
                deleteBtn.innerHTML = '<i class="fas fa-trash me-2"></i>Delete Category & Move Items';
            } else {
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = '<i class="fas fa-trash me-2"></i>Delete Category';
            }
        }
        
        replacementSelect.addEventListener('change', updateDeleteButton);
        updateDeleteButton(); // Initial state
    }
}

// Work Log Hourly Rate Auto-population
function initializeWorkLogHourlyRate() {
    const companyClientSelect = document.getElementById('id_company_client');
    const hourlyRateInput = document.getElementById('id_hourly_rate');
    
    // Check if we're on a work log form
    if (!companyClientSelect || !hourlyRateInput) {
        return;
    }
    
    // Get the client data from the data attribute (we'll add this to the template)
    const clientsDataElement = document.getElementById('clients-data');
    if (!clientsDataElement) {
        console.log('Clients data element not found - hourly rate auto-population disabled');
        return;
    }
    
    try {
        // Get the text content and clean it up
        let clientsDataText = clientsDataElement.textContent.trim();
        
        // Remove any HTML entities or extra whitespace
        clientsDataText = clientsDataText.replace(/&quot;/g, '"').replace(/&amp;/g, '&');
        
        // Validate that we have valid JSON content
        if (!clientsDataText || clientsDataText === 'null' || clientsDataText === 'undefined') {
            console.warn('No clients data available');
            return;
        }
        
        // Additional cleanup for any remaining whitespace or newlines
        clientsDataText = clientsDataText.replace(/\s+/g, ' ').trim();
        
        const clientsData = JSON.parse(clientsDataText);
        
        // Validate that clientsData is an object
        if (typeof clientsData !== 'object' || clientsData === null) {
            console.warn('Clients data is not a valid object');
            return;
        }
        
        // Function to update hourly rate when client changes
        function updateHourlyRate() {
            const selectedClientId = companyClientSelect.value;
            if (selectedClientId && clientsData[selectedClientId]) {
                hourlyRateInput.value = clientsData[selectedClientId];
            }
        }
        
        // Add event listener for client selection change
        companyClientSelect.addEventListener('change', updateHourlyRate);
        
        // Also update on page load if a client is pre-selected (for edit forms)
        if (companyClientSelect.value) {
            updateHourlyRate();
        }
    } catch (error) {
        console.error('Error parsing clients data:', error);
        console.error('Raw content:', clientsDataElement.textContent);
        console.error('Cleaned content:', clientsDataElement.textContent.trim());
    }
}

// Invoice Form Initialization
function initializeInvoiceForm() {
    const clientSelect = document.getElementById('id_client');
    const workLogsSection = document.getElementById('work-logs-section');
    const workLogsContainer = document.getElementById('work-logs-container');
    const noWorkLogs = document.getElementById('no-work-logs');
    const selectClientPrompt = document.getElementById('select-client-prompt');
    const submitBtn = document.getElementById('submit-btn');
    
    // Only initialize if we're on the invoice form page
    if (!clientSelect) {
        return;
    }
    
    // When client is selected, show available work logs
    clientSelect.addEventListener('change', function() {
        const clientId = this.value;
        
        if (clientId) {
            // Hide the prompt and show the work logs section
            if (selectClientPrompt) selectClientPrompt.style.display = 'none';
            if (workLogsSection) workLogsSection.style.display = 'block';
            
            // Fetch available work logs for this client
            fetch(`/invoices/get-available-worklogs/${clientId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.work_logs.length > 0) {
                        if (workLogsContainer) workLogsContainer.innerHTML = '';
                        if (noWorkLogs) noWorkLogs.style.display = 'none';
                        
                        data.work_logs.forEach(worklog => {
                            const div = document.createElement('div');
                            div.className = 'form-check mb-3 p-4 border rounded bg-light work-log-card';
                            
                            const checkbox = document.createElement('input');
                            checkbox.type = 'checkbox';
                            checkbox.name = 'work_logs';
                            checkbox.value = worklog.id;
                            checkbox.className = 'form-check-input me-3';
                            checkbox.id = `worklog-${worklog.id}`;
                            
                            const label = document.createElement('label');
                            label.className = 'form-check-label fw-bold w-100';
                            label.htmlFor = `worklog-${worklog.id}`;
                            label.innerHTML = `
                                <div class="row align-items-center">
                                    <div class="col-md-3">
                                        <div class="text-center">
                                            <div class="text-primary fw-bold fs-6">${worklog.work_date}</div>
                                            <small class="text-muted">Work Date</small>
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <div class="text-center">
                                            <div class="text-info fw-bold fs-6">${worklog.hours_worked}h</div>
                                            <small class="text-muted">Hours</small>
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <div class="text-center">
                                            <div class="text-success fw-bold fs-6">£${worklog.hourly_rate}</div>
                                            <small class="text-muted">Rate/Hour</small>
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <div class="text-center">
                                            <div class="text-success fw-bold fs-5">£${worklog.total_amount}</div>
                                            <small class="text-muted">Total</small>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="text-center">
                                            <span class="badge bg-primary fs-6">Ready to Invoice</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                            
                            div.appendChild(checkbox);
                            div.appendChild(label);
                            if (workLogsContainer) workLogsContainer.appendChild(div);
                        });
                        
                        // Enable submit button
                        if (submitBtn) submitBtn.disabled = false;
                        
                    } else {
                        if (workLogsContainer) workLogsContainer.innerHTML = '';
                        if (noWorkLogs) noWorkLogs.style.display = 'block';
                        if (submitBtn) submitBtn.disabled = true;
                    }
                })
                .catch(error => {
                    console.error('Error fetching work logs:', error);
                    if (workLogsContainer) workLogsContainer.innerHTML = '';
                    if (noWorkLogs) noWorkLogs.style.display = 'block';
                    if (submitBtn) submitBtn.disabled = true;
                });
        } else {
            // Show the prompt and hide the work logs section
            if (selectClientPrompt) selectClientPrompt.style.display = 'block';
            if (workLogsSection) workLogsSection.style.display = 'none';
            if (submitBtn) submitBtn.disabled = true;
        }
    });
    
    // Enable/disable submit button based on work log selection
    document.addEventListener('change', function(e) {
        if (e.target.name === 'work_logs') {
            const selectedWorkLogs = document.querySelectorAll('input[name="work_logs"]:checked');
            submitBtn.disabled = selectedWorkLogs.length === 0;
        }
    });
}

// Two-Factor Authentication Setup
function initializeTwoFactorAuth() {
    // Auto-focus on token input for 2FA setup
    const tokenInput = document.querySelector('input[name="token"]');
    const form = document.getElementById('twofa-form');
    
    if (tokenInput) {
        tokenInput.focus();
        
        // Auto-submit when token is complete (for verify page)
        if (form) {
            tokenInput.addEventListener('input', function() {
                if (this.value.length === 6 && /^\d{6}$/.test(this.value)) {
                    // Small delay to let user see the complete code
                    setTimeout(() => {
                        form.submit();
                    }, 500);
                }
            });
        }
    }
}

// Mileage Calculator
function initializeMileageCalculator() {
    // Look for mileage form elements
    const milesInput = document.querySelector('input[id*="miles"]');
    const claimPreview = document.getElementById('claim-preview');
    const previewMiles = document.getElementById('preview-miles');
    const previewRate = document.getElementById('preview-rate');
    const previewTotal = document.getElementById('preview-total');
    const clientSelect = document.querySelector('select[id*="client"]');
    const endLocationInput = document.querySelector('input[id*="end_location"]');
    
    // Only initialize if we're on a mileage form page
    if (!milesInput) {
        return;
    }
    
        // Client address auto-population
        if (clientSelect && endLocationInput) {
            // Get client data from the data attribute
            const clientsDataElement = document.getElementById('clients-data');
            const endAddressInput = document.querySelector('textarea[id*="end_address"]');
            
            if (clientsDataElement) {
                try {
                    const clientsDataText = clientsDataElement.textContent.trim();
                    
                    // Skip if empty or invalid
                    if (!clientsDataText || clientsDataText === 'null' || clientsDataText === 'undefined' || clientsDataText === '{}') {
                        return;
                    }
                    
                    const clientsData = JSON.parse(clientsDataText);
                    
                    if (typeof clientsData === 'object' && clientsData !== null) {
                        // Function to update end location and address when client changes
                        function updateEndLocation() {
                            const selectedClientId = clientSelect.value;
                            if (selectedClientId && clientsData[selectedClientId]) {
                                // Set end location to client company name
                                endLocationInput.value = clientSelect.options[clientSelect.selectedIndex].text;
                                // Set end address to client's full address
                                if (endAddressInput) {
                                    endAddressInput.value = clientsData[selectedClientId];
                                }
                            }
                        }
                        
                        // Add event listener for client selection change
                        clientSelect.addEventListener('change', updateEndLocation);
                        
                        // Also update on page load if a client is pre-selected (for edit forms)
                        if (clientSelect.value) {
                            updateEndLocation();
                        }
                    }
                } catch (error) {
                    console.warn('Could not parse clients data for mileage form:', error);
                    // Don't show error in console for missing data, just silently continue
                }
            }
        }
    
    // Claim preview functionality (only if preview elements exist)
    if (claimPreview && previewMiles && previewRate && previewTotal) {
        function updateClaimPreview() {
            const miles = parseFloat(milesInput.value);
            if (miles > 0) {
                // Make API call to calculate claim
                fetch(`/mileage/api/calculate/?miles=${miles}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            claimPreview.style.display = 'none';
                        } else {
                            previewMiles.textContent = data.miles;
                            previewRate.textContent = (data.effective_rate * 100).toFixed(1);
                            previewTotal.textContent = data.total_claim.toFixed(2);
                            claimPreview.style.display = 'block';
                        }
                    })
                    .catch(error => {
                        console.error('Error calculating claim:', error);
                        claimPreview.style.display = 'none';
                    });
            } else {
                claimPreview.style.display = 'none';
            }
        }
        
        milesInput.addEventListener('input', updateClaimPreview);
        
        // Update preview on page load if miles field has a value
        if (milesInput.value) {
            updateClaimPreview();
        }
    }
}


// Utility functions
window.FinanceTracker = {
    formatCurrency: function(amount, currency = 'GBP') {
        if (currency === 'GBP') {
            return new Intl.NumberFormat('en-GB', {
                style: 'currency',
                currency: 'GBP'
            }).format(amount);
        }
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency || 'USD'
        }).format(amount);
    },
    
    formatDate: function(dateString, format = 'short') {
        const date = new Date(dateString);
        if (format === 'long') {
            return date.toLocaleDateString('en-GB', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
        return date.toLocaleDateString('en-GB', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }, 5000);
        }
    },
    
    // Add utility functions for common operations
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Format numbers with proper decimal places
    formatNumber: function(number, decimals = 2) {
        return parseFloat(number).toFixed(decimals);
    }
};

// Clock Dashboard Functionality
function initializeClockDashboard() {
    // Update duration display for active session
    const durationElement = document.getElementById('current-duration');
    if (durationElement) {
        function updateDuration() {
            const clockInTimeElement = document.querySelector('[data-clock-in-time]');
            if (!clockInTimeElement) {
                return;
            }
            
            const clockInTime = new Date(clockInTimeElement.dataset.clockInTime);
            const now = new Date();
            const diffMs = now - clockInTime;
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
            
            let durationText;
            if (diffHours > 0) {
                durationText = `${diffHours}h ${diffMinutes}m`;
            } else {
                durationText = `${diffMinutes}m`;
            }
            
            durationElement.textContent = durationText;
        }
        
        // Update duration every minute
        setInterval(updateDuration, 60000);
        
        // Initial update
        updateDuration();
    }
}
