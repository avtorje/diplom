import sqlite3
import hashlib

class Database:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path

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
            return cursor

    def update_theme_local_number(self, question_id, new_number):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE QUESTION SET theme_local_number = ? WHERE id = ?", (new_number, question_id))
            conn.commit()

    def check_admin_password(self, admin_id, password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM USERS WHERE id=? AND role='admin'", (admin_id,))
            row = cursor.fetchone()
            # сравниваем хэш
            return row and row[0] == self.hash_password(password)

    def update_admin_password(self, admin_id, new_password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE USERS SET password=? WHERE id=? AND role='admin'", (self.hash_password(new_password), admin_id))
            conn.commit()

    def initialize(self):
        self._create_tables()
        self._add_admin_user()

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
        for table in tables:
            self._execute(table)

    def get_main_admin(self):
        """Возвращает первого (главного) администратора"""
        result = self._execute(
            "SELECT id, username, first_name, last_name, middle_name, role FROM USERS WHERE role = 'admin' ORDER BY id ASC LIMIT 1",
            fetch=True
        )
        return result[0] if result else None

    def get_group_users(self, group_id, exclude_main_admin=True):
        """Возвращает пользователей группы (студенты и админы этой группы, кроме главного админа)"""
        query = "SELECT id, username, first_name, last_name, middle_name, role FROM USERS WHERE group_id = ?"
        params = [group_id]
        if exclude_main_admin:
            main_admin = self.get_main_admin()
            if main_admin:
                query += " AND id != ?"
                params.append(main_admin[0])
        return self._execute(query, tuple(params), fetch=True)

    def _add_admin_user(self):
        try:
            self._execute(
                "INSERT INTO USERS (username, password, role, first_name, last_name, middle_name) VALUES (?, ?, ?, ?, ?, ?)",
                ("admin", self.hash_password("admin123"), "admin", "Admin", "User", "")
            )
        except sqlite3.IntegrityError:
            pass

    # --- Новый метод: Получение главного администратора ---
    def get_main_admin(self):
        # Считаем главным администратора с username = 'admin' (создаётся при инициализации)
        result = self._execute("SELECT id, username, role FROM USERS WHERE role='admin' AND username='admin'", fetch=True)
        return result[0] if result else None

    # --- Новый метод: Получение админов по id группы (кроме главного) ---
    def get_admins_by_group(self, group_id):
        return self._execute(
            "SELECT id, username, role FROM USERS WHERE role='admin' AND username != 'admin' AND group_id = ?",
            (group_id,),
            fetch=True
        )
    
    # --- Новый метод: Получение студентов по id группы ---
    def get_students_by_group(self, group_id):
        return self._execute(
            "SELECT id, username, role FROM USERS WHERE role='student' AND group_id = ?",
            (group_id,),
            fetch=True
        )
    
    # --- Получить пользователей для общего списка (только главный админ) ---
    def get_users_main_list(self):
        # Только главный админ в общем списке
        main_admin = self.get_main_admin()
        return [main_admin] if main_admin else []

    def get_groups(self):
        return self._execute("SELECT id, name FROM GROUPS", fetch=True)

    def add_group(self, name, access_code):
        self._execute("INSERT INTO GROUPS (name, access_code) VALUES (?, ?)", (name, access_code))

    def edit_group(self, group_id, name, access_code):
        self._execute("UPDATE GROUPS SET name=?, access_code=? WHERE id=?", (name, access_code, group_id))

    def delete_group(self, group_id):
        self._execute("DELETE FROM GROUPS WHERE id=?", (group_id,))

    def get_group_by_id(self, group_id):
        result = self._execute("SELECT id, name, access_code FROM GROUPS WHERE id=?", (group_id,), fetch=True)
        return result[0] if result else None

    # --------- Исправленные методы для пользователей ---------
    def add_user(self, username, password, role, group_id=None, first_name=None, last_name=None, middle_name=None):
        if role == "admin":
            self._execute(
                "INSERT INTO USERS (username, password, role, group_id, first_name, last_name, middle_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, self.hash_password(password), role, group_id, first_name, last_name, middle_name)
            )
        else:
            self._execute(
                "INSERT INTO USERS (username, password, role, group_id, first_name, last_name, middle_name) VALUES (?, NULL, ?, ?, ?, ?, ?)",
                (username, role, group_id, first_name, last_name, middle_name)
            )

    def update_user(self, user_id, username, password, role, group_id=None, first_name=None, last_name=None, middle_name=None):
        if role == "admin":
            self._execute(
                "UPDATE USERS SET username=?, password=?, role=?, group_id=?, first_name=?, last_name=?, middle_name=? WHERE id=?",
                (username, self.hash_password(password), role, group_id, first_name, last_name, middle_name, user_id)
            )
        else:
            self._execute(
                "UPDATE USERS SET username=?, password=NULL, role=?, group_id=?, first_name=?, last_name=?, middle_name=? WHERE id=?",
                (username, role, group_id, first_name, last_name, middle_name, user_id)
            )
    # --------------------------------------------------------

    def delete_user(self, user_id):
        self._execute("DELETE FROM USERS WHERE id=?", (user_id,))

    def get_user_by_id(self, user_id):
        result = self._execute(
            "SELECT id, username, role, group_id, first_name, last_name, middle_name FROM USERS WHERE id = ?",
            (user_id,),
            fetch=True
        )
        return result[0] if result else None

    def get_all_users(self):
        """Возвращает список всех пользователей"""
        return self._execute(
            "SELECT id, username, first_name, role, group_id FROM USERS",
            fetch=True
        )

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_user(self, username, password):
        result = self._execute(
            "SELECT * FROM USERS WHERE username = ? AND password = ?",
            (username, self.hash_password(password)), fetch=True
        )
        return result[0] if result else None

    def get_all_tests(self):
        return self._execute("SELECT id, name FROM THEME", fetch=True)

    def add_test(self, test_name):
        try:
            self._execute("INSERT INTO THEME (name) VALUES (?)", (test_name,))
        except sqlite3.IntegrityError:
            raise ValueError("Тест с таким названием уже существует.")

    def get_questions(self, theme_id):
        query = """
            SELECT q.id, q.theme_local_number, q.text, q.correct_option, GROUP_CONCAT(a.text)
            FROM QUESTION q
            LEFT JOIN ANSWER a ON q.id = a.question_id
            WHERE q.theme_id = ?
            GROUP BY q.id
        """
        rows = self._execute(query, (theme_id,), fetch=True)
        questions = []
        for row in rows:
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
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(MAX(theme_local_number), 0) + 1 FROM QUESTION WHERE theme_id = ?",
                (theme_id,)
            )
            theme_local_number = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO QUESTION (theme_id, text, correct_option, theme_local_number) VALUES (?, ?, ?, ?)",
                (theme_id, text, ",".join(map(str, correct_options)), theme_local_number)
            )
            question_id = cursor.lastrowid
            cursor.executemany(
                "INSERT INTO ANSWER (question_id, text) VALUES (?, ?)",
                [(question_id, option) for option in options]
            )
            conn.commit()

    def delete_test(self, test_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM QUESTION WHERE theme_id = ?", (test_id,))
            question_ids = [row[0] for row in cursor.fetchall()]
            if question_ids:
                cursor.executemany("DELETE FROM ANSWER WHERE question_id = ?", [(qid,) for qid in question_ids])
            cursor.execute("DELETE FROM QUESTION WHERE theme_id = ?", (test_id,))
            cursor.execute("DELETE FROM THEME WHERE id = ?", (test_id,))
            conn.commit()

    def update_question(self, question_id, text, options, correct_options):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE QUESTION SET text = ?, correct_option = ? WHERE id = ?",
                (text, ",".join(map(str, correct_options)), question_id)
            )
            cursor.execute("DELETE FROM ANSWER WHERE question_id = ?", (question_id,))
            cursor.executemany(
                "INSERT INTO ANSWER (question_id, text) VALUES (?, ?)",
                [(question_id, option) for option in options]
            )
            conn.commit()

    def delete_question(self, question_id):
        self._execute("DELETE FROM ANSWER WHERE question_id = ?", (question_id,))
        self._execute("DELETE FROM QUESTION WHERE id = ?", (question_id,))

    def update_theme_local_number(self, question_id, new_number):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE QUESTION SET theme_local_number = ? WHERE id = ?", (new_number, question_id))
            conn.commit()