import traceback
from pathlib import Path


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
        # Импорт внутри try — чтобы поймать ошибки вверху main.py (и вообще в импортах)
        from src.engine.main import main
        main()
    except Exception:
        write_emergency_log(traceback.format_exc())
        raise
