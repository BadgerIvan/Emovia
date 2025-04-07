from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from datetime import datetime, timedelta
import database
from werkzeug.security import generate_password_hash, check_password_hash
import re
import random

app = Flask(__name__)

app.secret_key = open("config.txt").readline()

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
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error="Заполните все поля")
        
        user_id = database.get_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('index'))
        
        return render_template('login.html', error="Неверное имя пользователя или пароль")
    
    return render_template('login.html', show_register=request.args.get('register'))

def is_password_strong(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            return render_template('login.html', error="Заполните все поля", show_register=True)
        
        if password != confirm_password:
            return render_template('login.html', error="Пароли не совпадают", show_register=True)
        
        if database.get_user(username):
            return render_template('login.html', error="Пользователь уже существует", show_register=True)
        
        if not is_password_strong(password):
            return render_template('login.html', error="Пароль должен содержать минимум 8 символов, включая заглавные буквы и цифры")
        
        user_id = database.create_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('index'))
        
        return render_template('login.html', error="Ошибка регистрации", show_register=True)
    
    return redirect(url_for('login', register=True))

@app.route('/api/user')
def get_user_info():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({
        "user_id": session['user_id'],
        "username": session['username']
    })

@app.route('/api/mood/week')
def get_week_moods():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    moods = database.get_week_moods(session['user_id'])
    return jsonify(moods)
    
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
    
    mood_weights = {
        'happy': 1,
        'good': 0.8,
        'neutral': 0.5,
        'bad': -0.8,
        'sad': -1
    }
    
    total_weight = 0
    for i, (date, mood) in enumerate(moods):
        weight = (len(moods) - i) / len(moods)
        total_weight += mood_weights.get(mood, 0) * weight
    
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
            "title": "Мне действительно грустно или…?", 
            "content": "Каждый из нас хотя бы раз в жизни испытывал чувство грусти. Оно может накрывать в самые неожиданные моменты — после просмотра фильма, при встрече с давним знакомым или просто без видимой причины. Но действительно ли мы можем однозначно сказать, что нам грустно, или существуют другие причины подавленного настроении?<br><br><b>Здоровье</b>: если уже длительное время вы пребываете в плохом настроении и негативные мысли так и лезут в голову, вспомните, когда в последний раз вы качественно высыпались, ели сытную и здоровую еду, пили больше одного стакана воды в день или бывали на свежем воздухе. Наше настроение сильно зависит от физического состояния. Поэтому, если объективных причин для апатии нет – уделите внимание именно здоровью тела. <br><br><b>Обесценивание позитивных эмоций</b>: люди склонны концентрироваться на проблемах, задачах на неделю, нереализованных планах, нежели на больших и маленьких победах, вдохновляющих мечтах. И тогда пролитый кофе на кофту утром или неудачный разговор с начальником могут испортить весь день. И вы уже не обращаете внимание на прекрасную погоду, не слышите комплимент от коллеги и не радуетесь встрече с любимым человеком. Посмотрите, сколько приятных мелочей происходит с вами каждый день! <br><br><b>Социальные связи</b>: возможно, причиной плохого настроения послужило внутреннее ощущение одиночества. Начните беседу с одногруппниками на интересующую вас тему, договоритесь о встрече с близким другом, позвоните родным и поделитесь своими переживаниями. Так вы напомните себе, что не одни и вам всегда есть, к кому обратиться."
        },
        {
            "id": 2, 
            "title": "Что такое ЛЕНЬ, и существует ли она вообще?", 
            "content": "Лень — это одно из наиболее известных и распространённых человеческих состояний, которое часто вызывает негативные ассоциации и порицания. Однако, что такое лень на самом деле? Существует ли она как явление, или же это лишь социальный конструкт, созданный для объяснения нашего с вами поведения?<br><br><b>Психологическое определение лени</b><br>Лень можно определить как состояние, при котором человек избегает активности или отказывается от выполнения задач, которые требуют усилий. Это состояние может проявляться как в физическом, так и в эмоциональном плане. Однако психологи выделяют несколько факторов, способствующих возникновению этого состояния. К ним относятся:<br>1. Мотивация: Часто лень возникает из-за отсутствия внутренней или внешней мотивации. Если человек не видит смысла в выполнении определенной задачи, его желание действовать уменьшается.<br>2. Страх и тревога: Неприятные эмоции, такие как страх перед неудачей или высокой ответственностью, могут провоцировать прокрастинацию и избегание задач. Часто мы боимся сделать что-то «неидеально», поэтому выбираем и вовсе не делать этого. <br>3. Физическое и психическое состояние: Усталость, как физическая, так и эмоциональная, может привести к временному состоянию лени. Если человек находится в состоянии стресса или депрессии, его активность может существенно снизиться. Организм показывает, что «ресурсов» почти не осталось и «бережет» вас от дополнительной активности.<br><br><b>Как же помочь себе?</b><br>1. Поиск мотивации – даже самые незначительные, на первый взгляд, действия могут принести весомые результаты в будущем. Когда наступает день запланированной тренировки, мыслите не так: «Сегодня я очень устану в зале и приду домой без сил», а так: «Сегодня я стану на шаг ближе к фигуре своей мечты и здоровому телу».<br>2. Ценность времени – люди как правило тратят на выполнение задачи ровно столько времени, сколько у них имеется. Вспомните, как студенты пишут доклад три недели или три дня с одним и тем же успехом. Поэтому старайтесь задавать себе четкие тайминги, чтобы дело, которое необходимо выполнить, не казалось чем-то бесконечным.<br>3. Отдых – не забывайте чередовать работу и отдых. Даже если после небольшого задания, вам необходимо больше времени на восстановление сил, чем другим – не отказывайте себе в этом. Так вы всегда будете знать, что как только задача будет выполнена, вы со спокойной душой сможете заняться более приятными вещами."
        },
        {
            "id": 3, 
            "title": "Позитивная психология: с чего начать?", 
            "content": "Позитивная психология изучает такие концепции, как счастье, удовлетворенность жизнью, любовь, доброта, надежда и оптимизм. Она охватывает множество тем, включая здоровье, благополучие, личностный рост и общение.<br><br>Если вас заинтересовала позитивная психология и вы хотите начать применять её принципы в своей жизни, вот несколько пунктов, которые помогут вам сделать первые шаги:<br><br><b>Изучите основы</b>: Начните с литературы по позитивной психологии. Книги Мартина Селигмана, \"Эмоциональный интеллект\" Дэниела Гоулмана и \"В поисках счастья\" Михая Чиксентмихайи являются отличными стартовыми точками.<br><br><b>Практикуйте благодарность</b>: Один из самых простых, но очень эффективных способов привнести позитив в свою жизнь — это практика благодарности. Каждый день записывайте три вещи, за которые вы благодарны. Это может быть что угодно: от теплой чашки кофе до добрых слов от друга. Эта практика помогает переносить фокус на положительные моменты вашей жизни.<br><br><b>Развивайте свои сильные стороны</b>: Позитивная психология утверждает, что изучение своих сильных сторон и их активное использование может значительно повысить качество жизни. Пройдите тесты на выявление сильных сторон, такие как VIA Survey of Character Strengths, и придерживайтесь их в повседневной жизни.<br><br><b>Ставьте реалистичные цели</b>: Стремление к достижению целей и мечт является важным критерием удовлетворенности жизнью. Установите небольшие, реалистичные и достижимые цели. Записывайте свои успехи и празднуйте достижения, даже если они кажутся незначительными."
        }
    ]
    return jsonify(articles)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
    
@app.route('/api/notes', methods=['GET', 'POST'])
def notes():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Missing content"}), 400
        
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        note_id = database.create_note(session['user_id'], date, data['content'])
        return jsonify({"status": "success", "note_id": note_id})
    
    date = request.args.get('date')
    notes = database.get_notes(session['user_id'], date)
    return jsonify(notes)

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    success = database.delete_note(note_id, session['user_id'])
    return jsonify({"status": "success" if success else "note not found"})

@app.route('/api/mood/stats')
def get_mood_stats():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    moods = database.get_moods(session['user_id'], days=30)
    
    stats = {
        'happy': 0,
        'good': 0,
        'neutral': 0,
        'bad': 0,
        'sad': 0
    }
    
    for date, mood in moods:
        if mood in stats:
            stats[mood] += 1
    
    return jsonify(stats)

QUOTES = {
    'happy': [
        "Счастье - это не что-то готовое. Оно зависит от ваших действий.",
        "Счастлив не тот, у кого все есть, а тот, кто умеет радоваться тому, что имеет."
    ],
    'good': [
        "Каждый день может быть хорошим, если правильно его начать.",
        "Хорошее настроение - это половина успеха."
    ],
    'neutral': [
        "Иногда нейтральное состояние - это просто передышка перед новыми свершениями.",
        "Спокойствие - это тоже результат."
    ],
    'bad': [
        "Даже в плохой день помни: завтра будет лучше.",
        "Трудности временны, но опыт, который они дают, останется с тобой навсегда."
    ],
    'sad': [
        "Грусть - это просто облако, которое закрывает солнце. Оно обязательно пройдет.",
        "Позволь себе погрустить, но не забывай, что впереди много хорошего."
    ]
}

@app.route('/api/quote')
def get_quote():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    forecast = request.args.get('forecast')
    if not forecast or forecast not in QUOTES:
        forecast = 'neutral'
    
    quote = random.choice(QUOTES[forecast])
    return jsonify({"quote": quote, "forecast": forecast})

if __name__ == '__main__':
    app.run(debug=True)