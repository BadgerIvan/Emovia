from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from datetime import datetime, timedelta
import database

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # В продакшене используйте настоящий секретный ключ

# Инициализация БД при старте
database.init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            user_id = database.get_user(username)
            if not user_id:
                user_id = database.create_user(username)
            if user_id:
                session['user_id'] = user_id
                session['username'] = username
                return redirect(url_for('index'))
        return render_template('login.html', error="Неверное имя пользователя")
    return render_template('login.html')

@app.route('/api/user')
def get_user_info():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({
        "user_id": session['user_id'],
        "username": session['username']
    })

@app.route('/api/mood', methods=['POST'])
def record_mood():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    if not data or 'mood' not in data:
        return jsonify({"error": "Missing mood data"}), 400
    
    today = datetime.now().strftime('%Y-%m-%d')
    database.record_mood(session['user_id'], today, data['mood'])
    
    return jsonify({
        "status": "success",
        "date": today,
        "mood": data['mood']
    })

@app.route('/api/mood/history')
def get_mood_history():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    moods = database.get_moods(session['user_id'], days=10)
    return jsonify([{"date": m[0], "mood": m[1]} for m in moods])

@app.route('/api/mood/forecast')
def get_mood_forecast():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    moods = database.get_moods(session['user_id'], days=10)
    if not moods:
        return jsonify({"forecast": "neutral", "message": "Недостаточно данных для прогноза"})
    
    # Веса для разных настроений (чем новее, тем больше вес)
    mood_weights = {
        'happy': 1,
        'good': 0.8,
        'neutral': 0.5,
        'bad': -0.8,
        'sad': -1
    }
    
    total_weight = 0
    for i, (date, mood) in enumerate(moods):
        # Чем новее запись, тем больше вес (линейно убывает)
        weight = (len(moods) - i) / len(moods)
        total_weight += mood_weights.get(mood, 0) * weight
    
    # Определяем прогноз на основе общего веса
    if total_weight > 0.6:
        forecast = "happy"
        message = "Отличное настроение"
    elif total_weight > 0.2:
        forecast = "good"
        message = "Хорошее настроение"
    elif total_weight > -0.2:
        forecast = "neutral"
        message = "Нейтральное настроение"
    elif total_weight > -0.6:
        forecast = "bad"
        message = "Плохое настроение"
    else:
        forecast = "sad"
        message = "Грустное настроение"
    
    return jsonify({
        "forecast": forecast,
        "message": message,
        "mood_data": [{"date": m[0], "mood": m[1]} for m in moods]
    })

@app.route('/api/articles')
def get_articles():
    articles = [
        {
            "id": 1, 
            "title": "Как справляться со стрессом", 
            "content": "Стресс - это естественная реакция организма на сложные ситуации. Вот несколько способов справиться с ним:<br><br>1. Глубокое дыхание - медленные вдохи и выдохи помогают успокоиться.<br>2. Физическая активность - даже короткая прогулка может снизить уровень стресса.<br>3. Планирование - разбивайте большие задачи на маленькие шаги.<br>4. Отдых - не забывайте делать перерывы в работе.<br>5. Общение - разговор с близкими может помочь взглянуть на ситуацию по-новому."
        },
        {
            "id": 2, 
            "title": "10 способов улучшить настроение", 
            "content": "1. Послушайте любимую музыку.<br>2. Выйдите на прогулку на свежий воздух.<br>3. Пообщайтесь с друзьями.<br>4. Займитесь творчеством.<br>5. Вспомните приятные моменты из жизни.<br>6. Сделайте что-то приятное для другого человека.<br>7. Посмотрите комедию или смешные видео.<br>8. Займитесь спортом.<br>9. Потанцуйте.<br>10. Выспитесь - качественный сон творит чудеса."
        },
        {
            "id": 3, 
            "title": "Важность эмоционального интеллекта", 
            "content": "Эмоциональный интеллект (EQ) - это способность понимать и управлять своими эмоциями и эмоциями других людей. Вот почему он важен:<br><br>- Помогает в построении отношений<br>- Улучшает коммуникацию<br>- Способствует лидерским качествам<br>- Помогает в разрешении конфликтов<br>- Уменьшает уровень стресса<br>- Повышает эмпатию<br><br>Развивать EQ можно через саморефлексию, активное слушание и практику осознанности."
        }
    ]
    return jsonify(articles)

# Уже есть маршрут для выхода, просто убедимся, что он правильный
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True)