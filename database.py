import sqlite3
import hashlib
import datetime

class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Позволяет получать строки как словари
        self.initialize()

    # --- Вспомогательные методы ---
    def _execute(self, query, params=(), fetch=False, many=False):
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
        res = self._execute(query, params, fetch=True)
        return res[0] if res else None

    def fetch_all(self, query, params=()):
        return self._execute(query, params, fetch=True)

    def _column_exists(self, table, column):
        return any(r["name"] == column for r in self._execute(f"PRAGMA table_info({table})", fetch=True))

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest() if password else None

    # --- Инициализация и создание таблиц ---
    def initialize(self):
        self._create_tables()
        if not self.fetch_one("SELECT 1 FROM USERS WHERE username='admin'"):
            self.add_user("admin", "admin123", "admin", first_name="Admin", last_name="User")
        if not self._column_exists("THEME", "timer_seconds"):
            self._execute("ALTER TABLE THEME ADD COLUMN timer_seconds INTEGER")
        if not self._column_exists("TEST_SUMMARY", "answers"):
            self._execute("ALTER TABLE TEST_SUMMARY ADD COLUMN answers TEXT")

    def _create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS GROUPS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                access_code TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS USERS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT,
                role TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                middle_name TEXT,
                group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES GROUPS(id)
            )""",
            """CREATE TABLE IF NOT EXISTS THEME (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                timer_seconds INTEGER
            )""",
            """CREATE TABLE IF NOT EXISTS THEME_GROUP (
                theme_id INTEGER,
                group_id INTEGER,
                FOREIGN KEY(theme_id) REFERENCES THEME(id),
                FOREIGN KEY(group_id) REFERENCES GROUPS(id)
            )""",
            """CREATE TABLE IF NOT EXISTS QUESTION (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_id INTEGER,
                text TEXT NOT NULL,
                correct_options TEXT NOT NULL,
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
                answers TEXT,
                FOREIGN KEY (user_id) REFERENCES USERS(id),
                FOREIGN KEY (theme_id) REFERENCES THEME(id)
            )"""
        ]
        for table in tables:
            self._execute(table)

    # --- Пользователи ---
    def add_user(self, username, password, role, group_id=None, first_name=None, last_name=None, middle_name=None):
        try:
            self._execute(
                "INSERT INTO USERS (username, password, role, group_id, first_name, last_name, middle_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, self.hash_password(password), role, group_id, first_name, last_name, middle_name)
            )
        except sqlite3.IntegrityError:
            raise ValueError("Пользователь с таким именем уже существует")

    def update_user(self, user_id, username, password, role, group_id=None, first_name=None, last_name=None, middle_name=None):
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
        self._execute("DELETE FROM USERS WHERE id=?", (user_id,))

    def get_user(self, **kwargs):
        if not kwargs:
            return None
        query = "SELECT id, username, role, group_id, first_name, last_name, middle_name FROM USERS WHERE " + \
                " AND ".join(f"{k}=?" for k in kwargs)
        row = self.fetch_one(query, tuple(kwargs.values()))
        if row:
            return {
                "id": row["id"], "username": row["username"], "role": row["role"], "group_id": row["group_id"],
                "first_name": row["first_name"], "last_name": row["last_name"], "middle_name": row["middle_name"]
            }
        return None

    def get_users(self, group_id=None, role=None, exclude_main_admin=False):
        query = "SELECT id, username, first_name, last_name, middle_name, role FROM USERS WHERE 1=1"
        params = []
        if group_id is not None:
            query += " AND group_id=?"
            params.append(group_id)
        if role:
            query += " AND role=?"
            params.append(role)
        if exclude_main_admin:
            query += " AND NOT (role='admin' AND username='admin')"
        rows = self._execute(query, tuple(params), fetch=True)
        return [
            {
                "id": r["id"], "username": r["username"], "first_name": r["first_name"],
                "last_name": r["last_name"], "middle_name": r["middle_name"], "role": r["role"]
            }
            for r in rows
        ]
    
    def get_admins_by_group(self, group_id):
        # Возвращает список словарей с пользователями-админами этой группы
        return self.fetch_all(
            "SELECT id, username FROM USERS WHERE group_id = ? AND role = 'admin'",
            (group_id,)
        )

    def get_students_by_group(self, group_id):
        # Возвращает список словарей с пользователями-студентами этой группы
        return self.fetch_all(
            "SELECT id, username FROM USERS WHERE group_id = ? AND role = 'student'",
            (group_id,)
        )

    def check_admin_password(self, admin_id, password):
        row = self.fetch_one("SELECT password FROM USERS WHERE id=? AND role='admin'", (admin_id,))
        return row and row["password"] == self.hash_password(password)

    def update_admin_password(self, admin_id, new_password):
        self._execute("UPDATE USERS SET password=? WHERE id=? AND role='admin'", (self.hash_password(new_password), admin_id))

    def validate_user(self, username, password):
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

    def get_main_admin(self):
        row = self.fetch_one("SELECT id, username, first_name, last_name, middle_name FROM USERS WHERE username='admin' AND role='admin'")
        if row:
            return {
                "id": row["id"], "username": row["username"], "first_name": row["first_name"],
                "last_name": row["last_name"], "middle_name": row["middle_name"]
            }
        return None

    # --- Группы ---
    def get_groups(self):
        rows = self._execute("SELECT id, name FROM GROUPS ORDER BY id ASC", fetch=True)
        return [{"id": r["id"], "name": r["name"]} for r in rows]

    def add_group(self, name, access_code):
        self._execute("INSERT INTO GROUPS (name, access_code) VALUES (?, ?)", (name, access_code))

    def edit_group(self, group_id, name, access_code):
        self._execute("UPDATE GROUPS SET name=?, access_code=? WHERE id=?", (name, access_code, group_id))

    def delete_group(self, group_id):
        self._execute("DELETE FROM GROUPS WHERE id=?", (group_id,))

    def get_group(self, **kwargs):
        if not kwargs:
            return None
        query = "SELECT id, name, access_code FROM GROUPS WHERE " + " AND ".join(f"{k}=?" for k in kwargs)
        row = self.fetch_one(query, tuple(kwargs.values()))
        if row:
            return {"id": row["id"], "name": row["name"], "access_code": row["access_code"]}
        return None

    # --- Тесты ---
    def get_all_tests(self, group_id=None):
        if group_id is None:
            rows = self._execute("SELECT id, name, timer_seconds FROM THEME", fetch=True)
        else:
            rows = self._execute(
                "SELECT t.id, t.name, t.timer_seconds FROM THEME t "
                "JOIN THEME_GROUP tg ON tg.theme_id = t.id WHERE tg.group_id = ?", (group_id,), fetch=True
            )
        return [
            {"id": r["id"], "name": r["name"], "timer_seconds": r["timer_seconds"]}
            for r in rows
        ]

    def get_test_name(self, theme_id):
        result = self.fetch_one("SELECT name FROM THEME WHERE id=?", (theme_id,))
        return result["name"] if result else "Без названия"

    def get_theme(self, theme_id):
        row = self.fetch_one("SELECT id, name, timer_seconds FROM THEME WHERE id=?", (theme_id,))
        if row:
            return {"id": row["id"], "name": row["name"], "timer_seconds": row["timer_seconds"]}
        return None

    def add_test(self, test_name, timer_seconds=None):
        try:
            self._execute("INSERT INTO THEME (name, timer_seconds) VALUES (?, ?)", (test_name, timer_seconds))
            return self.fetch_one("SELECT id FROM THEME WHERE name = ?", (test_name,))["id"]
        except sqlite3.IntegrityError:
            raise ValueError("Тест с таким названием уже существует.")

    def update_test(self, test_id, test_name, timer_seconds=None):
        self._execute("UPDATE THEME SET name=?, timer_seconds=? WHERE id=?", (test_name, timer_seconds, test_id))

    def remove_test_timer(self, test_id):
        self._execute("UPDATE THEME SET timer_seconds=NULL WHERE id=?", (test_id,))

    def add_test_groups(self, test_id, group_ids):
        self._execute(
            "INSERT INTO THEME_GROUP (theme_id, group_id) VALUES (?, ?)",
            [(test_id, gid) for gid in group_ids],
            many=True
        )

    def delete_test(self, test_id):
        question_ids = self._execute("SELECT id FROM QUESTION WHERE theme_id = ?", (test_id,), fetch=True)
        if question_ids:
            self._execute("DELETE FROM ANSWER WHERE question_id = ?", [(qid["id"],) for qid in question_ids], many=True)
        self._execute("DELETE FROM QUESTION WHERE theme_id = ?", (test_id,))
        self._execute("DELETE FROM THEME WHERE id = ?", (test_id,))

    # --- Вопросы ---
    def get_questions(self, theme_id):
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
        self._execute("DELETE FROM ANSWER WHERE question_id = ?", (question_id,))
        self._execute("DELETE FROM QUESTION WHERE id = ?", (question_id,))

    def update_theme_local_number(self, question_id, new_number):
        self._execute("UPDATE QUESTION SET theme_local_number = ? WHERE id = ?", (new_number, question_id))

    # --- Результаты тестов ---
    def save_test_results(self, user_id, test_id, questions, answers, score):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._execute(
            "INSERT INTO TEST_SUMMARY (user_id, theme_id, score, date, answers) VALUES (?, ?, ?, ?, ?)",
            (user_id, test_id, score, date_str, str(answers))
        )

    def get_unpassed_tests_for_user(self, user_id, group_id):
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