let currentUser = null;

document.addEventListener('DOMContentLoaded', async function() {
    const savedUser = localStorage.getItem('mindbox_user');
    if (!savedUser) {
        window.location.href = '/login';
        return;
    }

    currentUser = JSON.parse(savedUser);
    loadUserData();
    loadStats();
});

document.getElementById('avatarInput').addEventListener('change', async function(e) {
    if (!e.target.files || !e.target.files[0]) return;

    const formData = new FormData();
    formData.append('avatar', e.target.files[0]);

    try {
        const response = await fetch(`/api/auth/user/${currentUser.id}/avatar`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.success) {
            document.getElementById('avatarImg').src = result.avatar + '?t=' + Date.now();
            currentUser.avatar = result.avatar;
            localStorage.setItem('mindbox_user', JSON.stringify(currentUser));
        }
    } catch (error) {
        console.error('Error uploading avatar:', error);
    }
});

document.getElementById('logoutBtn').addEventListener('click', function() {
    localStorage.removeItem('mindbox_user');
    window.location.href = '/login';
});

async function loadUserData() {
    document.getElementById('userName').textContent = `${currentUser.first_name} ${currentUser.last_name}`;
    document.getElementById('userEmail').textContent = currentUser.email;
    
    if (currentUser.avatar && currentUser.avatar !== '/public/default-avatar.png') {
        document.getElementById('avatarImg').src = currentUser.avatar;
    }
}

async function loadStats() {
    try {
        const response = await fetch(`/api/stats/${currentUser.id}`);
        const result = await response.json();
        
        if (result.success) {
            updateStats(result.stats);
        }

        const storageResponse = await fetch(`/api/stats/${currentUser.id}/storage`);
        const storageResult = await storageResponse.json();
        
        if (storageResult.success) {
            updateStorage(storageResult.storage);
        }

        const achievementsResponse = await fetch(`/api/stats/${currentUser.id}/achievements`);
        const achievementsResult = await achievementsResponse.json();
        
        if (achievementsResult.success) {
            updateAchievements(achievementsResult.achievements);
        }

        const productivityResponse = await fetch(`/api/stats/${currentUser.id}/productivity`);
        const productivityResult = await productivityResponse.json();
        
        if (productivityResult.success) {
            updateProductivity(productivityResult.productivity);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStats(stats) {
    const basic = stats.basic;
    
    document.getElementById('totalEntries').textContent = basic.total_entries;
    document.getElementById('totalFiles').textContent = basic.total_files;
    document.getElementById('completedTasks').textContent = basic.completed_tasks;
    document.getElementById('completionRate').textContent = basic.task_completion_rate + '%';
    document.getElementById('accountAge').textContent = basic.account_age + ' يوم';
    document.getElementById('lastActive').textContent = basic.last_active;

    const moodDist = stats.mood_distribution;
    document.getElementById('moodHappy').textContent = moodDist['😊'] || 0;
    document.getElementById('moodNeutral').textContent = moodDist['😐'] || 0;
    document.getElementById('moodSad').textContent = moodDist['😕'] || 0;
    document.getElementById('moodExcited').textContent = (moodDist['🤩'] || 0) + (moodDist['🥳'] || 0);

    const total = Object.values(moodDist).reduce((a, b) => a + b, 0) || 1;
    document.querySelectorAll('.mood-item').forEach((item, index) => {
        const fill = item.querySelector('.mood-fill');
        if (fill) {
            let count = 0;
            if (index === 0) count = moodDist['😊'] || 0;
            if (index === 1) count = moodDist['😐'] || 0;
            if (index === 2) count = moodDist['😕'] || 0;
            if (index === 3) count = (moodDist['🤩'] || 0) + (moodDist['🥳'] || 0);
            fill.style.width = (count / total * 100) + '%';
        }
    });
}

function updateStorage(storage) {
    document.getElementById('storageFill').style.width = storage.percentage + '%';
    document.getElementById('storageUsed').textContent = storage.used_formatted;
}

function updateAchievements(achievements) {
    const grid = document.getElementById('achievementsGrid');
    grid.innerHTML = '';

    if (achievements.length === 0) {
        grid.innerHTML = `
            <div class="achievement-card locked" style="grid-column: span 2">
                <div class="achievement-icon">🎯</div>
                <div class="achievement-name">ابدأ رحلتك</div>
                <div class="achievement-desc">أنشئ أول ملف وأضف مدخلات</div>
            </div>
        `;
        return;
    }

    achievements.forEach(achievement => {
        const card = document.createElement('div');
        card.className = 'achievement-card';
        card.innerHTML = `
            <div class="achievement-icon">${achievement.icon}</div>
            <div class="achievement-name">${achievement.name}</div>
            <div class="achievement-desc">${achievement.description}</div>
        `;
        grid.appendChild(card);
    });
}

function updateProductivity(productivity) {
    document.getElementById('productivityScore').textContent = productivity.score;
}