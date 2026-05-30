from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'секретный_ключ_для_сессий_12345'

# Папка для хранения данных
DATA_FOLDER = 'data'
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')
QUEUES_FILE = os.path.join(DATA_FOLDER, 'queues.json')

# Преподаватели ФПМФиИТ
TEACHERS = {
    'arkhipova': 'Архипова Валентина Алексеевна (Экономика)',
    'gavrilov': 'Гаврилов Александр Олегович (История России)',
    'guryanova': 'Гурьянова Татьяна Юрьевна (Иностранный язык)',
    'emelyanova': 'Емельянова Татьяна Николаевна (Чувашский язык)',
    'dmitrieva': 'Дмитриева Ольга Юрьевна (Основы проектной деятельности)',
    'efimova': 'Ефимова Елена Геннадьевна (Линейная алгебра)',
    'ivanitsky': 'Иваницкий Александр Юрьевич (Численные методы)',
    'ignatieva': 'Игнатьева Елена Анатольевна (Иностранный язык)',
    'karpov': 'Карпов Алексей Петрович (Социология)',
    'kiselev': 'Киселев Михаил Витальевич (Интеллектуальный анализ данных)',
    'kuznetsov': 'Кузнецов Сергей Петрович (Дифференциальные уравнения)',
    'matveeva': 'Матвеева Алёна Николаевна (Аналитическая геометрия)',
    'mikhailova': 'Михайлова Наталия Алексеевна (Математический анализ/УМФ/ТФКП)',
    'mochalov': 'Мочалов Владимир Викторович (Математический анализ)',
    'pavlov': 'Павлов Вячеслав Валериевич (Безопасность жизнедеятельности)',
    'petrov': 'Петров Николай Аркадьевич (История России)',
    'platonov': 'Платонов Павел Сергеевич (Практикум на ЭВМ)',
    'rechnov': 'Речнов Алексей Владимирович (Информационные технологии)',
    'rukavishnikov': 'Рукавишников Денис Анатольевич (Физкультура)',
    'semenov': 'Семенов Сергей Анатольевич (Физкультура)',
    'troeshestova': 'Троешестова Дарья Анатольевна (Уравнения математической физики)',
    'tyunterov': 'Тюнтеров Евгений Сергеевич (Физика/Астрофизика)',
    'chuev': 'Чуев Василий Петрович (Базы данных)',
    'chueva': 'Чуева Эльвира Витальевна (Русский язык и деловые коммуникации)',
    'chuprunov': 'Чупрунов Алексей Николаевич (Теория вероятностей)',
    'shurbin': 'Шурбин Александр Кондратьевич (Молекулярная физика/Оптика)',
    'yaltaev': 'Ялтаев Дмитрий Анатольевич (Граждановедение)',
    'yardukhin': 'Ярдухин Алексей Константинович (Дифференциальные уравнения)'
}


# ========== РАБОТА С ФАЙЛАМИ ==========

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def load_queues():
    if os.path.exists(QUEUES_FILE):
        with open(QUEUES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    queues = {}
    for teacher_id in TEACHERS:
        queues[teacher_id] = []
    return queues


def save_queues(queues):
    with open(QUEUES_FILE, 'w', encoding='utf-8') as f:
        json.dump(queues, f, ensure_ascii=False, indent=2)


# ========== АВТОМАТИЧЕСКАЯ ОЧИСТКА ПРОСРОЧЕННЫХ ЗАПИСЕЙ ==========

def cleanup_expired_queues():
    queues = load_queues()
    today = datetime.now().strftime('%Y-%m-%d')
    changed = False

    for teacher_id in queues:
        original_length = len(queues[teacher_id])
        queues[teacher_id] = [s for s in queues[teacher_id] if s.get('date', '') >= today]
        if len(queues[teacher_id]) != original_length:
            changed = True

    if changed:
        save_queues(queues)
        print(f"[Очистка] Удалены просроченные записи на {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return queues


# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ШАБЛОНОВ ==========

@app.context_processor
def utility_processor():
    def now():
        return datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    return dict(now=now)


# ========== ФУНКЦИЯ ДЛЯ КРАСИВЫХ СООБЩЕНИЙ ==========

def show_message(title, message, type='error', icon=None, back_url=None, back_text='Назад', extra_url=None,
                 extra_text=None, queue_info=None):
    if icon is None:
        if type == 'error':
            icon = '❌'
        elif type == 'success':
            icon = '✅'
        elif type == 'warning':
            icon = '⚠️'
        else:
            icon = 'ℹ️'

    return render_template('message.html',
                           title=title,
                           message=message,
                           type=type,
                           icon=icon,
                           back_url=back_url,
                           back_text=back_text,
                           extra_url=extra_url,
                           extra_text=extra_text,
                           queue_info=queue_info)


# ========== МАРШРУТЫ ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ==========

@app.route('/')
def index():
    cleanup_expired_queues()
    return render_template('index.html', teachers=TEACHERS)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        group = request.form['group']
        subgroup = request.form['subgroup']

        users = load_users()

        if username in users:
            return show_message('Ошибка регистрации', 'Пользователь с таким логином уже существует!', 'error',
                                back_url='/register', back_text='Попробовать снова')

        users[username] = {
            'password': password,
            'fullname': fullname,
            'group': group,
            'subgroup': subgroup,
            'role': 'student'
        }
        save_users(users)

        return show_message('Регистрация успешна', 'Теперь вы можете войти в систему.', 'success', back_url='/login',
                            back_text='Войти')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        if username in users and users[username]['password'] == password:
            session['user'] = username
            session['role'] = users[username]['role']
            session['fullname'] = users[username]['fullname']

            if users[username]['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif users[username]['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))

        return show_message('Ошибка входа', 'Неверный логин или пароль.', 'error', back_url='/login',
                            back_text='Попробовать снова')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ========== МАРШРУТЫ ДЛЯ СТУДЕНТОВ ==========

@app.route('/student')
def student_dashboard():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    cleanup_expired_queues()

    users = load_users()
    user_info = users.get(session['user'], {})
    queues = load_queues()

    my_queues_list = []
    for teacher_id, queue in queues.items():
        for i, student in enumerate(queue):
            if student['username'] == session['user']:
                my_queues_list.append({
                    'teacher_id': teacher_id,
                    'teacher_name': TEACHERS.get(teacher_id, teacher_id),
                    'position': i + 1,
                    'date': student.get('date', 'Дата не указана'),
                    'time': student.get('time', '')
                })
                break

    today = datetime.now().strftime('%Y-%m-%d')

    return render_template('dashboard.html',
                           user=session['user'],
                           fullname=session['fullname'],
                           group=user_info.get('group', ''),
                           subgroup=user_info.get('subgroup', ''),
                           my_queues=my_queues_list,
                           teachers=TEACHERS,
                           today=today)


@app.route('/join_queue/<teacher_id>')
def join_queue(teacher_id):
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    if teacher_id not in TEACHERS:
        return show_message('Преподаватель не найден', 'Такого преподавателя не существует в системе.', 'error',
                            back_url='/student', back_text='Вернуться')

    selected_date = request.args.get('date', '')

    if not selected_date:
        return show_message('Дата не выбрана', 'Пожалуйста, выберите дату сдачи лабораторной работы.', 'warning',
                            back_url='/student', back_text='Вернуться')

    today = datetime.now().strftime('%Y-%m-%d')
    if selected_date < today:
        return show_message('Некорректная дата',
                            f'Нельзя записаться на прошедшую дату ({selected_date}).<br>Выберите сегодняшнюю или будущую дату.',
                            'warning', back_url='/student', back_text='Вернуться')

    queues = load_queues()
    queue = queues.get(teacher_id, [])

    # Проверяем, есть ли уже запись к этому преподавателю
    for student in queue:
        if student['username'] == session['user']:
            position = queue.index(student) + 1
            queue_info = {
                'teacher_name': TEACHERS.get(teacher_id, teacher_id),
                'date': student.get('date', 'Не указана'),
                'position': position
            }
            return show_message('Вы уже записаны!',
                                f'Вы уже находитесь в очереди к преподавателю <strong>{TEACHERS[teacher_id]}</strong>.<br><br>Чтобы записаться на другую дату, сначала выйдите из текущей очереди.',
                                'warning',
                                back_url='/student',
                                back_text='В личный кабинет',
                                queue_info=queue_info)

    users = load_users()
    user_info = users.get(session['user'], {})

    queue.append({
        'username': session['user'],
        'fullname': session['fullname'],
        'group': user_info.get('group', ''),
        'subgroup': user_info.get('subgroup', ''),
        'date': selected_date,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    queues[teacher_id] = queue
    save_queues(queues)

    return show_message('✅ Запись успешно создана!',
                        f'Вы записаны к преподавателю <strong>{TEACHERS[teacher_id]}</strong> на <strong>{selected_date}</strong>.<br><br>Следите за своей позицией в личном кабинете.',
                        'success',
                        back_url='/student',
                        back_text='В личный кабинет')


@app.route('/leave_specific_queue/<teacher_id>')
def leave_specific_queue(teacher_id):
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    selected_date = request.args.get('date', '')

    queues = load_queues()
    queue = queues.get(teacher_id, [])

    if selected_date:
        queues[teacher_id] = [s for s in queue if
                              not (s['username'] == session['user'] and s.get('date', '') == selected_date)]
    else:
        queues[teacher_id] = [s for s in queue if s['username'] != session['user']]

    save_queues(queues)

    return redirect(url_for('student_dashboard'))


# ========== МАРШРУТЫ ДЛЯ ПРЕПОДАВАТЕЛЕЙ ==========

@app.route('/teacher')
def teacher_dashboard():
    if 'user' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))

    cleanup_expired_queues()

    queues = load_queues()

    filter_group = request.args.get('group', '')
    filter_subgroup = request.args.get('subgroup', '')
    filter_date = request.args.get('date', '')

    queues_data = {}
    for teacher_id, queue in queues.items():
        filtered_queue = queue.copy()
        if filter_group:
            filtered_queue = [s for s in filtered_queue if s.get('group', '') == filter_group]
        if filter_subgroup:
            filtered_queue = [s for s in filtered_queue if s.get('subgroup', '') == filter_subgroup]
        if filter_date:
            filtered_queue = [s for s in filtered_queue if s.get('date', '') == filter_date]

        queues_data[teacher_id] = {
            'name': TEACHERS.get(teacher_id, teacher_id),
            'queue': queue,
            'filtered_queue': filtered_queue,
            'count': len(queue),
            'filtered_count': len(filtered_queue)
        }

    return render_template('teacher.html',
                           queues=queues_data,
                           teachers=TEACHERS,
                           filter_group=filter_group,
                           filter_subgroup=filter_subgroup,
                           filter_date=filter_date)


@app.route('/call_next/<teacher_id>')
def call_next(teacher_id):
    if 'user' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))

    queues = load_queues()
    queue = queues.get(teacher_id, [])

    if queue:
        next_student = queue.pop(0)
        queues[teacher_id] = queue
        save_queues(queues)
        return show_message('Вызов студента',
                            f'Вызван студент: <strong>{next_student["fullname"]}</strong><br>Группа: {next_student["group"]} | Подгруппа: {next_student["subgroup"]}<br>Дата сдачи: {next_student["date"]}',
                            'success', back_url='/teacher', back_text='Вернуться к очередям')

    return show_message('Очередь пуста', 'Нет студентов в очереди для вызова.', 'warning', back_url='/teacher',
                        back_text='Вернуться')


@app.route('/queue/<teacher_id>')
def view_queue(teacher_id):
    cleanup_expired_queues()

    queues = load_queues()
    queue = queues.get(teacher_id, [])

    return render_template('queue.html',
                           teacher_id=teacher_id,
                           teacher_name=TEACHERS.get(teacher_id, teacher_id),
                           queue=queue)


# ========== МАРШРУТЫ ДЛЯ ПЕЧАТИ ==========

@app.route('/print_public_queue/<teacher_id>')
def print_public_queue(teacher_id):
    if teacher_id not in TEACHERS:
        return 'Преподаватель не найден!'

    queues = load_queues()
    queue = queues.get(teacher_id, [])

    filter_group = request.args.get('group', '')
    filter_subgroup = request.args.get('subgroup', '')
    filter_date = request.args.get('date', '')

    filtered_queue = queue.copy()
    if filter_group:
        filtered_queue = [s for s in filtered_queue if s.get('group', '') == filter_group]
    if filter_subgroup:
        filtered_queue = [s for s in filtered_queue if s.get('subgroup', '') == filter_subgroup]
    if filter_date:
        filtered_queue = [s for s in filtered_queue if s.get('date', '') == filter_date]

    return render_template('print_public_queue.html',
                           teacher_name=TEACHERS.get(teacher_id, teacher_id),
                           teacher_id=teacher_id,
                           queue=filtered_queue,
                           filter_group=filter_group,
                           filter_subgroup=filter_subgroup,
                           filter_date=filter_date,
                           total_count=len(filtered_queue))


@app.route('/print_all_queues')
def print_all_queues():
    if 'user' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))

    cleanup_expired_queues()
    queues = load_queues()

    all_queues = {}
    for teacher_id, queue in queues.items():
        if queue:
            all_queues[teacher_id] = {
                'name': TEACHERS.get(teacher_id, teacher_id),
                'queue': queue,
                'count': len(queue)
            }

    return render_template('print_all_queues.html',
                           queues=all_queues,
                           print_date=datetime.now().strftime('%d.%m.%Y %H:%M'))


# ========== МАРШРУТЫ ДЛЯ АДМИНИСТРАТОРА ==========

@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')


@app.route('/admin/do_login', methods=['POST'])
def admin_do_login():
    username = request.form['username']
    password = request.form['password']

    users = load_users()

    if username in users and users[username]['password'] == password and users[username].get('role') == 'admin':
        session['user'] = username
        session['role'] = 'admin'
        session['fullname'] = users[username]['fullname']
        return redirect(url_for('admin_dashboard'))

    return show_message('Ошибка входа', 'Неверный логин или пароль администратора.', 'error', back_url='/admin/login',
                        back_text='Назад')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    users = load_users()
    queues = load_queues()

    stats = {
        'total_students': len([u for u in users.values() if u.get('role') == 'student']),
        'total_teachers': len([u for u in users.values() if u.get('role') == 'teacher']),
        'total_queues': 0,
        'active_queues': 0
    }

    for teacher_id, queue in queues.items():
        stats['total_queues'] += len(queue)
        if len(queue) > 0:
            stats['active_queues'] += 1

    return render_template('admin_dashboard.html', stats=stats, admin_name=session.get('fullname'))


@app.route('/admin/users')
def admin_users():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    users = load_users()

    students = []
    teachers = []

    for username, user_data in users.items():
        if user_data.get('role') == 'student':
            queues = load_queues()
            has_active_queues = False
            active_queues_info = []
            for teacher_id, queue in queues.items():
                for student in queue:
                    if student['username'] == username:
                        has_active_queues = True
                        active_queues_info.append({
                            'teacher': TEACHERS.get(teacher_id, teacher_id),
                            'date': student.get('date', 'не указана'),
                            'position': queue.index(student) + 1
                        })

            students.append({
                'username': username,
                'fullname': user_data.get('fullname', ''),
                'group': user_data.get('group', ''),
                'subgroup': user_data.get('subgroup', ''),
                'has_active_queues': has_active_queues,
                'active_queues': active_queues_info
            })
        elif user_data.get('role') == 'teacher':
            teachers.append({
                'username': username,
                'fullname': user_data.get('fullname', ''),
                'role': user_data.get('role', 'teacher')
            })

    return render_template('admin_users.html', students=students, teachers=teachers)


@app.route('/admin/delete_user/<username>')
def admin_delete_user(username):
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    users = load_users()

    if username not in users:
        return show_message('Ошибка', 'Пользователь не найден!', 'error', back_url='/admin/users', back_text='Назад')

    if users[username].get('role') == 'admin':
        return show_message('Ошибка', 'Нельзя удалить администратора!', 'error', back_url='/admin/users',
                            back_text='Назад')

    queues = load_queues()
    for teacher_id in queues:
        queues[teacher_id] = [s for s in queues[teacher_id] if s['username'] != username]
    save_queues(queues)

    fullname = users[username].get('fullname', username)
    del users[username]
    save_users(users)

    return show_message('✅ Успешно', f'Пользователь "{fullname}" удалён из системы.', 'success',
                        back_url='/admin/users', back_text='Назад')


@app.route('/admin/clear_all_students')
def admin_clear_all_students():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    users = load_users()
    queues = load_queues()

    students_to_delete = [username for username, data in users.items() if data.get('role') == 'student']

    if not students_to_delete:
        return show_message('Информация', 'Нет студентов для удаления.', 'info', back_url='/admin/users',
                            back_text='Назад')

    for teacher_id in queues:
        queues[teacher_id] = [s for s in queues[teacher_id] if s['username'] not in students_to_delete]
    save_queues(queues)

    users = {username: data for username, data in users.items() if data.get('role') != 'student'}
    save_users(users)

    return show_message('✅ Успешно', f'Удалено {len(students_to_delete)} студентов и все их записи.', 'success',
                        back_url='/admin/users', back_text='Назад')


@app.route('/admin/clear_graduated/<group>')
def admin_clear_graduated(group):
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    users = load_users()
    queues = load_queues()

    students_to_delete = [username for username, data in users.items()
                          if data.get('role') == 'student' and data.get('group') == group]

    if not students_to_delete:
        return show_message('Информация', f'Нет студентов в группе {group}.', 'info', back_url='/admin/users',
                            back_text='Назад')

    for teacher_id in queues:
        queues[teacher_id] = [s for s in queues[teacher_id] if s['username'] not in students_to_delete]
    save_queues(queues)

    users = {username: data for username, data in users.items()
             if not (data.get('role') == 'student' and data.get('group') == group)}
    save_users(users)

    return show_message('✅ Успешно', f'Удалено {len(students_to_delete)} студентов из группы {group}.', 'success',
                        back_url='/admin/users', back_text='Назад')


# ========== ЗАПУСК ПРИЛОЖЕНИЯ ==========

if __name__ == '__main__':
    users = load_users()
    if not users:
        # Создаём преподавателя
        users['teacher1'] = {
            'password': '123',
            'fullname': 'Преподаватель',
            'group': '',
            'subgroup': '',
            'role': 'teacher'
        }
        # Создаём администратора
        users['admin'] = {
            'password': 'admin123',
            'fullname': 'Администратор системы',
            'group': '',
            'subgroup': '',
            'role': 'admin'
        }
        save_users(users)

    app.run(debug=True)