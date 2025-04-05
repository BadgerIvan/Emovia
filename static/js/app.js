document.addEventListener('DOMContentLoaded', function() {
    // Проверяем авторизацию
    checkAuth();
    
    // Navigation
    const articlesBtn = document.getElementById('articles-btn');
    const homeBtn = document.getElementById('home-btn');
    const calendarBtn = document.getElementById('calendar-btn');
    const articlesScreen = document.getElementById('articles-screen');
    const mainScreen = document.getElementById('main-screen');
    const calendarScreen = document.getElementById('calendar-screen');
    
    // Mood tracking
    const markMoodBtn = document.getElementById('mark-mood-btn');
    const moodModal = document.getElementById('mood-modal');
    const closeModal = document.getElementById('close-modal');
    const moodOptions = document.querySelectorAll('.mood-option');
    const todayForecast = document.getElementById('today-forecast');
    const moodCircle = document.getElementById('mood-circle');
    
    // Time display
    const currentTime = document.getElementById('current-time');

    const usernameDisplay = document.getElementById('username-display');
    const logoutBtn = document.getElementById('logout-btn');

    // Добавим обработчики для статей
    const articleModal = document.getElementById('article-modal');
    const closeArticleModal = document.getElementById('close-article-modal');
    const articleModalTitle = document.getElementById('article-modal-title');
    const articleModalContent = document.getElementById('article-modal-content');

    
    // Initialize
    updateTime();
    setInterval(updateTime, 60000);
    loadArticles();
    generateCalendar();
    updateMoodForecast();
    updateWeekDaysColors();
    
    // Navigation handlers
    articlesBtn.addEventListener('click', function() {
        setActiveScreen('articles');
    });
    
    homeBtn.addEventListener('click', function() {
        setActiveScreen('home');
        updateMoodForecast();
    });
    
    calendarBtn.addEventListener('click', function() {
        setActiveScreen('calendar');
        generateCalendar();
    });
    
    // Mood tracking handlers
    markMoodBtn.addEventListener('click', function() {
        moodModal.classList.add('active');
    });
    
    closeModal.addEventListener('click', function() {
        moodModal.classList.remove('active');
    });
    
    moodOptions.forEach(option => {
        option.addEventListener('click', function() {
            const mood = this.getAttribute('data-mood');
            recordMood(mood);
            moodModal.classList.remove('active');
        });
    });
    
    function checkAuth() {
        fetch('/api/user')
            .then(response => {
                if (!response.ok) {
                    window.location.href = '/login';
                }
                return response.json();
            })
            .then(data => {
                console.log('Logged in as:', data.username);
                usernameDisplay.textContent = data.username;
            })
            .catch(() => {
                window.location.href = '/login';
            });
    }

    logoutBtn.addEventListener('click', function() {
        fetch('/logout')
            .then(() => {
                window.location.href = '/login';
            });
    });

    function updateWeekDaysColors() {
        fetch('/api/mood/week')
            .then(response => response.json())
            .then(moods => {
                const weekDays = document.querySelectorAll('.week-days div');
                const daysOfWeek = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС'];
                const today = new Date();
                
                weekDays.forEach((dayElem, index) => {
                    // Определяем дату для каждого дня недели
                    const dayOffset = index - today.getDay() + 1;
                    const date = new Date();
                    date.setDate(today.getDate() + dayOffset);
                    const dateStr = date.toISOString().split('T')[0];
                    
                    // Сбрасываем классы
                    dayElem.className = '';
                    
                    // Добавляем класс настроения, если есть данные
                    if (moods[dateStr]) {
                        dayElem.classList.add(moods[dateStr]);
                    }
                    
                    // Выделяем сегодняшний день
                    if (dayOffset === 0) {
                        dayElem.classList.add('today');
                    }
                });
            });
    }
    
    function setActiveScreen(screen) {
        // Reset all screens and buttons
        articlesScreen.classList.remove('active');
        mainScreen.classList.remove('active');
        calendarScreen.classList.remove('active');
        articlesBtn.classList.remove('active');
        homeBtn.classList.remove('active');
        calendarBtn.classList.remove('active');
        
        // Activate selected screen and button
        if (screen === 'articles') {
            articlesScreen.classList.add('active');
            articlesBtn.classList.add('active');
        } else if (screen === 'home') {
            mainScreen.classList.add('active');
            homeBtn.classList.add('active');
        } else if (screen === 'calendar') {
            calendarScreen.classList.add('active');
            calendarBtn.classList.add('active');
        }
    }
    
    function updateTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        currentTime.textContent = `${hours}:${minutes}`;
    }
    
    function loadArticles() {
        fetch('/api/articles')
            .then(response => response.json())
            .then(articles => {
                const articlesList = document.getElementById('articles-list');
                articlesList.innerHTML = '';
                
                articles.forEach(article => {
                    const articleElement = document.createElement('div');
                    articleElement.className = 'article-item';
                    articleElement.innerHTML = `
                        <h3>${article.title}</h3>
                        <p>${article.excerpt || article.content.substring(0, 60)}...</p>
                    `;
                    
                    articleElement.addEventListener('click', function() {
                        showArticle(article);
                    });
                    
                    articlesList.appendChild(articleElement);
                });
            });
    }

    function showArticle(article) {
        articleModalTitle.textContent = article.title;
        articleModalContent.innerHTML = `<p>${article.content}</p>`;
        articleModal.classList.add('active');
    }
    
    // Добавим обработчик закрытия модального окна статьи
    closeArticleModal.addEventListener('click', function() {
        articleModal.classList.remove('active');
    });
    
    function generateCalendar() {
        fetch('/api/mood/history')
            .then(response => response.json())
            .then(moods => {
                const now = new Date();
                const year = now.getFullYear();
                const month = now.getMonth();
                const today = now.getDate();
                
                const firstDay = new Date(year, month, 1).getDay();
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                
                const calendar = document.getElementById('calendar');
                calendar.innerHTML = '';
                
                // Add day headers
                ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].forEach(day => {
                    const header = document.createElement('div');
                    header.className = 'calendar-header';
                    header.textContent = day;
                    calendar.appendChild(header);
                });
                
                // Add empty cells for days before the first day of the month
                for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
                    const empty = document.createElement('div');
                    empty.className = 'calendar-day empty';
                    calendar.appendChild(empty);
                }
                
                // Create a map of dates to moods for quick lookup
                const moodMap = {};
                moods.forEach(m => {
                    const date = new Date(m.date);
                    if (date.getMonth() === month && date.getFullYear() === year) {
                        moodMap[date.getDate()] = m.mood;
                    }
                });
                
                // Add days of the month
                for (let day = 1; day <= daysInMonth; day++) {
                    const dayElement = document.createElement('div');
                    dayElement.className = 'calendar-day';
                    dayElement.textContent = day;
                    
                    if (day === today) {
                        dayElement.classList.add('today');
                    }
                    
                    if (moodMap[day]) {
                        dayElement.classList.add(moodMap[day]);
                    }
                    
                    dayElement.addEventListener('click', function() {
                        showDayDetails(day, month + 1, year, moodMap[day]);
                    });
                    
                    calendar.appendChild(dayElement);
                }
            });
    }
    
    function showDayDetails(day, month, year, mood) {
        const moodTexts = {
            'happy': 'Счастлив',
            'good': 'Хорошее',
            'neutral': 'Нейтральное',
            'bad': 'Плохое',
            'sad': 'Грусть'
        };
        
        const message = mood 
            ? `Настроение ${day}.${month}.${year}: ${moodTexts[mood] || mood}`
            : `Нет данных о настроении за ${day}.${month}.${year}`;
        
        alert(message);
    }
    
    function recordMood(mood) {
        fetch('/api/mood', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mood: mood })
        })
        .then(response => response.json())
        .then(data => {
            updateMoodForecast();
            generateCalendar();
            updateWeekDaysColors(); // Добавьте эту строку
        })
        .catch(error => {
            console.error('Error recording mood:', error);
        });
    }
    
    function updateMoodForecast() {
        fetch('/api/mood/forecast')
            .then(response => response.json())
            .then(data => {
                todayForecast.textContent = data.message;
                
                // Update mood circle
                const moodCircle = document.getElementById('mood-circle');
                if (!moodCircle) {
                    // Create mood circle if it doesn't exist
                    const circle = document.createElement('div');
                    circle.id = 'mood-circle';
                    circle.className = `mood-circle ${data.forecast}`;
                    circle.textContent = data.message;
                    document.querySelector('.mood-forecast').prepend(circle);
                } else {
                    // Update existing circle
                    moodCircle.className = `mood-circle ${data.forecast}`;
                    moodCircle.textContent = data.message;
                }
            });
    }
});