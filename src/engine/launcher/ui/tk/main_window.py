from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from src.engine.launcher.services.engine_runner import EngineRunner
from src.engine.launcher.services.project_service import ProjectService
from src.engine.launcher.services.recent_store import RecentProjectsStore


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
        self._root.title("Менеджер проектов")
        self._root.geometry("640x420")

        # --- Theme (dark) ---
        bg = "#1e1e1e"
        fg = "#e6e6e6"
        panel = "#252526"

        self._root.configure(bg=bg)

        # базовые настройки для виджетов tk
        self._tk_bg = bg
        self._tk_fg = fg
        self._tk_panel = panel

        self._selected_path = tk.StringVar(value=self._initial_project)

        self._build_ui()
        self._reload_recent()

        if self._initial_project:
            self._select_path(self._initial_project)

    def run(self) -> None:
        self._root.mainloop()

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        top = tk.Frame(self._root, bg=self._tk_bg)
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(
            top,
            text="Проекты",
            font=("Segoe UI", 14, "bold"),
            bg=self._tk_bg,
            fg=self._tk_fg,
        ).pack(anchor="w")

        mid = tk.Frame(self._root, bg=self._tk_bg)
        mid.pack(fill="both", expand=True, padx=12)

        left = tk.Frame(mid, bg=self._tk_bg)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Недавние проекты:", bg=self._tk_bg, fg=self._tk_fg).pack(anchor="w")

        self._list = tk.Listbox(
            left,
            height=14,
            bg=self._tk_panel,
            fg=self._tk_fg,
            selectbackground="#3a3d41",
            selectforeground=self._tk_fg,
            highlightthickness=0,
        )
        self._list.pack(fill="both", expand=True, pady=(6, 0))
        self._list.bind("<<ListboxSelect>>", self._on_select_recent)

        right = tk.Frame(mid, bg=self._tk_bg)
        right.pack(side="left", fill="y", padx=(12, 0))

        tk.Button(
            right,
            text="Открыть…",
            width=16,
            command=self._open_project,
            bg=self._tk_panel,
            fg=self._tk_fg,
            activebackground=self._tk_panel,
            activeforeground=self._tk_fg,
        ).pack(pady=(0, 8))
        tk.Button(
            right,
            text="Создать…",
            width=16,
            state="disabled",
            bg=self._tk_panel,
            fg=self._tk_fg,
            activebackground=self._tk_panel,
            activeforeground=self._tk_fg,
        ).pack(pady=(0, 8))
        tk.Button(
            right,
            text="Запуск",
            width=16,
            command=self._launch,
            bg=self._tk_panel,
            fg=self._tk_fg,
            activebackground=self._tk_panel,
            activeforeground=self._tk_fg,
        ).pack(pady=(0, 8))

        bottom = tk.Frame(self._root, bg=self._tk_bg)
        bottom.pack(fill="x", padx=12, pady=(6, 12))

        tk.Label(bottom, text="Выбранный проект:", bg=self._tk_bg, fg=self._tk_fg).pack(anchor="w")
        tk.Entry(
            bottom,
            textvariable=self._selected_path,
            bg=self._tk_panel,
            fg=self._tk_fg,
            insertbackground=self._tk_fg,
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
