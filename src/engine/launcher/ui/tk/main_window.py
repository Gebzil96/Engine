from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from src.engine.launcher.services.engine_runner import EngineRunner
from src.engine.launcher.services.project_service import ProjectService
from src.engine.launcher.services.recent_store import RecentProjectsStore

# ---------------- Theme ----------------
# 🔧 МОЖНО МЕНЯТЬ: базовые цвета тёмной темы
_BG = "#1E1E1E"
_PANEL = "#252526"
_TEXT = "#E6E6E6"
_MUTED = "#BDBDBD"
_ENTRY_BG = "#2D2D2D"
_BUTTON_BG = "#333333"
_BUTTON_ACTIVE = "#3A3A3A"
_SELECT_BG = "#0E639C"


class LauncherWindow:
    def __init__(
        self,
        recent_store: RecentProjectsStore,
        project_service: ProjectService,
        engine_runner: EngineRunner,
        initial_project: str = "",
    ) -> None:
        self._recent_store = recent_store
        self._project_service = project_service
        self._engine_runner = engine_runner
        self._initial_project = initial_project.strip()

        self._root = tk.Tk()
        self._root.title("Лаунчер движка")
        self._root.geometry("640x420")
        self._root.configure(bg=_BG)

        self._selected_path = tk.StringVar(value=self._initial_project)

        self._build_ui()
        self._reload_recent()

        if self._initial_project:
            self._select_path(self._initial_project)

    def run(self) -> None:
        self._root.mainloop()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        top = tk.Frame(self._root, bg=_BG)
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(
            top,
            text="Проекты",
            font=("Segoe UI", 14, "bold"),
            bg=_BG,
            fg=_TEXT,
        ).pack(anchor="w")

        mid = tk.Frame(self._root, bg=_BG)
        mid.pack(fill="both", expand=True, padx=12)

        left = tk.Frame(mid, bg=_BG)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Недавние проекты:", bg=_BG, fg=_MUTED).pack(anchor="w")

        self._list = tk.Listbox(
            left,
            height=14,
            bg=_ENTRY_BG,
            fg=_TEXT,
            selectbackground=_SELECT_BG,
            selectforeground=_TEXT,
            highlightthickness=0,
            relief="flat",
            activestyle="none",
        )
        self._list.pack(fill="both", expand=True, pady=(6, 0))
        self._list.bind("<<ListboxSelect>>", self._on_select_recent)

        right = tk.Frame(mid, bg=_BG)
        right.pack(side="left", fill="y", padx=(12, 0))

        btn_opts = {
            "width": 16,
            "bg": _BUTTON_BG,
            "fg": _TEXT,
            "activebackground": _BUTTON_ACTIVE,
            "activeforeground": _TEXT,
            "relief": "flat",
            "highlightthickness": 0,
        }

        tk.Button(right, text="Открыть…", command=self._open_project, **btn_opts).pack(pady=(0, 8))
        tk.Button(
            right,
            text="Создать…",
            command=self._create_project,
            **btn_opts,
        ).pack(pady=(0, 8))
        tk.Button(right, text="Запустить", command=self._launch, **btn_opts).pack(pady=(0, 8))

        bottom = tk.Frame(self._root, bg=_BG)
        bottom.pack(fill="x", padx=12, pady=(6, 12))

        tk.Label(bottom, text="Выбранный проект:", bg=_BG, fg=_MUTED).pack(anchor="w")

        tk.Entry(
            bottom,
            textvariable=self._selected_path,
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=_TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_PANEL,
            highlightcolor=_SELECT_BG,
        ).pack(fill="x", pady=(4, 0))

    def _reload_recent(self) -> None:
        self._list.delete(0, tk.END)
        items = self._recent_store.load()
        for item in items:
            self._list.insert(tk.END, item.path)

    def _select_path(self, path: str) -> None:
        self._selected_path.set(path)

    # ---------------- Actions ----------------
    def _on_select_recent(self, _evt: object) -> None:
        sel = self._list.curselection()
        if not sel:
            return
        path = self._list.get(sel[0])
        self._select_path(path)

    def _open_project(self) -> None:
        path = filedialog.askdirectory(title="Выберите папку проекта")
        if not path:
            return

        ok, err = self._project_service.validate_project_dir(path)
        if not ok:
            messagebox.showerror("Некорректный проект", err)
            return

        self._recent_store.push_front(path)
        self._reload_recent()
        self._select_path(path)

    def _create_project(self) -> None:
        parent = filedialog.askdirectory(title="Выберите папку, где создать проект")
        if not parent:
            return

        name = simpledialog.askstring("Создать проект", "Название проекта:", parent=self._root)
        if name is None:
            return  # Cancel
        name = name.strip()
        if not name:
            messagebox.showerror("Создать проект", "Название проекта пустое")
            return

        result = self._project_service.create_project(parent, name)
        if not result.ok:
            messagebox.showerror("Создать проект", result.error)
            return

        # автодобавление в recent + выбор
        self._recent_store.push_front(result.project_path)
        self._reload_recent()
        self._select_path(result.project_path)

        messagebox.showinfo("Создать проект", "Проект создан")

    def _launch(self) -> None:
        path = self._selected_path.get().strip()

        ok, err = self._project_service.validate_project_dir(path)
        if not ok:
            messagebox.showerror("Некорректный проект", err)
            return

        self._recent_store.push_front(path)
        self._engine_runner.launch_engine(path)

        # Закрываем launcher после запуска
        self._root.destroy()
