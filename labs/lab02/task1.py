import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

PASSWORD_HASH_ITERATIONS = 600_000
SESSION_TIMEOUT_SEC = 900

EMAIL_PATTERN = re.compile(
    r"[A-Za-z][A-Za-z0-9_]{2,63}@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}"
)


class User:
    def __init__(self, username, email, role="user", active=True):
        self.username = username
        self.email = email
        self.role = role
        self.active = active
        self.__password_hash = None
        self.__password_salt = None

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str) or not EMAIL_PATTERN.fullmatch(value):
            raise ValueError("Некоректна електронна пошта")
        self._email = value

    def set_password(self, password: str):
        salt = os.urandom(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PASSWORD_HASH_ITERATIONS,
        )
        self.__password_salt = salt
        self.__password_hash = password_hash

    def check_password(self, password: str) -> bool:
        if self.__password_hash is None:
            return False

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PASSWORD_HASH_ITERATIONS,
        )
        return hmac.compare_digest(self.__password_hash, candidate)

    def deactivate(self):
        self.active = False

    def __str__(self):
        return (
            f"User: {self.username}, email: {self.email}, "
            f"role: {self.role}, active: {self.active}"
        )


class Admin(User):
    def __init__(self, username, email, permissions=None):
        super().__init__(username, email, role="admin")
        self.permissions = set(permissions) if permissions is not None else set()

    def grant_permission(self, permission):
        self.permissions.add(permission)

    def revoke_permission(self, permission):
        self.permissions.discard(permission)

    def has_permission(self, permission) -> bool:
        return permission in self.permissions

    def __str__(self):
        return f"{super().__str__()}, permissions: {sorted(self.permissions)}"


class Session:
    def __init__(self, ip):
        self.ip = ip
        self.login_time = datetime.now(timezone.utc)
        self.last_activity = self.login_time

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("Таймаут має бути додатним")

        elapsed = datetime.now(timezone.utc) - self.last_activity
        return timedelta(0) <= elapsed < timedelta(seconds=timeout_sec)


@dataclass
class AuditRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.records = []

    def add_log(self, username, action):
        self.records.append(
            AuditRecord(datetime.now(timezone.utc), username, action)
        )

    def show_all(self):
        for record in self.records:
            print(
                f"{record.timestamp.isoformat(timespec='seconds')} | "
                f"{record.username} | {record.action}"
            )


class UserAccount:
    def __init__(self, user, session=None, audit_log=None):
        self["user"] = user
        self["session"] = session
        self["audit_log"] = audit_log if audit_log is not None else AuditLog()

    def login(self, username, password, ip) -> bool:
        if (
            not self.user.active
            or username != self.user.username
            or not self.user.check_password(password)
        ):
            self.audit_log.add_log(username, "login_failure")
            return False

        self.session = Session(ip)
        self.session.touch()
        self.audit_log.add_log(username, "login_success")
        return True

    def is_authenticated(self) -> bool:
        return (
            self.user.active
            and self.session is not None
            and self.session.is_active(SESSION_TIMEOUT_SEC)
        )

    def logout(self):
        self.session = None
        self.audit_log.add_log(self.user.username, "logout")

    def __getitem__(self, key):
        if key not in ("user", "session", "audit_log"):
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        types = {
            "user": (User,),
            "session": (Session, type(None)),
            "audit_log": (AuditLog,),
        }
        if key not in types:
            raise KeyError(key)
        if not isinstance(value, types[key]):
            raise TypeError(f"Неправильний тип для {key}")

        if key == "user" and hasattr(self, "user") and value is not self.user:
            self.session = None

        setattr(self, key, value)


def run_demo():
    user = User("danylo", "danylo@example.com")
    user.set_password("Lab2_Test!")
    account = UserAccount(user)

    print(user)
    print("Успішний вхід:", account.login("danylo", "Lab2_Test!", "127.0.0.1"))
    print("Автентифікований:", account.is_authenticated())

    previous_activity = account.session.last_activity
    print("Невдалий вхід:", account.login("danylo", "wrong", "127.0.0.1"))
    print(
        "Невдалий вхід не подовжив сеанс:",
        account.session.last_activity == previous_activity,
    )

    user.email = "danylo_06@example.com"
    print("Нова пошта:", user.email)

    try:
        user.email = "wrong-email"
    except ValueError as error:
        print("Помилка:", error)

    admin = Admin("admin", "admin@example.com")
    admin.grant_permission("manage_users")
    print(admin)
    print("Право manage_users:", admin.has_permission("manage_users"))
    admin.revoke_permission("manage_users")
    print("Після відкликання:", admin.has_permission("manage_users"))

    account.session.last_activity -= timedelta(seconds=SESSION_TIMEOUT_SEC + 1)
    print("Після таймауту:", account.is_authenticated())

    account.login("danylo", "Lab2_Test!", "127.0.0.1")
    account.logout()
    print("Після виходу:", account.is_authenticated())
    print("Доступ через ключ:", account["user"].username)
    account["session"] = None

    try:
        account["password_hash"]
    except KeyError:
        print("Невідомий ключ: KeyError")

    try:
        account["user"] = "wrong"
    except TypeError:
        print("Неправильний тип: TypeError")

    user.deactivate()
    print(
        "Вхід неактивного користувача:",
        account.login("danylo", "Lab2_Test!", "127.0.0.1"),
    )

    print("=== Журнал аудиту ===")
    account.audit_log.show_all()