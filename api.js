const API_BASE_URL = '/api';

const api = {
    // Auth
    async register(userData) {
        return fetchAPI('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },

    async login(credentials) {
        return fetchAPI('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    },

    async getMe() {
        return fetchAPI('/auth/me');
    },

    // Profile
    async getProfile() {
        return fetchAPI('/students/profile');
    },

    async updateProfile(profileData) {
        return fetchAPI('/students/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    },

    // Opportunities
    async getOpportunities(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `/opportunities${queryString ? `?${queryString}` : ''}`;
        return fetchAPI(url);
    },

    async getOpportunity(id) {
        return fetchAPI(`/opportunities/${id}`);
    },

    // Roadmap
    async getRoadmap() {
        return fetchAPI('/roadmap');
    },

    // Bookmarks
    async getBookmarks() {
        return fetchAPI('/bookmarks');
    },

    async addBookmark(opportunityId) {
        return fetchAPI(`/bookmarks/${opportunityId}`, {
            method: 'POST'
        });
    },

    async removeBookmark(opportunityId) {
        return fetchAPI(`/bookmarks/${opportunityId}`, {
            method: 'DELETE'
        });
    },

    // Applications
    async getApplications() {
        return fetchAPI('/applications');
    },

    async updateApplicationStatus(opportunityId, statusData) {
        return fetchAPI(`/applications/${opportunityId}/status`, {
            method: 'PUT',
            body: JSON.stringify(statusData)
        });
    }
};

async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'API request failed');
        }

        // Return empty object for 204 No Content
        if (response.status === 204) return {};
        
        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

// UI Utilities
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    const color = type === 'success' ? '#10b981' : '#ef4444';
    
    toast.innerHTML = `
        <i class="fas ${icon}" style="color: ${color}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        if(toast.parentNode) toast.parentNode.removeChild(toast);
    }, 3500);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function getMatchColor(score) {
    if (score >= 80) return 'match-high';
    if (score >= 60) return 'match-med';
    return 'match-low';
}

function getPriorityBadge(priority) {
    if (priority === 'HIGH PRIORITY') return '<span class="badge priority-high"><i class="fas fa-fire mr-1"></i> High Priority</span>';
    if (priority === 'MEDIUM PRIORITY') return '<span class="badge priority-med"><i class="fas fa-bolt mr-1"></i> Med Priority</span>';
    return '<span class="badge priority-low"><i class="fas fa-bookmark mr-1"></i> Explore</span>';
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/frontend/login.html';
}

function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.href.includes('login.html') && !window.location.href.includes('register.html') && !window.location.href.endsWith('index.html') && !window.location.href.endsWith('/frontend/')) {
        window.location.href = '/frontend/login.html';
    }
}

// Run auth check
document.addEventListener('DOMContentLoaded', checkAuth);
