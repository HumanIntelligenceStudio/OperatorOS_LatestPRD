/**
 * OperatorOS - Main JavaScript functionality
 * Handles interactive features for the AI-powered goal achievement platform
 */

// Global variables
let currentUser = null;
let aiResponseHistory = [];
let activeCharts = {};

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupTooltips();
    setupAnimations();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Check authentication status
    checkAuthStatus();
    
    // Initialize charts if on dashboard
    if (document.getElementById('userGrowthChart')) {
        initializeDashboardCharts();
    }
    
    // Set up real-time updates
    setupRealTimeUpdates();
    
    // Initialize forms
    setupFormValidation();
    
    console.log('OperatorOS initialized successfully');
}

/**
 * Setup event listeners for interactive elements
 */
function setupEventListeners() {
    // AI Chat form submission
    const aiChatForm = document.getElementById('aiChatForm');
    if (aiChatForm) {
        aiChatForm.addEventListener('submit', handleAIChat);
    }
    
    // Goal creation form
    const createGoalForm = document.getElementById('createGoalForm');
    if (createGoalForm) {
        createGoalForm.addEventListener('submit', handleGoalCreation);
    }
    
    // File upload handlers
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileUpload);
    });
    
    // Navigation enhancements
    setupNavigationEnhancements();
    
    // Search functionality
    setupSearchFunctionality();
    
    // Auto-save functionality
    setupAutoSave();
}

/**
 * Handle AI chat form submission
 */
function handleAIChat(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const responseDiv = document.getElementById('aiResponse');
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Thinking...';
    
    // Hide previous response
    if (responseDiv) {
        responseDiv.classList.add('d-none');
    }
    
    fetch('/ai_chat', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAIResponse(data);
            addToHistory(formData.get('prompt'), data.response);
            
            // Clear the input
            form.querySelector('textarea[name="prompt"]').value = '';
            
            // Show success notification
            showNotification('AI response generated successfully!', 'success');
        } else {
            showNotification('Error: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('AI Chat Error:', error);
        showNotification('An error occurred while processing your request.', 'danger');
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
    });
}

/**
 * Display AI response with proper formatting
 */
function displayAIResponse(data) {
    const responseDiv = document.getElementById('aiResponse');
    const providerSpan = document.getElementById('responseProvider');
    const contentDiv = document.getElementById('responseContent');
    
    if (!responseDiv || !providerSpan || !contentDiv) return;
    
    // Set provider information
    providerSpan.textContent = data.provider || 'Unknown';
    
    // Format and display content
    const formattedContent = formatAIResponse(data.response);
    contentDiv.innerHTML = formattedContent;
    
    // Show the response
    responseDiv.classList.remove('d-none');
    
    // Setup rating functionality
    setupRatingStars(data.conversation_id);
    
    // Animate the response
    responseDiv.classList.add('fade-in');
    
    // Scroll to response
    responseDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Format AI response for better display
 */
function formatAIResponse(response) {
    // Convert markdown-style formatting
    let formatted = response
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^(.+)$/gm, '<p>$1</p>');
    
    // Handle lists
    formatted = formatted.replace(/^- (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Handle numbered lists
    formatted = formatted.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    
    return formatted;
}

/**
 * Setup rating stars functionality
 */
function setupRatingStars(conversationId) {
    const stars = document.querySelectorAll('#ratingStars i');
    
    stars.forEach((star, index) => {
        star.addEventListener('click', function() {
            const rating = index + 1;
            rateResponse(conversationId, rating);
            
            // Update visual state
            stars.forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('text-warning');
                } else {
                    s.classList.remove('text-warning');
                }
            });
        });
        
        // Hover effects
        star.addEventListener('mouseenter', function() {
            stars.forEach((s, i) => {
                if (i <= index) {
                    s.classList.add('text-warning');
                } else {
                    s.classList.remove('text-warning');
                }
            });
        });
    });
    
    // Reset on mouse leave
    const ratingContainer = document.getElementById('ratingStars');
    if (ratingContainer) {
        ratingContainer.addEventListener('mouseleave', function() {
            stars.forEach(s => s.classList.remove('text-warning'));
        });
    }
}

/**
 * Rate AI response
 */
function rateResponse(conversationId, rating) {
    const formData = new FormData();
    formData.append('conversation_id', conversationId);
    formData.append('rating', rating);
    
    fetch('/rate_response', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Thank you for your feedback!', 'success');
        } else {
            showNotification('Error saving rating', 'warning');
        }
    })
    .catch(error => {
        console.error('Rating Error:', error);
    });
}

/**
 * Handle goal creation
 */
function handleGoalCreation(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Validate form
    if (!validateGoalForm(formData)) {
        return;
    }
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
    
    // Submit form
    fetch('/create_goal', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            showNotification('Goal created successfully!', 'success');
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createGoalModal'));
            if (modal) modal.hide();
            
            // Refresh page to show new goal
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error('Failed to create goal');
        }
    })
    .catch(error => {
        console.error('Goal Creation Error:', error);
        showNotification('Error creating goal. Please try again.', 'danger');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-plus"></i> Create Goal';
    });
}

/**
 * Validate goal creation form
 */
function validateGoalForm(formData) {
    const title = formData.get('title');
    const description = formData.get('description');
    
    if (!title || title.trim().length < 3) {
        showNotification('Goal title must be at least 3 characters long', 'warning');
        return false;
    }
    
    if (!description || description.trim().length < 10) {
        showNotification('Goal description must be at least 10 characters long', 'warning');
        return false;
    }
    
    return true;
}

/**
 * Handle file uploads
 */
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel'];
    
    if (file.size > maxSize) {
        showNotification('File size must be less than 10MB', 'warning');
        event.target.value = '';
        return;
    }
    
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.csv')) {
        showNotification('Only CSV files are allowed', 'warning');
        event.target.value = '';
        return;
    }
    
    // Show file info
    const fileInfo = document.createElement('div');
    fileInfo.className = 'alert alert-info mt-2';
    fileInfo.innerHTML = `
        <i class="fas fa-file-csv"></i>
        Selected: ${file.name} (${formatFileSize(file.size)})
    `;
    
    // Insert after file input
    const existingInfo = event.target.parentNode.querySelector('.alert');
    if (existingInfo) {
        existingInfo.remove();
    }
    event.target.parentNode.insertBefore(fileInfo, event.target.nextSibling);
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to container
    let container = document.getElementById('notificationContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Initialize dashboard charts
 */
function initializeDashboardCharts() {
    // This function would be called when dashboard charts need to be initialized
    // The actual chart initialization is handled in the template files
    console.log('Dashboard charts initialized');
}

/**
 * Setup real-time updates
 */
function setupRealTimeUpdates() {
    // Poll for updates every 30 seconds
    setInterval(checkForUpdates, 30000);
}

/**
 * Check for system updates
 */
function checkForUpdates() {
    // This could check for new notifications, goal progress updates, etc.
    // For now, we'll just update timestamps
    updateTimestamps();
}

/**
 * Update relative timestamps
 */
function updateTimestamps() {
    const timestamps = document.querySelectorAll('[data-timestamp]');
    timestamps.forEach(element => {
        const timestamp = element.getAttribute('data-timestamp');
        if (timestamp) {
            element.textContent = formatRelativeTime(new Date(timestamp));
        }
    });
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
function formatRelativeTime(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
    if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
    if (diffInSeconds < 2592000) return Math.floor(diffInSeconds / 86400) + ' days ago';
    
    return date.toLocaleDateString();
}

/**
 * Setup tooltips
 */
function setupTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup animations
 */
function setupAnimations() {
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });
    
    // Observe elements with animation classes
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Setup navigation enhancements
 */
function setupNavigationEnhancements() {
    // Add active class to current page
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Setup search functionality
 */
function setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            const query = this.value.toLowerCase();
            const searchables = document.querySelectorAll('.searchable');
            
            searchables.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query) || query === '') {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        }, 300));
    });
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Setup auto-save functionality
 */
function setupAutoSave() {
    const autoSaveFields = document.querySelectorAll('.auto-save');
    
    autoSaveFields.forEach(field => {
        field.addEventListener('input', debounce(function() {
            // Auto-save implementation would go here
            console.log('Auto-saving:', field.name, field.value);
        }, 2000));
    });
}

/**
 * Add to AI response history
 */
function addToHistory(prompt, response) {
    aiResponseHistory.push({
        prompt: prompt,
        response: response,
        timestamp: new Date()
    });
    
    // Keep only last 50 responses
    if (aiResponseHistory.length > 50) {
        aiResponseHistory.shift();
    }
    
    // Store in localStorage
    localStorage.setItem('aiResponseHistory', JSON.stringify(aiResponseHistory));
}

/**
 * Get AI response history
 */
function getHistory() {
    const stored = localStorage.getItem('aiResponseHistory');
    return stored ? JSON.parse(stored) : [];
}

/**
 * Clear AI response history
 */
function clearHistory() {
    aiResponseHistory = [];
    localStorage.removeItem('aiResponseHistory');
    showNotification('History cleared', 'info');
}

/**
 * Check authentication status
 */
function checkAuthStatus() {
    // This would check if user is authenticated
    // For now, we'll just check if there's a user element
    const userElement = document.querySelector('.navbar-nav .dropdown-toggle');
    if (userElement) {
        currentUser = {
            name: userElement.textContent.trim(),
            authenticated: true
        };
    }
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Utility function to copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'danger');
    });
}

/**
 * Format currency for display
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Format percentage for display
 */
function formatPercentage(value, decimals = 1) {
    return (value * 100).toFixed(decimals) + '%';
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Generate random ID
 */
function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Export functionality for reports
 */
function exportData(data, filename, type = 'json') {
    let content, mimeType;
    
    switch (type) {
        case 'json':
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
            break;
        case 'csv':
            content = convertToCSV(data);
            mimeType = 'text/csv';
            break;
        default:
            throw new Error('Unsupported export type');
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Convert data to CSV format
 */
function convertToCSV(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return '';
    }
    
    const headers = Object.keys(data[0]);
    const csvRows = [];
    
    // Add header row
    csvRows.push(headers.join(','));
    
    // Add data rows
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

/**
 * Handle page visibility changes
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, pause updates
        console.log('Page hidden, pausing updates');
    } else {
        // Page is visible, resume updates
        console.log('Page visible, resuming updates');
        checkForUpdates();
    }
});

/**
 * Handle online/offline status
 */
window.addEventListener('online', function() {
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Connection lost. Some features may not work.', 'warning');
});

/**
 * Initialize service worker if available
 */
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registered successfully');
            })
            .catch(error => {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Export functions for global use
window.OperatorOS = {
    showNotification,
    copyToClipboard,
    formatCurrency,
    formatPercentage,
    validateEmail,
    exportData,
    clearHistory,
    rateResponse
};

console.log('OperatorOS Main JavaScript loaded successfully');
