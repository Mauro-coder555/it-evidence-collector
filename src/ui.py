"""Tkinter user interface for the IT Evidence Collector app."""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk
from typing import Any

from src.collectors import collect_evidence
from src.i18n import SUPPORTED_LANGUAGES, normalize_language, t
from src.report import REPORTS_DIR, generate_markdown_report


class EvidenceCollectorApp:
    """Main desktop application window."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the application UI."""
        self.root = root
        self.root.title(t("en", "app.title"))
        self.root.geometry("760x500")
        self.root.minsize(720, 460)

        self.event_queue: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.latest_report_path: Path | None = None
        self.collection_thread: threading.Thread | None = None

        self.language_var = tk.StringVar(value="en")
        self.language_display_var = tk.StringVar(value=SUPPORTED_LANGUAGES["en"])

        self._build_ui()
        self._refresh_language()
        self._poll_queue()

    def _current_language(self) -> str:
        """Return the currently selected language code."""
        return normalize_language(self.language_var.get())

    def _build_ui(self) -> None:
        """Build the UI widgets."""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X)

        self.title_label = ttk.Label(
            top_frame,
            text="",
            font=("Segoe UI", 18, "bold"),
        )
        self.title_label.pack(side=tk.LEFT, anchor=tk.W)

        language_frame = ttk.Frame(top_frame)
        language_frame.pack(side=tk.RIGHT, anchor=tk.E)

        self.language_label = ttk.Label(language_frame, text="")
        self.language_label.pack(side=tk.LEFT, padx=(0, 8))

        self.language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_display_var,
            values=list(SUPPORTED_LANGUAGES.values()),
            state="readonly",
            width=12,
        )
        self.language_combo.pack(side=tk.LEFT)
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_changed)

        self.description_label = ttk.Label(
            main_frame,
            text="",
            wraplength=690,
        )
        self.description_label.pack(anchor=tk.W, pady=(8, 16))

        self.safety_label = ttk.Label(
            main_frame,
            text="",
            wraplength=690,
            foreground="#555555",
        )
        self.safety_label.pack(anchor=tk.W, pady=(0, 16))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 16))

        self.start_button = ttk.Button(
            button_frame,
            text="",
            command=self.start_collection,
        )
        self.start_button.pack(side=tk.LEFT)

        self.open_reports_button = ttk.Button(
            button_frame,
            text="",
            command=self.open_reports_folder,
        )
        self.open_reports_button.pack(side=tk.LEFT, padx=(10, 0))

        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            maximum=100,
            variable=self.progress_var,
            mode="determinate",
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))

        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W, pady=(0, 12))

        self.output_label = ttk.Label(main_frame, text="")
        self.output_label.pack(anchor=tk.W)

        self.output_text = tk.Text(
            main_frame,
            height=13,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

    def _on_language_changed(self, _event: tk.Event) -> None:
        """Update application language based on the selected display value."""
        selected_display = self.language_display_var.get()

        for code, display_name in SUPPORTED_LANGUAGES.items():
            if display_name == selected_display:
                self.language_var.set(code)
                break

        self._refresh_language()

    def _refresh_language(self) -> None:
        """Refresh visible UI texts using the selected language."""
        language = self._current_language()

        self.root.title(t(language, "app.title"))
        self.title_label.configure(text=t(language, "app.title"))
        self.description_label.configure(text=t(language, "app.description"))
        self.safety_label.configure(text=t(language, "app.safety"))
        self.language_label.configure(text=t(language, "label.language"))
        self.start_button.configure(text=t(language, "button.start"))
        self.open_reports_button.configure(text=t(language, "button.open_reports"))
        self.output_label.configure(text=t(language, "label.activity_log"))

        if not self.collection_thread or not self.collection_thread.is_alive():
            self.status_var.set(t(language, "status.ready"))

    def _log(self, message: str) -> None:
        """Append a message to the activity log."""
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)

    def _set_busy_state(self, is_busy: bool) -> None:
        """Enable or disable UI controls during collection."""
        self.start_button.configure(state=tk.DISABLED if is_busy else tk.NORMAL)
        self.language_combo.configure(state=tk.DISABLED if is_busy else "readonly")

    def _progress_callback(self, percent: int, message: str) -> None:
        """Receive progress updates from the collection thread."""
        self.event_queue.put(("progress", {"percent": percent, "message": message}))

    def start_collection(self) -> None:
        """Start evidence collection in a background thread."""
        language = self._current_language()

        if self.collection_thread and self.collection_thread.is_alive():
            messagebox.showinfo(
                t(language, "dialog.already_running.title"),
                t(language, "status.collection_running"),
            )
            return

        self.progress_var.set(0)
        self.status_var.set(t(language, "status.starting"))
        self._set_busy_state(True)
        self._log(t(language, "log.starting"))

        self.collection_thread = threading.Thread(
            target=self._run_collection,
            args=(language,),
            daemon=True,
        )
        self.collection_thread.start()

    def _run_collection(self, language: str) -> None:
        """Run evidence collection and report generation."""
        try:
            evidence = collect_evidence(
                progress_callback=self._progress_callback,
                language=language,
            )

            self.event_queue.put(
                (
                    "progress",
                    {
                        "percent": 98,
                        "message": t(language, "status.generating_report"),
                    },
                )
            )

            report_path = generate_markdown_report(evidence, language=language)

            self.event_queue.put(
                (
                    "completed",
                    {
                        "report_path": report_path,
                        "language": language,
                    },
                )
            )
        except Exception as exc:
            self.event_queue.put(
                (
                    "failed",
                    {
                        "error": str(exc),
                        "language": language,
                    },
                )
            )

    def _poll_queue(self) -> None:
        """Poll UI events from the background thread."""
        try:
            while True:
                event_type, payload = self.event_queue.get_nowait()

                language = normalize_language(payload.get("language", self._current_language()))

                if event_type == "progress":
                    percent = int(payload["percent"])
                    message = str(payload["message"])

                    self.progress_var.set(percent)
                    self.status_var.set(message)
                    self._log(message)

                elif event_type == "completed":
                    report_path = Path(payload["report_path"])
                    self.latest_report_path = report_path

                    self.progress_var.set(100)
                    self.status_var.set(f"{t(language, 'status.completed')}: {report_path}")
                    self._log(f"{t(language, 'log.completed')} {report_path}")
                    self._set_busy_state(False)

                    messagebox.showinfo(
                        t(language, "dialog.completed.title"),
                        f"{t(language, 'dialog.completed.message')}\n\n{report_path}",
                    )

                elif event_type == "failed":
                    error = str(payload["error"])

                    self.status_var.set(t(language, "status.failed"))
                    self._log(f"{t(language, 'log.error')} {error}")
                    self._set_busy_state(False)

                    messagebox.showerror(
                        t(language, "dialog.failed.title"),
                        f"{t(language, 'dialog.failed.message')}\n\n{error}",
                    )

        except queue.Empty:
            pass

        self.root.after(150, self._poll_queue)

    def open_reports_folder(self) -> None:
        """Open the local reports folder using the operating system file explorer."""
        language = self._current_language()
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        reports_path = REPORTS_DIR.resolve()

        try:
            if sys.platform.startswith("win"):
                os.startfile(reports_path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(reports_path)], check=False)
            else:
                subprocess.run(["xdg-open", str(reports_path)], check=False)
        except Exception as exc:
            messagebox.showerror(
                t(language, "dialog.open_reports_failed.title"),
                f"{t(language, 'dialog.open_reports_failed.message')}\n\n{exc}",
            )


def run_app() -> None:
    """Run the Tkinter application."""
    root = tk.Tk()
    EvidenceCollectorApp(root)
    root.mainloop()