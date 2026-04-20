import tkinter as tk
from tkinter import ttk, messagebox


# ── Placeholder course list (swap these out later) ───────────────────────────
ALL_COURSES = [
    "Temp 1",
    "Temp 2",
    "Temp 3",
    "Temp 4",
    "Temp 5",
]


class StudentTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Course Tracker")
        self.root.geometry("700x620")
        self.root.configure(bg="#f0f2f5")
        self.root.resizable(True, True)

        # Each entry: {"frame": Frame, "var": StringVar, "combo": Combobox, "btn": Button}
        self.course_rows = []

        self._build_ui()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        canvas = tk.Canvas(self.root, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(canvas, bg="#f0f2f5")
        self.inner_id = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(self.inner_id, width=e.width),
        )
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )

        self._build_header()
        self._build_name_card()
        self._build_courses_card()
        self._build_save_bar()

    def _card(self, title):
        wrapper = tk.Frame(self.inner, bg="#f0f2f5", pady=10, padx=20)
        wrapper.pack(fill="x")

        card = tk.Frame(
            wrapper, bg="white", bd=0, relief="flat",
            highlightbackground="#d1d5db", highlightthickness=1,
        )
        card.pack(fill="x")

        title_bar = tk.Frame(card, bg="#2c3e50", pady=10, padx=16)
        title_bar.pack(fill="x")
        tk.Label(
            title_bar, text=title, font=("Helvetica", 13, "bold"),
            fg="white", bg="#2c3e50",
        ).pack(anchor="w")

        body = tk.Frame(card, bg="white", padx=16, pady=14)
        body.pack(fill="x")
        return body

    def _build_header(self):
        header = tk.Frame(self.inner, bg="#2c3e50", pady=18)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Student Course Tracker",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="#2c3e50",
        ).pack()

    # ── Name Card ─────────────────────────────────────────────────────────────

    def _build_name_card(self):
        body = self._card("Student Name")

        tk.Label(
            body, text="Full Name:", font=("Helvetica", 11),
            bg="white", fg="#374151",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.name_var = tk.StringVar()
        ttk.Entry(
            body, textvariable=self.name_var, font=("Helvetica", 11), width=40,
        ).grid(row=1, column=0, sticky="ew")

        body.columnconfigure(0, weight=1)

    # ── Courses Card ──────────────────────────────────────────────────────────

    def _build_courses_card(self):
        body = self._card("Classes Already Taken")
        self.courses_body = body

        tk.Label(
            body,
            text="Select each course you have already completed:",
            font=("Helvetica", 11), bg="white", fg="#374151",
        ).pack(anchor="w", pady=(0, 10))

        self.courses_container = tk.Frame(body, bg="white")
        self.courses_container.pack(fill="x")

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=12)

        tk.Button(
            body,
            text="＋  Add Class",
            command=self._add_course_row,
            bg="#10b981", fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#059669", activeforeground="white",
        ).pack(anchor="w")

        # Start with two rows
        self._add_course_row()
        self._add_course_row()

    # ── Save Bar ──────────────────────────────────────────────────────────────

    def _build_save_bar(self):
        bar = tk.Frame(self.inner, bg="#f0f2f5", pady=14, padx=20)
        bar.pack(fill="x")

        tk.Button(
            bar,
            text="💾  Save All",
            command=self._save_all,
            bg="#3498db", fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat", padx=24, pady=10, cursor="hand2",
            activebackground="#2980b9", activeforeground="white",
        ).pack(side="left")

        self.save_status = tk.Label(
            bar, text="", font=("Helvetica", 10, "italic"),
            bg="#f0f2f5", fg="#16a34a",
        )
        self.save_status.pack(side="left", padx=14)

    # ── Course Row Logic ──────────────────────────────────────────────────────

    def _add_course_row(self):
        row_index = len(self.course_rows) + 1

        row_frame = tk.Frame(self.courses_container, bg="white", pady=4)
        row_frame.pack(fill="x")

        tk.Label(
            row_frame,
            text=f"Course {row_index}:",
            font=("Helvetica", 10), bg="white", fg="#6b7280",
            width=10, anchor="w",
        ).pack(side="left")

        var = tk.StringVar(value="")
        combo = ttk.Combobox(
            row_frame, textvariable=var,
            state="readonly", font=("Helvetica", 10), width=28,
        )
        combo.pack(side="left", padx=(0, 10))

        rm_btn = tk.Button(
            row_frame, text="✕",
            bg="#ef4444", fg="white",
            font=("Helvetica", 9, "bold"),
            relief="flat", padx=6, pady=2, cursor="hand2",
            activebackground="#dc2626", activeforeground="white",
        )
        rm_btn.pack(side="left")

        row = {"frame": row_frame, "var": var, "combo": combo, "btn": rm_btn}
        self.course_rows.append(row)

        var.trace_add("write", lambda *_: self._on_selection_changed())
        rm_btn.config(command=lambda r=row: self._remove_row(r))

        self._refresh_all_combos()
        self._update_remove_buttons()

    def _remove_row(self, row):
        if len(self.course_rows) <= 1:
            return
        self.course_rows.remove(row)
        row["frame"].destroy()
        self._renumber_rows()
        self._refresh_all_combos()
        self._update_remove_buttons()

    def _renumber_rows(self):
        for i, row in enumerate(self.course_rows):
            label = row["frame"].winfo_children()[0]
            label.config(text=f"Course {i + 1}:")

    def _on_selection_changed(self):
        self._refresh_all_combos()

    def _refresh_all_combos(self):
        """
        Rebuild each combobox's option list so it only shows courses
        that haven't been chosen by a *different* row.
        """
        chosen = {row["var"].get() for row in self.course_rows if row["var"].get()}

        for row in self.course_rows:
            current = row["var"].get()
            taken_by_others = chosen - ({current} if current else set())
            available = [c for c in ALL_COURSES if c not in taken_by_others]

            row["combo"].config(values=available)

            if current and current not in available:
                row["var"].set("")

    def _update_remove_buttons(self):
        """Disable the remove button when only one row remains."""
        only_one = len(self.course_rows) == 1
        for row in self.course_rows:
            if only_one:
                row["btn"].config(state="disabled", bg="#9ca3af", cursor="arrow")
            else:
                row["btn"].config(state="normal", bg="#ef4444", cursor="hand2")

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save_all(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a student name before saving.")
            return

        selected_courses = [row["var"].get() for row in self.course_rows if row["var"].get()]
        if not selected_courses:
            messagebox.showwarning("No Courses", "Please select at least one course before saving.")
            return

        summary = (
            f"Saved successfully!\n\n"
            f"Student: {name}\n"
            f"Courses ({len(selected_courses)}): {', '.join(selected_courses)}"
        )
        messagebox.showinfo("Saved", summary)
        self.save_status.config(
            text=f"✔  Saved {name} · {len(selected_courses)} course(s)"
        )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TCombobox", padding=4)
    style.configure("TEntry", padding=4)

    app = StudentTrackerApp(root)
    root.mainloop()