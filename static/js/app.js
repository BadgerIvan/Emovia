document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    const articlesBtn = document.getElementById('articles-btn');
    const homeBtn = document.getElementById('home-btn');
    const calendarBtn = document.getElementById('calendar-btn');
    const articlesScreen = document.getElementById('articles-screen');
    const mainScreen = document.getElementById('main-screen');
    const calendarScreen = document.getElementById('calendar-screen');
    
    const markMoodBtn = document.getElementById('mark-mood-btn');
    const moodModal = document.getElementById('mood-modal');
    const closeModal = document.getElementById('close-modal');
    const moodOptions = document.querySelectorAll('.mood-option');
    const todayForecast = document.getElementById('today-forecast');
    const moodCircle = document.getElementById('mood-circle');
    
    const currentTime = document.getElementById('current-time');

    const usernameDisplay = document.getElementById('username-display');
    const logoutBtn = document.getElementById('logout-btn');

    const articleModal = document.getElementById('article-modal');
    const closeArticleModal = document.getElementById('close-article-modal');
    const articleModalTitle = document.getElementById('article-modal-title');
    const articleModalContent = document.getElementById('article-modal-content');

    const notesModal = document.getElementById('notes-modal');
    const closeNotesModal = document.getElementById('close-notes-modal');
    const notesDate = document.getElementById('notes-date');
    const notesList = document.getElementById('notes-list');
    const newNote = document.getElementById('new-note');
    const addNoteBtn = document.getElementById('add-note-btn');
    
    updateTime();
    setInterval(updateTime, 60000);
    loadArticles();
    generateCalendar();
    updateMoodForecast();
    updateWeekDaysColors();
    
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
                    const dayOffset = index - today.getDay() + 1;
                    const date = new Date();
                    date.setDate(today.getDate() + dayOffset);
                    const dateStr = date.toISOString().split('T')[0];
                    
                    dayElem.className = '';
                    
                    if (moods[dateStr]) {
                        dayElem.classList.add(moods[dateStr]);
                    }
                    
                    if (dayOffset === 0) {
                        dayElem.classList.add('today');
                    }
                });
            });
    }
    
    function setActiveScreen(screen) {
        articlesScreen.classList.remove('active');
        mainScreen.classList.remove('active');
        calendarScreen.classList.remove('active');
        articlesBtn.classList.remove('active');
        homeBtn.classList.remove('active');
        calendarBtn.classList.remove('active');
        
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
                
                ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].forEach(day => {
                    const header = document.createElement('div');
                    header.className = 'calendar-header';
                    header.textContent = day;
                    calendar.appendChild(header);
                });
                
                for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
                    const empty = document.createElement('div');
                    empty.className = 'calendar-day empty';
                    calendar.appendChild(empty);
                }
                
                const moodMap = {};
                moods.forEach(m => {
                    const date = new Date(m.date);
                    if (date.getMonth() === month && date.getFullYear() === year) {
                        moodMap[date.getDate()] = m.mood;
                    }
                });
                
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
            updateWeekDaysColors(); 
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
                
                const moodCircle = document.getElementById('mood-circle');
                if (!moodCircle) {
                    const circle = document.createElement('div');
                    circle.id = 'mood-circle';
                    circle.className = `mood-circle ${data.forecast}`;
                    circle.textContent = data.message;
                    document.querySelector('.mood-forecast').prepend(circle);
                } else {
                    moodCircle.className = `mood-circle ${data.forecast}`;
                    moodCircle.textContent = data.message;
                }
            });
    }

    function showNotesForDate(day, month, year) {
        const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const formattedDate = `${day}.${month}.${year}`;
        
        notesDate.textContent = formattedDate;
        newNote.value = '';
        
        fetch(`/api/notes?date=${dateStr}`)
            .then(response => response.json())
            .then(notes => {
                notesList.innerHTML = '';
                
                if (notes.length === 0) {
                    notesList.innerHTML = '<p>Нет заметок на эту дату</p>';
                    return;
                }
                
                notes.forEach(note => {
                    const noteElement = document.createElement('div');
                    noteElement.className = 'note-item';
                    noteElement.innerHTML = `
                        <div class="note-date">${new Date(note.date).toLocaleDateString()}</div>
                        <div class="note-content">${note.content}</div>
                        <button class="delete-note" data-id="${note.id}">×</button>
                    `;
                    notesList.appendChild(noteElement);
                });
                
                document.querySelectorAll('.delete-note').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const noteId = this.getAttribute('data-id');
                        deleteNote(noteId);
                    });
                });
            });
        
        notesModal.classList.add('active');
    }
    
    function deleteNote(noteId) {
        fetch(`/api/notes/${noteId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const currentDate = notesDate.textContent.split('.');
                showNotesForDate(currentDate[0], currentDate[1], currentDate[2]);
            }
        });
    }
    
    function showDayDetails(day, month, year, mood) {
        showNotesForDate(day, month, year);
    }
    
    addNoteBtn.addEventListener('click', function() {
        const currentDate = notesDate.textContent.split('.');
        const dateStr = `${currentDate[2]}-${String(currentDate[1]).padStart(2, '0')}-${String(currentDate[0]).padStart(2, '0')}`;
        
        if (newNote.value.trim() === '') {
            alert('Заметка не может быть пустой');
            return;
        }
        
        fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                date: dateStr,
                content: newNote.value.trim()
            })
        })
        .then(response => response.json())
        .then(data => {
            newNote.value = '';
            showNotesForDate(currentDate[0], currentDate[1], currentDate[2]);
        });
    });
    
    closeNotesModal.addEventListener('click', function() {
        notesModal.classList.remove('active');
    });
});