import sqlite3
import hashlib
import datetime

class Database:
    def __init__(self, db_path: str = "database.db"):
        # Инициализация соединения с базой данных
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Позволяет обращаться к столбцам по имени
        self.initialize()

    # --- Вспомогательные методы работы с БД ---
    def _execute(self, query, params=(), fetch=False, many=False):
        """
        Универсальный метод для выполнения SQL-запросов.
        fetch=True — вернуть результат запроса (fetchall)
        many=True — использовать executemany для пакетных операций
        """
        cur = self.conn.cursor()
        if many:
            cur.executemany(query, params)
        else:
            cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        self.conn.commit()
        return cur

    def fetch_one(self, query, params=()):
        # Получить одну строку результата запроса
        res = self._execute(query, params, fetch=True)
        return res[0] if res else None

    def fetch_all(self, query, params=()):
        # Получить все строки результата запроса
        return self._execute(query, params, fetch=True)

    def _column_exists(self, table, column):
        # Проверить, существует ли столбец в таблице
        return any(r["name"] == column for r in self._execute(f"PRAGMA table_info({table})", fetch=True))

    @staticmethod
    def hash_password(password):
        # Хеширование пароля с помощью SHA-256
        return hashlib.sha256(password.encode()).hexdigest() if password else None

    # --- Инициализация базы данных и создание таблиц ---
    def initialize(self):
        # Создание таблиц и добавление администратора по умолчанию
        self._create_tables()
        if not self.fetch_one("SELECT 1 FROM USERS WHERE username='admin'"):
            self.add_admin("admin", "Admin", "User", "admin123")
        # Добавление новых столбцов при необходимости (миграция)
        if not self._column_exists("THEME", "timer_seconds"):
            self._execute("ALTER TABLE THEME ADD COLUMN timer_seconds INTEGER")
        if not self._column_exists("TEST_SUMMARY", "answers"):
            self._execute("ALTER TABLE TEST_SUMMARY ADD COLUMN answers TEXT")

    def _create_tables(self):
        # Создание всех необходимых таблиц, если их нет
        tables = [
            # Таблица групп
            """CREATE TABLE IF NOT EXISTS GROUPS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                access_code TEXT NOT NULL
            )""",
            # Таблица пользователей
            """CREATE TABLE IF NOT EXISTS USERS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                middle_name TEXT,
                group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES GROUPS(id)
            )""",
            # Таблица связей преподавателей и групп
            """CREATE TABLE IF NOT EXISTS ADMIN_GROUP (
                admin_id INTEGER,
                group_id INTEGER,
                FOREIGN KEY(admin_id) REFERENCES USERS(id),
                FOREIGN KEY(group_id) REFERENCES GROUPS(id),
                PRIMARY KEY(admin_id, group_id)
            )""",
            # Таблица тестов (тем)
            """CREATE TABLE IF NOT EXISTS THEME (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                timer_seconds INTEGER,
                author_id INTEGER,
                FOREIGN KEY (author_id) REFERENCES USERS(id)
            )""",
            # Таблица связей тестов и групп
            """CREATE TABLE IF NOT EXISTS THEME_GROUP (
                theme_id INTEGER,
                group_id INTEGER,
                FOREIGN KEY(theme_id) REFERENCES THEME(id),
                FOREIGN KEY(group_id) REFERENCES GROUPS(id)
            )""",
            # Таблица вопросов
            """CREATE TABLE IF NOT EXISTS QUESTION (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_id INTEGER,
                text TEXT NOT NULL,
                correct_options TEXT NOT NULL,
                theme_local_number INTEGER,
                FOREIGN KEY (theme_id) REFERENCES THEME(id)
            )""",
            # Таблица вариантов ответов
            """CREATE TABLE IF NOT EXISTS ANSWER (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                text TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES QUESTION(id)
            )""",
            # Таблица результатов тестирования
            """CREATE TABLE IF NOT EXISTS TEST_SUMMARY (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                theme_id INTEGER,
                score INTEGER,
                date TEXT,
                answers TEXT,
                elapsed_seconds INTEGER,
                FOREIGN KEY (user_id) REFERENCES USERS(id),
                FOREIGN KEY (theme_id) REFERENCES THEME(id)
            )"""
        ]
        for table in tables:
            self._execute(table)

    # --- Методы управления пользователями ---
    def add_student(self, first_name, last_name, group_id):
        # Добавить нового студента (без логина и пароля)
        self._execute(
            "INSERT INTO USERS (username, password, role, group_id, first_name, last_name) VALUES (?, ?, ?, ?, ?, ?)",
            (None, None, "student", group_id, first_name, last_name)
        )

    def add_admin(self, username, first_name, last_name, password):
        # Добавить нового преподавателя (администратора)
        if not username or not password:
            raise ValueError("Логин и пароль обязательны для преподавателя.")
        if self.fetch_one("SELECT 1 FROM USERS WHERE username = ?", (username,)):
            raise ValueError("Пользователь с таким логином уже существует.")
        self._execute(
            "INSERT INTO USERS (username, password, role, group_id, first_name, last_name) VALUES (?, ?, ?, NULL, ?, ?)",
            (username, self.hash_password(password), "admin", first_name, last_name)
        )

    def check_admin_password(self, admin_id, password):
        # Проверить правильность пароля администратора
        row = self.fetch_one("SELECT password FROM USERS WHERE id=? AND role='admin'", (admin_id,))
        return row and row["password"] == self.hash_password(password)
    
    def update_admin_password(self, admin_id, new_password):
        # Обновить пароль администратора
        self._execute(
            "UPDATE USERS SET password=? WHERE id=? AND role='admin'",
            (self.hash_password(new_password), admin_id)
        )

    def validate_user(self, username, password):
        # Проверить логин и пароль пользователя
        row = self.fetch_one(
            "SELECT id, username, role, group_id, first_name, last_name, middle_name FROM USERS WHERE username = ? AND password = ?",
            (username, self.hash_password(password))
        )
        if row:
            return {
                "id": row["id"], "username": row["username"], "role": row["role"], "group_id": row["group_id"],
                "first_name": row["first_name"], "last_name": row["last_name"], "middle_name": row["middle_name"]
            }
        return None

    def update_user(self, user_id, username, password, role, group_id=None, first_name=None, last_name=None, middle_name=None):
        # Обновить данные пользователя
        fields = ["username=?", "role=?", "group_id=?", "first_name=?", "last_name=?", "middle_name=?"]
        params = [username, role, group_id, first_name, last_name, middle_name]
        if password:
            fields.insert(1, "password=?")
            params.insert(1, self.hash_password(password))
        params.append(user_id)
        try:
            self._execute(f"UPDATE USERS SET {', '.join(fields)} WHERE id=?", tuple(params))
        except sqlite3.IntegrityError:
            raise ValueError("Пользователь с таким именем уже существует")

    def delete_user(self, user_id):
        # Удалить пользователя и его связи с группами (если админ)
        self._execute("DELETE FROM USERS WHERE id=?", (user_id,))
        self._execute("DELETE FROM ADMIN_GROUP WHERE admin_id=?", (user_id,))

    def get_user_by_id(self, user_id):
        # Получить пользователя по id
        return self.fetch_one(
            "SELECT id, username, role, group_id, first_name, last_name, middle_name FROM USERS WHERE id = ?",
            (user_id,)
        )

    # --- Методы управления связями преподавателей и групп ---
    def add_admin_to_group(self, admin_id, group_id):
        # Назначить преподавателя на группу
        self._execute(
            "INSERT OR IGNORE INTO ADMIN_GROUP (admin_id, group_id) VALUES (?, ?)",
            (admin_id, group_id)
        )

    def remove_admin_from_group(self, admin_id, group_id):
        # Удалить преподавателя из группы
        self._execute(
            "DELETE FROM ADMIN_GROUP WHERE admin_id=? AND group_id=?",
            (admin_id, group_id)
        )

    def get_admins_by_group(self, group_id):
        # Получить список преподавателей, назначенных на группу (кроме главного администратора)
        rows = self._execute(
            "SELECT u.id, u.username, u.first_name, u.last_name FROM ADMIN_GROUP ag JOIN USERS u ON ag.admin_id = u.id WHERE ag.group_id=? AND NOT (u.username = 'admin' AND u.role = 'admin')",
            (group_id,), fetch=True
        )
        return [dict(r) for r in rows]

    def get_groups_for_admin(self, admin_id):
        # Получить список групп, назначенных преподавателю
        rows = self._execute(
            "SELECT g.id, g.name FROM ADMIN_GROUP ag JOIN GROUPS g ON ag.group_id = g.id WHERE ag.admin_id=?",
            (admin_id,), fetch=True
        )
        return [{"id": r["id"], "name": r["name"]} for r in rows]

    # --- Методы управления студентами и группами ---
    def get_students_by_group(self, group_id):
        # Получить список студентов в группе
        rows = self.fetch_all(
            "SELECT id, first_name, last_name FROM USERS WHERE group_id = ? AND role = 'student'",
            (group_id,)
        )
        return [{'id': row["id"], 'first_name': row["first_name"], 'last_name': row["last_name"]} for row in rows]
    
    def get_user_by_fullname_and_group(self, first_name, last_name, group_id):
        # Получить студента по ФИО и группе
        row = self.fetch_one(
            "SELECT * FROM USERS WHERE first_name=? AND last_name=? AND group_id=? AND role='student'",
            (first_name, last_name, group_id)
        )
        if row:
            return dict(row)
        return None
                    
    # --- Методы управления группами ---
    def get_groups(self):
        # Получить список всех групп
        rows = self._execute("SELECT id, name, access_code FROM GROUPS ORDER BY id ASC", fetch=True)
        return [{"id": r["id"], "name": r["name"], "access_code": r["access_code"]} for r in rows]
    
    def get_group_by_name(self, group_name):
        # Получить группу по названию
        return self.fetch_one(
            "SELECT * FROM GROUPS WHERE name = ?",
            (group_name,)
        )
    
    def get_group_by_id(self, group_id):
        # Получить группу по id
        return self.fetch_one(
            "SELECT * FROM GROUPS WHERE id = ?",
            (group_id,)
        )
    
    def get_available_groups_for_admin(self, admin_id):
        # Получить группы, доступные преподавателю (главный админ видит все)
        user = self.get_user_by_id(admin_id)
        if not user:
            return []
        if user["role"] == "admin" and user["username"] == "admin":
            return self.get_groups()
        else:
            return self.get_groups_for_admin(admin_id)

    def add_group(self, name, access_code):
        # Добавить новую группу
        self._execute("INSERT INTO GROUPS (name, access_code) VALUES (?, ?)", (name, access_code))

    def edit_group(self, group_id, name, access_code):
        # Изменить данные группы
        self._execute("UPDATE GROUPS SET name=?, access_code=? WHERE id=?", (name, access_code, group_id))

    def delete_group(self, group_id):
        # Удалить группу
        self._execute("DELETE FROM GROUPS WHERE id=?", (group_id,))

    # --- Методы управления тестами (темами) ---
    def get_test_name(self, theme_id):
        # Получить название теста по id
        result = self.fetch_one("SELECT name FROM THEME WHERE id=?", (theme_id,))
        return result["name"] if result else "Без названия"

    def get_theme(self, theme_id):
        # Получить тему (тест) по id
        row = self.fetch_one("SELECT id, name, timer_seconds FROM THEME WHERE id=?", (theme_id,))
        if row:
            return {"id": row["id"], "name": row["name"], "timer_seconds": row["timer_seconds"]}
        return None

    def add_test(self, test_name, author_id, timer_seconds=None):
        # Добавить новый тест (тему)
        try:
            self._execute("INSERT INTO THEME (name, author_id, timer_seconds) VALUES (?, ?, ?)", (test_name, author_id, timer_seconds))
            return self.fetch_one("SELECT id FROM THEME WHERE name = ?", (test_name,))["id"]
        except sqlite3.IntegrityError:
            raise ValueError("Тест с таким названием уже существует.")

    def update_test(self, test_id, test_name, timer_seconds=None):
        # Обновить название и время теста
        self._execute("UPDATE THEME SET name=?, timer_seconds=? WHERE id=?", (test_name, timer_seconds, test_id))

    def delete_test(self, test_id, user_id=None):
        # Удалить тест (тему) и все связанные вопросы и ответы
        test = self.fetch_one("SELECT author_id FROM THEME WHERE id=?", (test_id,))
        if not test:
            raise ValueError("Тест не найден.")
        if user_id is not None:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("Пользователь не найден.")
            if user["id"] != test["author_id"] and not (user["role"] == "admin" and user["username"] == "admin"):
                raise PermissionError("Вы не можете удалить этот тест.")
        question_ids = self._execute("SELECT id FROM QUESTION WHERE theme_id = ?", (test_id,), fetch=True)
        if question_ids:
            self._execute("DELETE FROM ANSWER WHERE question_id = ?", [(qid["id"],) for qid in question_ids], many=True)
        self._execute("DELETE FROM QUESTION WHERE theme_id = ?", (test_id,))
        self._execute("DELETE FROM THEME WHERE id = ?", (test_id,))

    # --- Методы управления вопросами и вариантами ответов ---
    def get_questions(self, theme_id):
        # Получить список вопросов и вариантов ответов для теста
        query = """
            SELECT q.id, q.theme_local_number, q.text, q.correct_options, GROUP_CONCAT(a.text, '|||') AS options
            FROM QUESTION q
            LEFT JOIN ANSWER a ON q.id = a.question_id
            WHERE q.theme_id = ?
            GROUP BY q.id
        """
        rows = self._execute(query, (theme_id,), fetch=True)
        return [
            {
                "id": row["id"],
                "theme_local_number": row["theme_local_number"],
                "text": row["text"],
                "correct_options": list(map(int, row["correct_options"].split(","))) if row["correct_options"] else [],
                "options": row["options"].split("|||") if row["options"] else []
            }
            for row in rows
        ]

    def add_question(self, theme_id, text, options, correct_options):
        # Добавить новый вопрос с вариантами ответов
        if not options:
            raise ValueError("Нельзя добавить вопрос без вариантов ответа.")
        theme_local_number = self.fetch_one(
            "SELECT COALESCE(MAX(theme_local_number), 0) + 1 AS next_num FROM QUESTION WHERE theme_id = ?",
            (theme_id,)
        )["next_num"]
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO QUESTION (theme_id, text, correct_options, theme_local_number) VALUES (?, ?, ?, ?)",
            (theme_id, text, ",".join(map(str, correct_options)), theme_local_number)
        )
        question_id = cur.lastrowid
        cur.executemany(
            "INSERT INTO ANSWER (question_id, text) VALUES (?, ?)",
            [(question_id, option) for option in options]
        )
        self.conn.commit()

    def update_question(self, question_id, text, options, correct_options):
        # Обновить текст вопроса и варианты ответов
        if not options:
            raise ValueError("Нельзя обновить вопрос без вариантов ответа.")
        self._execute(
            "UPDATE QUESTION SET text = ?, correct_options = ? WHERE id = ?",
            (text, ",".join(map(str, correct_options)), question_id)
        )
        self._execute("DELETE FROM ANSWER WHERE question_id = ?", (question_id,))
        self._execute(
            "INSERT INTO ANSWER (question_id, text) VALUES (?, ?)",
            [(question_id, option) for option in options],
            many=True
        )

    def delete_question(self, question_id):
        # Удалить вопрос и все его варианты ответов
        self._execute("DELETE FROM ANSWER WHERE question_id = ?", (question_id,))
        self._execute("DELETE FROM QUESTION WHERE id = ?", (question_id,))

    def update_theme_local_number(self, question_id, new_number):
        # Обновить локальный номер вопроса в теме
        self._execute("UPDATE QUESTION SET theme_local_number = ? WHERE id = ?", (new_number, question_id))

    # --- Методы получения тестов и результатов для пользователей и групп ---
    def get_unpassed_tests_for_user(self, user_id, group_id):
        # Получить список тестов, которые пользователь еще не прошел
        query = """
        SELECT t.id, t.name, t.timer_seconds
        FROM THEME t
        JOIN THEME_GROUP tg ON tg.theme_id = t.id
        WHERE tg.group_id = ?
        AND t.id NOT IN (
            SELECT ts.theme_id FROM TEST_SUMMARY ts WHERE ts.user_id = ?
        )
        """
        rows = self._execute(query, (group_id, user_id), fetch=True)
        return [{"id": r["id"], "name": r["name"], "timer_seconds": r["timer_seconds"]} for r in rows]
    
    def get_journal_for_user(self, user_id):
        # Получить журнал прохождения тестов пользователем
        query = """
            SELECT
                ts.id,
                ts.score,
                ts.date,
                th.name as test_name,
                th.timer_seconds,
                ts.elapsed_seconds,
                (u.last_name || ' ' || u.first_name || IFNULL(u.middle_name, '')) AS teacher_name
            FROM TEST_SUMMARY ts
            JOIN THEME th ON ts.theme_id = th.id
            LEFT JOIN USERS u ON th.author_id = u.id
            WHERE ts.user_id = ?
            ORDER BY ts.date DESC
        """
        return self._execute(query, (user_id,), fetch=True)
    
    def get_tests_for_group(self, group_id):
        # Получить список тестов, назначенных группе
        rows = self._execute(
            "SELECT t.id, t.name, t.timer_seconds FROM THEME t "
            "JOIN THEME_GROUP tg ON tg.theme_id = t.id WHERE tg.group_id = ?", (group_id,), fetch=True
        )
        return [
            {"id": r["id"], "name": r["name"], "timer_seconds": r["timer_seconds"]}
            for r in rows
        ]

    # --- Методы управления назначением тестов группам ---
    def add_test_with_groups(self, test_name, author_id, group_ids, timer_seconds=None):
        # Добавить тест и назначить его нескольким группам
        available_ids = set(g['id'] for g in self.get_available_groups_for_admin(author_id))
        for gid in group_ids:
            if gid not in available_ids:
                raise ValueError("Вы не можете создать тест для группы, в которую не назначены.")
        self._execute("INSERT INTO THEME (name, author_id, timer_seconds) VALUES (?, ?, ?)",
                      (test_name, author_id, timer_seconds))
        test_id = self.fetch_one("SELECT id FROM THEME WHERE name = ? AND author_id = ?", (test_name, author_id))["id"]
        for gid in group_ids:
            self._execute("INSERT INTO THEME_GROUP (theme_id, group_id) VALUES (?, ?)", (test_id, gid))
        return test_id

    def update_test_groups(self, test_id, new_group_ids, author_id):
        # Обновить список групп, которым назначен тест
        available_ids = set(g['id'] for g in self.get_available_groups_for_admin(author_id))
        for gid in new_group_ids:
            if gid not in available_ids:
                raise ValueError("Вы не можете назначить тест в группу, в которую не назначены.")
        self._execute("DELETE FROM THEME_GROUP WHERE theme_id=?", (test_id,))
        for gid in new_group_ids:
            self._execute("INSERT INTO THEME_GROUP (theme_id, group_id) VALUES (?, ?)", (test_id, gid))

    def remove_test_from_group(self, test_id, group_id, user_id=None):
        # Удалить тест из группы (и сам тест, если он больше ни к одной группе не привязан)
        test = self.fetch_one("SELECT author_id FROM THEME WHERE id=?", (test_id,))
        if not test:
            raise ValueError("Тест не найден.")
        if user_id is not None:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("Пользователь не найден.")
            if user["id"] != test["author_id"] and not (user["role"] == "admin" and user["username"] == "admin"):
                raise PermissionError("Вы не можете удалить этот тест.")
        self._execute("DELETE FROM THEME_GROUP WHERE theme_id=? AND group_id=?", (test_id, group_id))
        count = self.fetch_one("SELECT COUNT(*) as cnt FROM THEME_GROUP WHERE theme_id=?", (test_id,))["cnt"]
        if count == 0:
            self.delete_test(test_id, user_id)

    # --- Методы для преподавателей (получение групп и тестов) ---
    def get_teacher_groups(self, admin_id):
        # Получить группы, назначенные преподавателю
        return self.get_groups_for_admin(admin_id)

    def get_teacher_tests_for_group(self, admin_id, group_id):
        # Получить тесты, созданные преподавателем и назначенные группе
        rows = self._execute(
            "SELECT t.id, t.name, t.timer_seconds FROM THEME t "
            "JOIN THEME_GROUP tg ON tg.theme_id = t.id "
            "WHERE tg.group_id = ? AND t.author_id = ?",
            (group_id, admin_id), fetch=True
        )
        return [{"id": r["id"], "name": r["name"], "timer_seconds": r["timer_seconds"]} for r in rows]

    # --- Методы получения результатов тестирования ---
    def get_test_results_for_group(self, group_id, test_id, search_student=None):
        # Получить результаты тестирования студентов группы по конкретному тесту
        query = """
            SELECT u.id as user_id, u.last_name, u.first_name, ts.date, ts.score, ts.elapsed_seconds
            FROM USERS u
            LEFT JOIN TEST_SUMMARY ts ON ts.user_id = u.id AND ts.theme_id = ?
            WHERE u.group_id = ? AND u.role = 'student'
        """
        params = [test_id, group_id]
        if search_student:
            query += " AND (u.last_name LIKE ? OR u.first_name LIKE ?)"
            params += [f"%{search_student}%", f"%{search_student}%"]
        query += " ORDER BY u.last_name, u.first_name"
        return self._execute(query, tuple(params), fetch=True)