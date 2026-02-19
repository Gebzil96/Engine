from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CreateProjectResult:
    ok: bool
    project_path: str = ""
    error: str = ""


class ProjectService:
    PROJECT_FILE_NAME = "engine_project.json"

    def validate_project_dir(self, path: str) -> tuple[bool, str]:
        p = Path(path)

        if not p.exists():
            return False, "Папка не существует"
        if not p.is_dir():
            return False, "Это не папка"

        project_file = p / self.PROJECT_FILE_NAME
        if not project_file.exists():
            return False, f"Не найден {self.PROJECT_FILE_NAME}"
        if not project_file.is_file():
            return False, f"{self.PROJECT_FILE_NAME} должен быть файлом"

        try:
            data = json.loads(project_file.read_text(encoding="utf-8"))
        except Exception:
            return False, f"{self.PROJECT_FILE_NAME} повреждён или не JSON"

        name = data.get("name", "")
        if not isinstance(name, str) or not name.strip():
            return False, f"В {self.PROJECT_FILE_NAME} нет поля 'name'"

        return True, ""

    def create_project(self, parent_dir: str, project_name: str) -> CreateProjectResult:
        parent = Path(parent_dir)
        name = (project_name or "").strip()

        if not name:
            return CreateProjectResult(ok=False, error="Название проекта пустое")
        if any(ch in name for ch in r'\/:*?"<>|'):
            return CreateProjectResult(
                ok=False,
                error="Название содержит запрещённые символы Windows",
            )

        if not parent.exists():
            return CreateProjectResult(ok=False, error="Папка-родитель не существует")
        if not parent.is_dir():
            return CreateProjectResult(ok=False, error="Папка-родитель не папка")

        project_root = parent / name

        if project_root.exists():
            return CreateProjectResult(ok=False, error="Папка проекта уже существует")

        try:
            # 1) Корневая папка проекта
            project_root.mkdir(parents=True, exist_ok=False)

            # 2) Структура проекта (минимально полезная)
            (project_root / "assets" / "textures").mkdir(parents=True, exist_ok=True)
            (project_root / "assets" / "shaders").mkdir(parents=True, exist_ok=True)
            (project_root / "scenes").mkdir(parents=True, exist_ok=True)

            # 3) engine_project.json
            project_data = {
                "name": name,
                "schema": 1,
                "created_utc": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            }
            (project_root / self.PROJECT_FILE_NAME).write_text(
                json.dumps(project_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            # 4) Простейший README (чтобы папка не была “пустой” для человека)
            (project_root / "README.txt").write_text(
                "Engine Project\n\n"
                "assets/  - ресурсы проекта\n"
                "scenes/  - сцены проекта\n"
                f"{self.PROJECT_FILE_NAME} - описание проекта\n",
                encoding="utf-8",
            )

            return CreateProjectResult(ok=True, project_path=str(project_root))

        except Exception as e:
            # если что-то пошло не так — попробуем подчистить созданную папку (best-effort)
            try:
                if project_root.exists():
                    # удаляем только если пусто/почти пусто — безопаснее
                    # (если что — пользователь удалит вручную)
                    pass
            except Exception:
                pass

            return CreateProjectResult(ok=False, error=f"Ошибка создания проекта: {e}")
