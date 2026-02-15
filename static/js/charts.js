let activityChart, entriesChart, moodChart;

document.addEventListener('DOMContentLoaded', async function() {
    const savedUser = localStorage.getItem('mindbox_user');
    if (!savedUser) {
        window.location.href = '/login';
        return;
    }

    const user = JSON.parse(savedUser);
    await loadDetailedStats(user.id);
});

async function loadDetailedStats(userId) {
    try {
        const response = await fetch(`/api/stats/${userId}`);
        const result = await response.json();
        
        if (result.success) {
            updateDetailedStats(result.stats);
        }

        const activityResponse = await fetch(`/api/stats/${userId}/activity?days=30`);
        const activityResult = await activityResponse.json();
        
        if (activityResult.success) {
            createActivityChart(activityResult.activity);
        }

        const storageResponse = await fetch(`/api/stats/${userId}/storage`);
        const storageResult = await storageResponse.json();
        
        if (storageResult.success) {
            document.getElementById('storageSize').textContent = storageResult.storage.used_formatted;
        }

        const achievementsResponse = await fetch(`/api/stats/${userId}/achievements`);
        const achievementsResult = await achievementsResponse.json();
        
        if (achievementsResult.success) {
            updateAllAchievements(achievementsResult.achievements);
        }
    } catch (error) {
        console.error('Error loading detailed stats:', error);
    }
}

function updateDetailedStats(stats) {
    const basic = stats.basic;
    const byType = stats.entries_by_type;

    document.getElementById('productivityScore').textContent = stats.productivity_score;
    document.getElementById('totalEntriesStats').textContent = basic.total_entries;
    document.getElementById('textCount').textContent = byType.text || 0;
    document.getElementById('checklistCount').textContent = byType.checklist || 0;
    document.getElementById('highlightCount').textContent = byType.highlight || 0;
    document.getElementById('problemCount').textContent = byType.problem || 0;
    document.getElementById('achievementCount').textContent = byType.achievement || 0;

    createEntriesTypeChart(byType);
    createMoodChart(stats.mood_distribution);
}

function createActivityChart(activity) {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    const dates = Object.keys(activity).slice(-30);
    const values = Object.values(activity).slice(-30);

    if (activityChart) activityChart.destroy();

    activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates.map(d => d.slice(5)),
            datasets: [{
                label: 'عدد المدخلات',
                data: values,
                borderColor: '#9d4edd',
                backgroundColor: 'rgba(157, 78, 221, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#c0b0d0'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#c0b0d0',
                        maxRotation: 45
                    }
                }
            }
        }
    });
}

function createEntriesTypeChart(byType) {
    const ctx = document.getElementById('entriesTypeChart').getContext('2d');

    const data = [
        byType.text || 0,
        byType.checklist || 0,
        byType.highlight || 0,
        byType.problem || 0,
        byType.achievement || 0
    ];

    if (entriesChart) entriesChart.destroy();

    entriesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['نص', 'قائمة', 'مهم', 'مشكلة', 'إنجاز'],
            datasets: [{
                data: data,
                backgroundColor: [
                    '#9d4edd',
                    '#c77dff',
                    '#ff9e00',
                    '#f85f5f',
                    '#00b8a9'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#c0b0d0'
                    }
                }
            }
        }
    });
}

function createMoodChart(moodDist) {
    const ctx = document.getElementById('moodPieChart').getContext('2d');

    const data = [
        moodDist['😊'] || 0,
        moodDist['😐'] || 0,
        moodDist['😕'] || 0,
        (moodDist['🤩'] || 0) + (moodDist['🥳'] || 0),
        (moodDist['😴'] || 0) + (moodDist['🤔'] || 0) + (moodDist['😎'] || 0)
    ];

    if (moodChart) moodChart.destroy();

    moodChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['سعيد', 'محايد', 'حزين', 'متحمس', 'آخر'],
            datasets: [{
                data: data,
                backgroundColor: [
                    '#9d4edd',
                    '#c77dff',
                    '#7b2cbf',
                    '#ff9e00',
                    '#00b8a9'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#c0b0d0'
                    }
                }
            }
        }
    });
}

function updateAllAchievements(achievements) {
    const grid = document.getElementById('allAchievementsGrid');
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