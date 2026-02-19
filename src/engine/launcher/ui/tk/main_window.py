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
        self._root.title("Engine Launcher")
        self._root.geometry("640x420")

        self._selected_path = tk.StringVar(value=self._initial_project)

        self._build_ui()
        self._reload_recent()

        if self._initial_project:
            self._select_path(self._initial_project)

    def run(self) -> None:
        self._root.mainloop()

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        top = tk.Frame(self._root)
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(top, text="Projects", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        mid = tk.Frame(self._root)
        mid.pack(fill="both", expand=True, padx=12)

        left = tk.Frame(mid)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Recent projects:").pack(anchor="w")

        self._list = tk.Listbox(left, height=14)
        self._list.pack(fill="both", expand=True, pady=(6, 0))
        self._list.bind("<<ListboxSelect>>", self._on_select_recent)

        right = tk.Frame(mid)
        right.pack(side="left", fill="y", padx=(12, 0))

        tk.Button(right, text="Open…", width=16, command=self._open_project).pack(pady=(0, 8))
        tk.Button(right, text="Create…", width=16, state="disabled").pack(pady=(0, 8))
        tk.Button(right, text="Launch", width=16, command=self._launch).pack(pady=(0, 8))

        bottom = tk.Frame(self._root)
        bottom.pack(fill="x", padx=12, pady=(6, 12))

        tk.Label(bottom, text="Selected:").pack(anchor="w")
        tk.Entry(bottom, textvariable=self._selected_path).pack(fill="x", pady=(4, 0))

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
        path = filedialog.askdirectory(title="Select project folder")
        if not path:
            return

        ok, err = self._project_service.validate_project_dir(path)
        if not ok:
            messagebox.showerror("Invalid project", err)
            return

        self._recent_store.push_front(path)
        self._reload_recent()
        self._select_path(path)

    def _launch(self) -> None:
        path = self._selected_path.get().strip()
        ok, err = self._project_service.validate_project_dir(path)
        if not ok:
            messagebox.showerror("Invalid project", err)
            return

        self._recent_store.push_front(path)
        self._engine_runner.launch_engine(path)

        # Закрываем launcher после запуска
        self._root.destroy()
