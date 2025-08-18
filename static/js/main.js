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
            input.value = savedValue;
        }
        
        // Save on input
        input.addEventListener('input', function() {
            if (input.type !== 'password') {
                localStorage.setItem(inputKey, input.value);
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
    // Look for subscription form fields by their actual names
    var dateField = document.querySelector('input[name="date"]');
    var billingCycleField = document.querySelector('select[name="billing_cycle"]');
    var nextBillingDateField = document.querySelector('input[name="next_billing_date"]');

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
