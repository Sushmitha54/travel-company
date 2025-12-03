// ========================================
// TRAVEL COMPANY - MODERN JAVASCRIPT
// ========================================

// Utility Functions
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// Configuration
const CONFIG = {
    baseUrl: window.location.origin,
    apiTimeout: 10000,
    fadeDuration: 300
};

// Enhanced Fetch with timeout and error handling
async function apiRequest(url, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.apiTimeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);
        console.error('API Request failed:', error);
        throw error;
    }
}

// UI Utilities
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in-up`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        box-shadow: var(--shadow-lg);
    `;

    document.body.appendChild(notification);

    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }

    return notification;
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showSpinner(element) {
    element.classList.add('loading');
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    element.appendChild(spinner);
    return spinner;
}

function hideSpinner(element) {
    element.classList.remove('loading');
    const spinner = element.querySelector('.spinner');
    if (spinner) spinner.remove();
}

function fadeIn(element, duration = CONFIG.fadeDuration) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = `all ${duration}ms ease-out`;

    requestAnimationFrame(() => {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    });
}

function fadeOut(element, duration = CONFIG.fadeDuration) {
    element.style.transition = `all ${duration}ms ease-out`;
    element.style.opacity = '0';
    element.style.transform = 'translateY(-20px)';

    setTimeout(() => {
        element.style.display = 'none';
    }, duration);
}

// Form Handling
function handleFormSubmission(formId, endpoint, successCallback = null) {
    const form = $(`#${formId}`);
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        const spinner = showSpinner(submitBtn);
        submitBtn.textContent = 'Processing...';

        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            // Add CSRF token if present
            const csrfToken = form.querySelector('[name="csrf_token"]');
            if (csrfToken) {
                data.csrf_token = csrfToken.value;
            }

            const result = await apiRequest(`${CONFIG.baseUrl}${endpoint}`, {
                method: 'POST',
                body: JSON.stringify(data)
            });

            if (result.success !== false) {
                showNotification(result.message || 'Operation completed successfully!', 'success');
                form.reset();

                if (successCallback) {
                    successCallback(result);
                }
            } else {
                showNotification(result.message || 'An error occurred', 'error');
            }

        } catch (error) {
            console.error('Form submission error:', error);
            showNotification('Network error. Please try again.', 'error');
        } finally {
            hideSpinner(submitBtn);
            submitBtn.textContent = originalText;
        }
    });
}

// Ride Posting Functionality
function initializeRidePosting() {
    handleFormSubmission('join-form', '/submit', (result) => {
        loadGroups(); // Refresh groups after posting
    });

    // Refresh button
    const refreshBtn = $('#refresh-groups');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadGroups();
            showNotification('Groups refreshed!', 'info');
        });
    }
}

// Group Loading with Modern UI
async function loadGroups() {
    const groupsContainer = $('#groups-list');
    if (!groupsContainer) return;

    try {
        showSpinner(groupsContainer);
        const data = await apiRequest(`${CONFIG.baseUrl}/groups`);

        groupsContainer.innerHTML = '';

        if (Object.keys(data).length === 0) {
            groupsContainer.innerHTML = `
                <div class="text-center p-5">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">No ride groups yet</h4>
                    <p class="text-secondary">Be the first to post a ride and start a group!</p>
                </div>
            `;
            return;
        }

        for (const [destination, rides] of Object.entries(data)) {
            const groupCard = document.createElement('div');
            groupCard.className = 'card mb-4 fade-in-up';
            groupCard.innerHTML = `
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-map-marker-alt me-2"></i>
                        ${destination}
                        <span class="badge bg-primary ms-2">${rides.length} ride${rides.length !== 1 ? 's' : ''}</span>
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        ${rides.map(ride => `
                            <div class="col-md-6 col-lg-4 mb-3">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body">
                                        <h6 class="card-title">
                                            <i class="fas fa-car text-primary me-2"></i>
                                            ${ride.name}
                                        </h6>
                                        <div class="text-muted small mb-2">
                                            <i class="fas fa-clock me-1"></i>
                                            ${ride.date || 'Flexible timing'}
                                        </div>
                                        <div class="text-muted small">
                                            <i class="fas fa-phone me-1"></i>
                                            ${ride.contact}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;

            groupsContainer.appendChild(groupCard);
            fadeIn(groupCard);
        }

    } catch (error) {
        console.error('Error loading groups:', error);
        groupsContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to load ride groups. Please refresh the page.
            </div>
        `;
    } finally {
        hideSpinner(groupsContainer);
    }
}

// Booking Form Enhancements
function initializeBookingForm() {
    const bookingForm = $('#bookingForm');
    if (!bookingForm) return;

    // Real-time validation
    const inputs = bookingForm.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });

    function validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        switch (field.name) {
            case 'name':
                if (value.length < 2) {
                    isValid = false;
                    message = 'Name must be at least 2 characters';
                }
                break;
            case 'contact':
                if (!/^\d{10,15}$/.test(value)) {
                    isValid = false;
                    message = 'Please enter a valid phone number (10-15 digits)';
                }
                break;
            case 'passengers':
                const passengers = parseInt(value);
                if (passengers < 1 || passengers > 8) {
                    isValid = false;
                    message = 'Number of passengers must be between 1 and 8';
                }
                break;
        }

        field.classList.toggle('is-invalid', !isValid);
        field.classList.toggle('is-valid', isValid && value.length > 0);

        const feedback = field.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = message;
        }

        return isValid;
    }
}

// Dashboard Enhancements
function initializeDashboard() {
    // Add loading states to action buttons
    const actionButtons = $$('.btn');
    actionButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.form || this.closest('form')) {
                const originalText = this.textContent;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                this.disabled = true;

                // Re-enable after 5 seconds (fallback)
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 5000);
            }
        });
    });
}

// Modal Enhancements
function initializeModals() {
    const modals = $$('.modal');
    modals.forEach(modal => {
        const modalElement = new bootstrap.Modal(modal);

        // Add backdrop blur effect
        modal.addEventListener('show.bs.modal', function() {
            document.body.style.backdropFilter = 'blur(4px)';
        });

        modal.addEventListener('hidden.bs.modal', function() {
            document.body.style.backdropFilter = '';
        });
    });
}

// Responsive Navigation
function initializeResponsiveNav() {
    const nav = $('nav');
    const navContainer = $('.nav-container');

    // Add mobile menu toggle for smaller screens
    if (window.innerWidth < 768) {
        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.className = 'mobile-menu-btn';
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
        mobileMenuBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0.5rem;
            margin-left: auto;
        `;

        navContainer.insertBefore(mobileMenuBtn, navContainer.lastElementChild);

        mobileMenuBtn.addEventListener('click', function() {
            const navLinks = navContainer.querySelectorAll('a');
            navLinks.forEach(link => {
                if (link !== navContainer.firstElementChild) { // Skip logo
                    link.style.display = link.style.display === 'none' ? 'block' : 'none';
                }
            });
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Travel Company JavaScript loaded!');

    // Initialize all features
    initializeRidePosting();
    initializeBookingForm();
    initializeDashboard();
    initializeModals();
    initializeResponsiveNav();

    // Load initial data
    if ($('#groups-list')) {
        loadGroups();
    }

    // Add loading animations to page elements
    const cards = $$('.card');
    cards.forEach((card, index) => {
        setTimeout(() => fadeIn(card), index * 100);
    });

    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
        showNotification('An unexpected error occurred. Please refresh the page.', 'error');
    });

    // Service worker for PWA (if needed later)
    if ('serviceWorker' in navigator) {
        // Register service worker for offline functionality
        // navigator.serviceWorker.register('/sw.js');
    }

    console.log('✅ All Travel Company features initialized!');
});

// Export functions for potential use in other scripts
window.TravelCompany = {
    showNotification,
    apiRequest,
    loadGroups,
    fadeIn,
    fadeOut
};
