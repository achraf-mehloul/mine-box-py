class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.checkSavedUser();
        this.attachEvents();
    }

    checkSavedUser() {
        const savedUser = localStorage.getItem('mindbox_user');
        if (savedUser) {
            this.currentUser = JSON.parse(savedUser);
            this.updateUIForLoggedIn();
        }
    }

    attachEvents() {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const email = document.getElementById('email')?.value;
        const password = document.getElementById('password')?.value;

        if (!email || !password) {
            this.showNotification('الرجاء إدخال البريد الإلكتروني وكلمة المرور', 'error');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const result = await response.json();

            if (result.success) {
                this.currentUser = result.user;
                localStorage.setItem('mindbox_user', JSON.stringify(result.user));
                this.showNotification('تم تسجيل الدخول بنجاح', 'success');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                this.showNotification(result.error || 'فشل تسجيل الدخول', 'error');
            }
        } catch (error) {
            this.showNotification('حدث خطأ في الاتصال بالخادم', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        
        const firstName = formData.get('first_name');
        const lastName = formData.get('last_name');
        const email = formData.get('email');
        const phone = formData.get('phone');

        if (!firstName || !lastName || !email || !phone) {
            this.showNotification('الرجاء ملء جميع الحقول المطلوبة', 'error');
            return;
        }

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentUser = result.user;
                localStorage.setItem('mindbox_user', JSON.stringify(result.user));
                this.showNotification('تم التسجيل بنجاح', 'success');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                this.showNotification(result.error || 'فشل التسجيل', 'error');
            }
        } catch (error) {
            this.showNotification('حدث خطأ في الاتصال بالخادم', 'error');
        }
    }

    handleLogout() {
        localStorage.removeItem('mindbox_user');
        this.currentUser = null;
        this.showNotification('تم تسجيل الخروج بنجاح', 'info');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1000);
    }

    updateUIForLoggedIn() {
        const loginElements = document.querySelectorAll('.auth-required');
        const guestElements = document.querySelectorAll('.guest-only');
        
        loginElements.forEach(el => el.style.display = 'block');
        guestElements.forEach(el => el.style.display = 'none');
        
        const userElements = document.querySelectorAll('.user-name');
        userElements.forEach(el => {
            if (this.currentUser) {
                el.textContent = `${this.currentUser.first_name} ${this.currentUser.last_name}`;
            }
        });

        const avatarElements = document.querySelectorAll('.user-avatar');
        avatarElements.forEach(el => {
            if (this.currentUser && this.currentUser.avatar) {
                el.src = this.currentUser.avatar;
            }
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isAuthenticated() {
        return !!this.currentUser;
    }

    async updateProfile(updates) {
        if (!this.currentUser) return false;

        try {
            const response = await fetch(`/api/auth/user/${this.currentUser.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });

            const result = await response.json();

            if (result.success) {
                this.currentUser = { ...this.currentUser, ...updates };
                localStorage.setItem('mindbox_user', JSON.stringify(this.currentUser));
                this.updateUIForLoggedIn();
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async uploadAvatar(file) {
        if (!this.currentUser) return false;

        const formData = new FormData();
        formData.append('avatar', file);

        try {
            const response = await fetch(`/api/auth/user/${this.currentUser.id}/avatar`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentUser.avatar = result.avatar;
                localStorage.setItem('mindbox_user', JSON.stringify(this.currentUser));
                this.updateUIForLoggedIn();
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }
}

const authStyles = document.createElement('style');
authStyles.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(-100px);
        background: rgba(26, 0, 46, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(157, 78, 221, 0.3);
        border-radius: 40px;
        padding: 12px 24px;
        z-index: 9999;
        transition: transform 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }

    .notification.show {
        transform: translateX(-50%) translateY(0);
    }

    .notification-success {
        border-right: 4px solid #00b8a9;
    }

    .notification-error {
        border-right: 4px solid #f85f5f;
    }

    .notification-info {
        border-right: 4px solid #9d4edd;
    }

    .notification-message {
        color: white;
        font-size: 14px;
    }

    .auth-required, .guest-only {
        transition: all 0.3s;
    }
`;

document.head.appendChild(authStyles);

const authManager = new AuthManager();
window.authManager = authManager;