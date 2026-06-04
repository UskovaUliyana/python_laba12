from flask import Flask, render_template_string, request
import re

app = Flask(__name__)

def check_password(password):
    score = 0
    tips = []
    
    length = len(password)
    
    if length > 32:
        tips.append(f"Длина {length} символов (рекомендуется не более 32)")
    
    if length >= 16:
        score += 3
    elif length >= 12:
        score += 2
    elif length >= 8:
        score += 1
    else:
        tips.append(f"Длина {length} символов (нужно минимум 8)")
    
    has_digit = bool(re.search(r'\d', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:?,.\\/|`~]', password))
    
    types_count = sum([has_digit, has_lower, has_upper, has_special])
    score += types_count
    
    if not has_digit:
        tips.append("Нет цифр")
    if not has_lower:
        tips.append("Нет строчных букв (a-z)")
    if not has_upper:
        tips.append("Нет заглавных букв (A-Z)")
    if not has_special:
        tips.append("Нет спецсимволов (!@#$%^&*)")
    
    if len(set(password)) >= length * 0.7:
        score += 1
    else:
        tips.append("Много повторяющихся символов")
    
    sequences = ['123456', '234567', '345678', '456789', '567890',
                 'abcdef', 'bcdefg', 'cdefgh', 'qwerty', 'asdfgh', 'zxcvbn']
    lower_pass = password.lower()
    has_sequence = False
    for seq in sequences:
        if seq in lower_pass:
            tips.append(f"Содержит простую последовательность '{seq[:4]}...'")
            has_sequence = True
            break
    if not has_sequence and length >= 8:
        score += 1
    
    common_passwords = ['123456', 'password', '12345678', 'qwerty', '12345', 
                        '123456789', '111111', '123123', 'abc123', 'password1',
                        '000000', '1234567890', 'qwerty123', 'admin', 'letmein']
    if password.lower() not in common_passwords:
        score += 1
    else:
        tips.append("Очень распространённый пароль")
    
    date_pattern = r'^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])(19|20)\d\d$'
    if not re.match(date_pattern, password):
        score += 1
    else:
        tips.append("Похоже на дату (легко подобрать)")
    
    half_len = length // 2
    if half_len >= 3 and password[:half_len] != password[half_len:half_len*2]:
        score += 1
    else:
        tips.append("Пароль состоит из повторяющихся блоков")
    
    dictionary = ['password', 'admin', 'user', 'login', 'welcome', 'master', 'hello']
    has_dict_word = False
    for word in dictionary:
        if word in password.lower():
            tips.append(f"Содержит простое слово '{word}'")
            has_dict_word = True
            break
    if not has_dict_word:
        score += 1
    
    if length >= 12 and types_count >= 3:
        score += 1
    
    if length >= 16 and types_count >= 4:
        score += 2
    
    MAX_SCORE = 16
    
    if score <= 6:
        level = "Слабый"
        color = "#e74c3c"
    elif score <= 11:
        level = "Средний"
        color = "#f39c12"
    elif score <= 15:
        level = "Хороший"
        color = "#2ecc71"
    else:
        level = "Сильный"
        color = "#27ae60"
    
    return score, level, color, tips, MAX_SCORE

html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Анализатор пароля</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; margin: 0; padding: 40px 20px; }
        .container { max-width: 500px; margin: 0 auto; }
        .card { background: white; border-radius: 16px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #333; margin: 0 0 25px 0; font-size: 26px; }
        input { width: 100%; padding: 12px 15px; font-size: 16px; border: 1px solid #ddd; border-radius: 10px; outline: none; box-sizing: border-box; }
        input:focus { border-color: #667eea; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 15px; }
        button:hover { background: #5a67d8; }
        .result { margin-top: 25px; padding-top: 20px; border-top: 1px solid #eee; }
        .result p { margin: 10px 0; }
        .score-bar { background: #e0e0e0; border-radius: 8px; height: 8px; margin: 15px 0; overflow: hidden; }
        .score-fill { height: 100%; border-radius: 8px; transition: width 0.3s; }
        .level-badge { display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: bold; margin: 10px 0; }
        ul { margin: 10px 0 0 20px; padding: 0; }
        li { margin: 6px 0; color: #e74c3c; }
        .good { text-align: center; padding: 10px; background: #e8f8f5; border-radius: 10px; color: #27ae60; font-weight: bold; }
        .text-center { text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>🔐 Анализатор пароля</h2>
            <form method="POST">
                <input type="text" name="password" placeholder="Введите пароль" value="{{ pwd }}" autocomplete="off">
                <button type="submit">Проверить</button>
            </form>
            
            {% if show %}
            <div class="result">
                <p><strong>Пароль:</strong> {{ pwd }}</p>
                <p><strong>Баллы:</strong> {{ score }}/{{ max_score }}</p>
                
                <div class="score-bar">
                    <div class="score-fill" style="width: {{ (score / max_score * 100)|round|int }}%; background: {{ color }}"></div>
                </div>
                
                <div class="text-center">
                    <span class="level-badge" style="background: {{ color }}20; color: {{ color }}">{{ level }}</span>
                </div>
                
                {% if tips %}
                    <p><strong>Что можно улучшить</strong></p>
                    <ul>
                    {% for t in tips %}
                        <li>{{ t }}</li>
                    {% endfor %}
                    </ul>
                {% else %}
                    <div class="good">✅ Отличный пароль! Надёжно защищён!</div>
                {% endif %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pwd = request.form['password']
        score, level, color, tips, max_score = check_password(pwd)
        return render_template_string(html, show=True, pwd=pwd, score=score, level=level, tips=tips, color=color, max_score=max_score)
    
    return render_template_string(html, show=False, pwd='')

if __name__ == '__main__':
    app.run(debug=True)