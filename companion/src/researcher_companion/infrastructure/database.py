import sqlite3
from pathlib import Path


class SQLiteDatabase:
    def __init__(self, path: Path, migrations: Path) -> None:
        self._path = path
        self._migrations = migrations
        self._connection: sqlite3.Connection | None = None

    def start(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self._path)
        self._enable_integrity_checks()
        self._create_migration_history()
        self._apply_pending_migrations()

    def stop(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def is_ready(self) -> bool:
        return self._connection is not None

    def applied_migrations(self) -> list[str]:
        rows = self._require_connection().execute(
            "SELECT version FROM _schema_migrations ORDER BY version"
        )
        return [row[0] for row in rows]

    def _enable_integrity_checks(self) -> None:
        self._require_connection().execute("PRAGMA foreign_keys = ON")

    def _create_migration_history(self) -> None:
        self._require_connection().execute(
            "CREATE TABLE IF NOT EXISTS _schema_migrations "
            "(version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        self._require_connection().commit()

    def _apply_pending_migrations(self) -> None:
        applied = set(self.applied_migrations())
        for migration in sorted(self._migrations.glob("*.sql")):
            if migration.name not in applied:
                self._apply_migration(migration)

    def _apply_migration(self, migration: Path) -> None:
        connection = self._require_connection()
        with connection:
            connection.executescript(migration.read_text(encoding="utf-8"))
            connection.execute(
                "INSERT INTO _schema_migrations(version) VALUES (?)", (migration.name,)
            )

    def _require_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("Database is not started")
        return self._connection
