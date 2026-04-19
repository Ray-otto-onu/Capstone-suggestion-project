import tkinter as tk
from tkinter import ttk, messagebox


# ── Placeholder course list (swap these out later) ──────────────────────────
COURSE_OPTIONS = [
    "",
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
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f2f5")
        self.root.resizable(True, True)

        # List that holds each (frame, StringVar) pair for course rows
        self.course_rows = []

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Outer scroll canvas so the window can grow ──────────────────────
        canvas = tk.Canvas(self.root, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Inner frame that holds everything
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
        # Mouse-wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._build_header()
        self._build_name_card()
        self._build_courses_card()

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

    def _card(self, title):
        """Create a white card with a title label and return the card body frame."""
        wrapper = tk.Frame(self.inner, bg="#f0f2f5", pady=10, padx=20)
        wrapper.pack(fill="x")

        card = tk.Frame(wrapper, bg="white", bd=0, relief="flat",
                        highlightbackground="#d1d5db", highlightthickness=1)
        card.pack(fill="x")

        title_bar = tk.Frame(card, bg="#3498db", pady=10, padx=16)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text=title, font=("Helvetica", 13, "bold"),
                 fg="white", bg="#3498db").pack(anchor="w")

        body = tk.Frame(card, bg="white", padx=16, pady=14)
        body.pack(fill="x")
        return body

    # ── Name Card ────────────────────────────────────────────────────────────

    def _build_name_card(self):
        body = self._card("Student Name")

        tk.Label(body, text="Full Name:", font=("Helvetica", 11),
                 bg="white", fg="#374151").grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(body, textvariable=self.name_var, font=("Helvetica", 11), width=36)
        name_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12))

        save_btn = tk.Button(
            body, text="Save Name", command=self._save_name,
            bg="#3498db", fg="white", font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=6, cursor="hand2",
            activebackground="#2980b9", activeforeground="white",
        )
        save_btn.grid(row=1, column=1, sticky="w")

        self.name_saved_label = tk.Label(body, text="", font=("Helvetica", 10, "italic"),
                                         bg="white", fg="#16a34a")
        self.name_saved_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

        body.columnconfigure(0, weight=1)

    def _save_name(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("No Name", "Please enter a name before saving.")
            return
        self.name_saved_label.config(text=f"✔  Saved: {name}")

    # ── Courses Card ─────────────────────────────────────────────────────────

    def _build_courses_card(self):
        body = self._card("Classes Already Taken")
        self.courses_body = body

        tk.Label(body, text="Select each course you have already completed:",
                 font=("Helvetica", 11), bg="white", fg="#374151").pack(anchor="w", pady=(0, 10))

        # Container for dynamic course rows
        self.courses_container = tk.Frame(body, bg="white")
        self.courses_container.pack(fill="x")

        # Start with two rows
        self._add_course_row()
        self._add_course_row()

        # Separator
        sep = ttk.Separator(body, orient="horizontal")
        sep.pack(fill="x", pady=12)

        # Add Class button
        add_btn = tk.Button(
            body,
            text="＋  Add Class",
            command=self._add_course_row,
            bg="#10b981", fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#059669", activeforeground="white",
        )
        add_btn.pack(anchor="w")

        # Save courses button
        save_btn = tk.Button(
            body,
            text="Save Courses",
            command=self._save_courses,
            bg="#3498db", fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#2980b9", activeforeground="white",
        )
        save_btn.pack(anchor="w", pady=(8, 0))

        self.courses_saved_label = tk.Label(body, text="", font=("Helvetica", 10, "italic"),
                                            bg="white", fg="#16a34a")
        self.courses_saved_label.pack(anchor="w", pady=(4, 0))

    def _add_course_row(self):
        row_index = len(self.course_rows) + 1
        row_frame = tk.Frame(self.courses_container, bg="white", pady=4)
        row_frame.pack(fill="x")

        tk.Label(row_frame, text=f"Course {row_index}:",
                 font=("Helvetica", 10), bg="white", fg="#6b7280",
                 width=10, anchor="w").pack(side="left")

        var = tk.StringVar(value="")
        combo = ttk.Combobox(row_frame, textvariable=var, values=COURSE_OPTIONS,
                             state="readonly", font=("Helvetica", 10), width=28)
        combo.pack(side="left", padx=(0, 10))

        # Remove button
        def remove(f=row_frame, v=var):
            self.course_rows = [(fr, vr) for fr, vr in self.course_rows if fr is not f]
            f.destroy()
            self._renumber_rows()

        rm_btn = tk.Button(row_frame, text="✕", command=remove,
                           bg="#ef4444", fg="white", font=("Helvetica", 9, "bold"),
                           relief="flat", padx=6, pady=2, cursor="hand2",
                           activebackground="#dc2626", activeforeground="white")
        rm_btn.pack(side="left")

        self.course_rows.append((row_frame, var))

    def _renumber_rows(self):
        for i, (frame, _) in enumerate(self.course_rows):
            label = frame.winfo_children()[0]   # first child is the Label
            label.config(text=f"Course {i + 1}:")

    def _save_courses(self):
        selected = [v.get() for _, v in self.course_rows if v.get()]
        if not selected:
            messagebox.showwarning("No Courses", "Please select at least one course.")
            return
        self.courses_saved_label.config(
            text=f"✔  {len(selected)} course(s) saved."
        )
        # (Later you can persist `selected` to a file or database here.)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()

    # Nicer default ttk style
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TCombobox", padding=4)
    style.configure("TEntry", padding=4)

    app = StudentTrackerApp(root)
    root.mainloop()