import sqlite3
import hashlib
import datetime

class Database:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.initialize()

    def _execute(self, query, params=(), fetch=False, many=False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if many:
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest() if password else None

    def initialize(self):
        self._create_tables()
        self._add_admin_user()
        self._add_timer_column()
        self._add_answers_column_to_test_summary()

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
                name TEXT NOT NULL UNIQUE
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
                FOREIGN KEY (user_id) REFERENCES USERS(id),
                FOREIGN KEY (theme_id) REFERENCES THEME(id)
            )"""
        ]
        for table in tables:
            self._execute(table)

    def initialize(self):
        self._create_tables()
        self._add_admin_user()
        self._add_timer_column()
        self._add_answers_column_to_test_summary()

    def _add_answers_column_to_test_summary(self):
        res = self._execute("PRAGMA table_info(TEST_SUMMARY)", fetch=True)
        if not any(r[1] == "answers" for r in res):
            self._execute("ALTER TABLE TEST_SUMMARY ADD COLUMN answers TEXT")

    def _add_admin_user(self):
        try:
            self._execute(
                "INSERT INTO USERS (username, password, role, first_name, last_name, middle_name) VALUES (?, ?, ?, ?, ?, ?)",
                ("admin", self.hash_password("admin123"), "admin", "Admin", "User", "")
            )
        except sqlite3.IntegrityError:
            pass

    def _add_timer_column(self):
        res = self._execute("PRAGMA table_info(THEME)", fetch=True)
        if not any(r[1] == "timer_seconds" for r in res):
            self._execute("ALTER TABLE THEME ADD COLUMN timer_seconds INTEGER")
    
    def _add_answers_column_to_test_summary(self):
        # Добавляем поле answers, если его нет в TEST_SUMMARY
        res = self._execute("PRAGMA table_info(TEST_SUMMARY)", fetch=True)
        if not any(r[1] == "answers" for r in res):
            self._execute("ALTER TABLE TEST_SUMMARY ADD COLUMN answers TEXT")

    # --- Универсальные методы выборки ---
    def fetch_one(self, query, params=()):
        res = self._execute(query, params, fetch=True)
        return res[0] if res else None

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

    def get_user_by_id(self, user_id):
        return self.fetch_one(
            "SELECT id, username, role, group_id, first_name, last_name, middle_name FROM USERS WHERE id = ?",
            (user_id,)
        )

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
            main_admin = self.get_main_admin()
            if main_admin:
                query += " AND id != ?"
                params.append(main_admin[0])
        return self._execute(query, tuple(params), fetch=True)

    def get_admins_by_group(self, group_id):
        return self._execute(
            "SELECT id, username, role FROM USERS WHERE role='admin' AND username != 'admin' AND group_id = ?",
            (group_id,), fetch=True
        )

    def get_students_by_group(self, group_id):
        return self._execute(
            "SELECT id, username, role FROM USERS WHERE role='student' AND group_id = ?",
            (group_id,), fetch=True
        )

    def get_main_admin(self):
        return self.fetch_one("SELECT id, username, role FROM USERS WHERE role='admin' AND username='admin'")

    def check_admin_password(self, admin_id, password):
        row = self.fetch_one("SELECT password FROM USERS WHERE id=? AND role='admin'", (admin_id,))
        return row and row[0] == self.hash_password(password)

    def update_admin_password(self, admin_id, new_password):
        self._execute("UPDATE USERS SET password=? WHERE id=? AND role='admin'", (self.hash_password(new_password), admin_id))

    def validate_user(self, username, password):
        return self.fetch_one(
            "SELECT * FROM USERS WHERE username = ? AND password = ?",
            (username, self.hash_password(password))
        )

    # --- Группы ---
    def get_groups(self):
        return self._execute("SELECT id, name FROM GROUPS ORDER BY id ASC", fetch=True)

    def add_group(self, name, access_code):
        self._execute("INSERT INTO GROUPS (name, access_code) VALUES (?, ?)", (name, access_code))

    def edit_group(self, group_id, name, access_code):
        self._execute("UPDATE GROUPS SET name=?, access_code=? WHERE id=?", (name, access_code, group_id))

    def delete_group(self, group_id):
        self._execute("DELETE FROM GROUPS WHERE id=?", (group_id,))

    def get_group_by_id(self, group_id):
        return self.fetch_one("SELECT id, name, access_code FROM GROUPS WHERE id=?", (group_id,))

    def get_group_by_name(self, name):
        row = self.fetch_one("SELECT id, name, access_code FROM GROUPS WHERE name = ?", (name,))
        if row:
            return {"id": row[0], "name": row[1], "access_code": row[2]}
        return None

    def get_user_by_name_and_group(self, username, group_id):
        row = self.fetch_one(
            "SELECT id, username, role, group_id, first_name, last_name, middle_name FROM USERS WHERE username = ? AND group_id = ?",
            (username, group_id)
        )
        if row:
            return {
                "id": row[0], "username": row[1], "role": row[2],
                "group_id": row[3], "first_name": row[4],
                "last_name": row[5], "middle_name": row[6]
            }
        return None

    def get_user_group_id(self, user_id):
        row = self.fetch_one("SELECT group_id FROM USERS WHERE id = ?", (user_id,))
        return row[0] if row and row[0] is not None else None

    # --- Тесты и вопросы ---
    def get_all_tests(self, group_id=None):
        if group_id is None:
            return self._execute("SELECT id, name, timer_seconds FROM THEME", fetch=True)
        else:
            return self._execute(
                "SELECT t.id, t.name, t.timer_seconds FROM THEME t "
                "JOIN THEME_GROUP tg ON tg.theme_id = t.id WHERE tg.group_id = ?", (group_id,), fetch=True
            )

    def get_test_name(self, theme_id):
        
        result = self._execute("SELECT name FROM THEME WHERE id=?", (theme_id,), fetch=True)
        return result[0][0] if result else "Без названия"
    
    def get_theme(self, theme_id):
        result = self._execute("SELECT id, name, timer_seconds FROM THEME WHERE id=?", (theme_id,), fetch=True)
        return result[0] if result else None
    
    def add_test(self, test_name, timer_seconds=None):
        try:
            self._execute("INSERT INTO THEME (name, timer_seconds) VALUES (?, ?)", (test_name, timer_seconds))
            return self._execute("SELECT id FROM THEME WHERE name = ?", (test_name,), fetch=True)[0][0]
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

    def save_test_results(self, user_id, test_id, questions, answers, score):
        """
        Сохраняет результат теста пользователя в таблицу TEST_SUMMARY.
        """
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._execute(
            "INSERT INTO TEST_SUMMARY (user_id, theme_id, score, date, answers) VALUES (?, ?, ?, ?, ?)",
            (user_id, test_id, score, date_str, str(answers))
        )

    def delete_test(self, test_id):
        question_ids = self._execute("SELECT id FROM QUESTION WHERE theme_id = ?", (test_id,), fetch=True)
        if question_ids:
            self._execute("DELETE FROM ANSWER WHERE question_id = ?", [(qid[0],) for qid in question_ids], many=True)
        self._execute("DELETE FROM QUESTION WHERE theme_id = ?", (test_id,))
        self._execute("DELETE FROM THEME WHERE id = ?", (test_id,))

    def get_questions(self, theme_id):
        query = """
            SELECT q.id, q.theme_local_number, q.text, q.correct_options, GROUP_CONCAT(a.text, '|||')
            FROM QUESTION q
            LEFT JOIN ANSWER a ON q.id = a.question_id
            WHERE q.theme_id = ?
            GROUP BY q.id
        """
        rows = self._execute(query, (theme_id,), fetch=True)
        return [
            {
                "id": row[0],
                "theme_local_number": row[1],
                "text": row[2],
                "correct_options": list(map(int, row[3].split(","))) if row[3] else [],
                "options": row[4].split("|||") if row[4] else []
            }
            for row in rows
        ]

    def add_question(self, theme_id, text, options, correct_options):
        theme_local_number = self.fetch_one(
            "SELECT COALESCE(MAX(theme_local_number), 0) + 1 FROM QUESTION WHERE theme_id = ?",
            (theme_id,)
        )[0]
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO QUESTION (theme_id, text, correct_options, theme_local_number) VALUES (?, ?, ?, ?)",
            (theme_id, text, ",".join(map(str, correct_options)), theme_local_number)
        )
        question_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO ANSWER (question_id, text) VALUES (?, ?)",
            [(question_id, option) for option in options]
        )
        self.conn.commit()

    def update_question(self, question_id, text, options, correct_options):
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
