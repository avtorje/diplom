import sqlite3
import hashlib


class Database:
    def __init__(self):
        self.db_path = "database.db"

    def initialize(self):
        self.create_tables()
        self.add_admin_user()

    def create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS USERS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                middle_name TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS THEME (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )""",
            """CREATE TABLE IF NOT EXISTS QUESTION (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_id INTEGER,
                text TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                theme_local_number INTEGER,
                FOREIGN KEY (theme_id) REFERENCES THEME(id)
            )""",
            """CREATE TABLE IF NOT EXISTS ANSWER (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                text TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES QUESTION(id)
            )""",
            """CREATE TABLE IF NOT EXISTS TEST_SUMMARY (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                theme_id INTEGER,
                score INTEGER,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES USERS(id),
                FOREIGN KEY (theme_id) REFERENCES THEME(id)
            )"""
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(table)
            conn.commit()

    def add_admin_user(self):
        username = "admin"
        password = self.hash_password("admin123")
        role = "admin"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO USERS (username, password, role, first_name, last_name, middle_name) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, password, role, "Admin", "User", "")
                )
                conn.commit()
            except sqlite3.IntegrityError:
                pass  # Пользователь уже существует

    def hash_password(self, password):
        """Хэширование пароля."""
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_user(self, username, password):
        """Проверка пользователя по имени и паролю."""
        hashed_password = self.hash_password(password)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM USERS WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            return cursor.fetchone()

    def get_all_tests(self):
        """Получение всех тестов."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM THEME")
            return cursor.fetchall()

    def add_test(self, test_name):
        """Добавление нового теста."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO THEME (name) VALUES (?)", (test_name,))
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError("Тест с таким названием уже существует.")

    def get_questions(self, theme_id):
        """Получение вопросов для определенной темы."""
        query = """
            SELECT q.id, q.theme_local_number, q.text, q.correct_option, GROUP_CONCAT(a.text) AS options
            FROM QUESTION q
            LEFT JOIN ANSWER a ON q.id = a.question_id
            WHERE q.theme_id = ?
            GROUP BY q.id
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (theme_id,))
            questions = []
            for row in cursor.fetchall():
                options = row[4].split(",") if row[4] else []
                questions.append({
                    "id": row[0],
                    "theme_local_number": row[1],
                    "text": row[2],
                    "correct_option": list(map(int, row[3].split(","))),
                    "options": options
                })
            return questions

    def add_question(self, theme_id, text, options, correct_options):
        """Добавление вопроса вместе с вариантами ответов."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Получаем следующий локальный номер
            theme_local_number = self.get_next_local_question_number(theme_id, cursor)
            # Добавляем вопрос
            cursor.execute(
                "INSERT INTO QUESTION (theme_id, text, correct_option, theme_local_number) VALUES (?, ?, ?, ?)",
                (theme_id, text, ",".join(map(str, correct_options)), theme_local_number)
            )
            question_id = cursor.lastrowid
            # Добавляем варианты ответов
            for option in options:
                cursor.execute(
                    "INSERT INTO ANSWER (question_id, text) VALUES (?, ?)",
                    (question_id, option)
                )
            conn.commit()

    def delete_test(self, test_id):
        """Удаление теста (темы), всех его вопросов и ответов."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Найти все вопросы этого теста
            cursor.execute("SELECT id FROM QUESTION WHERE theme_id = ?", (test_id,))
            question_ids = [row[0] for row in cursor.fetchall()]
            # Удалить все ответы
            for qid in question_ids:
                cursor.execute("DELETE FROM ANSWER WHERE question_id = ?", (qid,))
            # Удалить все вопросы
            cursor.execute("DELETE FROM QUESTION WHERE theme_id = ?", (test_id,))
            # Удалить сам тест
            cursor.execute("DELETE FROM THEME WHERE id = ?", (test_id,))
            conn.commit()

    def update_question(self, question_id, text, options, correct_options):
        """Обновление вопроса и его ответов."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Обновить текст и правильные ответы
            cursor.execute(
                "UPDATE QUESTION SET text = ?, correct_option = ? WHERE id = ?",
                (text, ",".join(map(str, correct_options)), question_id)
            )
            # Удалить старые варианты ответа
            cursor.execute("DELETE FROM ANSWER WHERE question_id = ?", (question_id,))
            # Добавить новые варианты ответа
            for option in options:
                cursor.execute(
                    "INSERT INTO ANSWER (question_id, text) VALUES (?, ?)",
                    (question_id, option)
                )
            conn.commit()

    def get_next_local_question_number(self, theme_id, cursor):
        """Получение следующего локального номера вопроса для указанной темы (теста)."""
        cursor.execute(
            "SELECT COALESCE(MAX(theme_local_number), 0) + 1 FROM QUESTION WHERE theme_id = ?",
            (theme_id,)
        )
        return cursor.fetchone()[0]