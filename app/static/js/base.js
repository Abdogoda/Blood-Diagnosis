// Common JavaScript functionality for Blood Diagnosis System

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
        });
    }
});

// Flash Messages functionality
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function deleteCookie(name) {
    document.cookie = name + '=; Max-Age=0; path=/';
}

function showFlashMessage(type, message) {
    // Remove any existing flash messages
    const existingMessage = document.getElementById('flash-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const colors = {
        error: { bg: 'bg-red-50', border: 'border-red-500', text: 'text-red-800', subtext: 'text-red-700', icon: 'text-red-500', title: 'Error' },
        success: { bg: 'bg-green-50', border: 'border-green-500', text: 'text-green-800', subtext: 'text-green-700', icon: 'text-green-500', title: 'Success' },
        warning: { bg: 'bg-yellow-50', border: 'border-yellow-500', text: 'text-yellow-800', subtext: 'text-yellow-700', icon: 'text-yellow-500', title: 'Warning' },
        info: { bg: 'bg-blue-50', border: 'border-blue-500', text: 'text-blue-800', subtext: 'text-blue-700', icon: 'text-blue-500', title: 'Info' }
    };
    
    const color = colors[type] || colors.error;
    
    const messageDiv = document.createElement('div');
    messageDiv.id = 'flash-message';
    messageDiv.className = 'fixed top-20 right-4 z-[9999] max-w-md w-full animate-slide-up';
    messageDiv.innerHTML = `
        <div class="${color.bg} border-l-4 ${color.border} rounded-lg shadow-lg p-4">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-6 w-6 ${color.icon}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div class="ml-3 flex-1">
                    <h3 class="text-sm font-semibold ${color.text}">${color.title}</h3>
                    <p class="mt-1 text-sm ${color.subtext}">${message}</p>
                </div>
                <button onclick="closeMessage()" class="ml-4 flex-shrink-0 ${color.icon} hover:opacity-70 transition-colors">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(messageDiv);
    
    // Auto-close after 5 seconds
    setTimeout(() => {
        closeMessage();
    }, 5000);
}

function closeMessage() {
    const message = document.getElementById('flash-message');
    if (message) {
        message.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            message.remove();
        }, 300);
    }
}

// Check for flash message in cookie on page load
document.addEventListener('DOMContentLoaded', function() {
    const flashCookie = getCookie('flash_message');
    if (flashCookie) {
        try {
            const flashData = JSON.parse(decodeURIComponent(flashCookie));
            const messageType = flashData.type;
            const messageText = flashData.message;
            
            // Create and show the flash message
            showFlashMessage(messageType, messageText);
            
            // Delete the cookie after reading
            deleteCookie('flash_message');
        } catch (e) {
            console.error('Error parsing flash message:', e);
        }
    }

    // Auto-close existing static messages after 5 seconds
    const staticMessage = document.getElementById('flash-message');
    if (staticMessage) {
        setTimeout(() => {
            closeMessage();
        }, 5000);
    }
});
