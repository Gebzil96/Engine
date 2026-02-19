import traceback
from pathlib import Path
import argparse
import os
import sys


def write_emergency_log(text: str) -> None:
    # run_engine.pyw лежит в корне проекта -> logs рядом
    project_root = Path(__file__).resolve().parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / "run.log"

    # ВАЖНО: пишем ДО любых импортов движка, чтобы поймать даже падение импорта
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n--- EMERGENCY CRASH ---\n")
        f.write(text)
        f.write("\n")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--launcher", action="store_true")
        parser.add_argument("--engine", action="store_true")
        parser.add_argument("--project", type=str, default="")
        args, _unknown = parser.parse_known_args()

        # Режим по умолчанию: если НЕ сказали явно engine — показываем launcher
        run_launcher = args.launcher or (not args.engine)

        if run_launcher:
            # Launcher не импортирует движок. Он только выбирает project и запускает engine как subprocess.
            from src.engine.app.run_launcher_app import run_launcher_app

            run_launcher_app(initial_project=args.project or "")
        else:
            # Передаём выбранный проект через env (движок пока может его игнорировать — не ломаем движок)
            if args.project:
                os.environ["ENGINE_PROJECT"] = args.project

            # Импорт внутри try — чтобы поймать ошибки вверху main.py (и вообще в импортах)
            from src.engine.main import main

            main()

    except Exception:
        write_emergency_log(traceback.format_exc())
        raise
