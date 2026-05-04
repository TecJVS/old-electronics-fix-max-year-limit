#!/usr/bin/env python3
"""
old-electronics-fix-max-year-limit

Calendar year matcher for old electronic devices.

Some old devices can only store years inside a limited range. This module finds
older programmable years whose month/day and weekday match a target date for as
long as possible.

The core algorithm does not scan day by day. It compares the relative position
of the next leap day in both calendars. As long as leap days occur after the same
number of elapsed days, the month/day sequence remains identical.

(c) TecJVS 2026

This software is provided without warranty. Please verify results on your device before relying on them.
"""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from calendar_matcher import find_matching_years


class CalendarMatcherApp(tk.Tk):

	def __init__(self) -> None:
		super().__init__()

		self.title("Old Electronics Calendar Year Matcher")
		self.geometry("960x620")
		self.minsize(860, 540)

		self.target_date_var = tk.StringVar(value=date.today().isoformat())
		self.earliest_year_var = tk.StringVar(value="2000")
		self.latest_year_var = tk.StringVar(value="2020")
		self.horizon_years_var = tk.StringVar(value="10")
		self.status_var = tk.StringVar(value="Ready.")

		self._configure_style()
		self._build_layout()
		self._calculate()

	def _configure_style(self) -> None:
		style = ttk.Style(self)
		try:
			style.theme_use("clam")
		except tk.TclError:
			pass

		style.configure("TFrame", padding=8)
		style.configure("Header.TLabel", font=("TkDefaultFont", 16, "bold"))
		style.configure("Hint.TLabel", foreground="#555555")
		style.configure("Treeview", rowheight=28)
		style.configure("Treeview.Heading", font=("TkDefaultFont", 10, "bold"))

	def _build_layout(self) -> None:
		outer = ttk.Frame(self, padding=16)
		outer.pack(fill=tk.BOTH, expand=True)

		header = ttk.Label(
			outer,
			text="Old Electronics Calendar Year Matcher",
			style="Header.TLabel",
		)
		header.pack(anchor=tk.W)

		subtitle = ttk.Label(
			outer,
			text=(
				"Find an older programmable year whose day, month and weekday "
				"match the real calendar for as long as possible."
			),
			style="Hint.TLabel",
		)
		subtitle.pack(anchor=tk.W, pady=(4, 16))

		input_frame = ttk.LabelFrame(outer, text="Settings", padding=12)
		input_frame.pack(fill=tk.X)

		input_frame.columnconfigure(1, weight=1)
		input_frame.columnconfigure(3, weight=1)

		self._add_labeled_entry(input_frame, "Target date (YYYY-MM-DD)", self.target_date_var, 0, 0)
		self._add_labeled_entry(input_frame, "Earliest year", self.earliest_year_var, 0, 2)
		self._add_labeled_entry(input_frame, "Latest year", self.latest_year_var, 1, 0)
		self._add_labeled_entry(input_frame, "Check horizon (years)", self.horizon_years_var, 1, 2)

		button_frame = ttk.Frame(input_frame, padding=(0, 12, 0, 0))
		button_frame.grid(row=2, column=0, columnspan=4, sticky=tk.EW)
		button_frame.columnconfigure(0, weight=1)

		calculate_button = ttk.Button(button_frame, text="Calculate", command=self._calculate)
		calculate_button.grid(row=0, column=1, padx=(0, 8))

		today_button = ttk.Button(button_frame, text="Use today", command=self._use_today)
		today_button.grid(row=0, column=2)

		result_frame = ttk.LabelFrame(outer, text="Results", padding=12)
		result_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 8))

		columns = ("rank", "year", "programmed_date", "working_days", "next_change")
		self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", selectmode="browse")
		self.tree.heading("rank", text="#")
		self.tree.heading("year", text="Programmable year")
		self.tree.heading("programmed_date", text="Set device date to")
		self.tree.heading("working_days", text="Works for days")
		self.tree.heading("next_change", text="Next change date")

		self.tree.column("rank", width=55, anchor=tk.CENTER, stretch=False)
		self.tree.column("year", width=160, anchor=tk.CENTER)
		self.tree.column("programmed_date", width=170, anchor=tk.CENTER)
		self.tree.column("working_days", width=140, anchor=tk.CENTER)
		self.tree.column("next_change", width=220, anchor=tk.CENTER)

		y_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscrollcommand=y_scroll.set)

		self.tree.grid(row=0, column=0, sticky=tk.NSEW)
		y_scroll.grid(row=0, column=1, sticky=tk.NS)

		result_frame.rowconfigure(0, weight=1)
		result_frame.columnconfigure(0, weight=1)

		status = ttk.Label(outer, textvariable=self.status_var, style="Hint.TLabel")
		status.pack(anchor=tk.W)

		self.bind("<Return>", lambda _event: self._calculate())

	def _add_labeled_entry(
		self,
		parent: ttk.Frame,
		label: str,
		variable: tk.StringVar,
		row: int,
		column: int,
	) -> None:
		ttk.Label(parent, text=label).grid(row=row, column=column, sticky=tk.W, padx=(0, 8), pady=6)
		entry = ttk.Entry(parent, textvariable=variable)
		entry.grid(row=row, column=column + 1, sticky=tk.EW, padx=(0, 16), pady=6)

	def _use_today(self) -> None:
		self.target_date_var.set(date.today().isoformat())
		self._calculate()

	def _parse_inputs(self) -> tuple[date, int, int, int]:
		try:
			target = date.fromisoformat(self.target_date_var.get().strip())
		except ValueError as exc:
			raise ValueError("Target date must use the format YYYY-MM-DD.") from exc

		try:
			earliest = int(self.earliest_year_var.get().strip())
			latest = int(self.latest_year_var.get().strip())
			horizon_years = int(self.horizon_years_var.get().strip())
		except ValueError as exc:
			raise ValueError("Years and horizon must be whole numbers.") from exc

		if earliest < 1 or latest < 1:
			raise ValueError("Years must be positive.")
		if earliest > latest:
			raise ValueError("Earliest year must not be later than latest year.")
		if horizon_years < 1:
			raise ValueError("Check horizon must be at least one year.")

		# 365.2425 is the exact average length of the Gregorian year over 400 years.
		horizon_days = round(horizon_years * 365.2425)
		return target, earliest, latest, horizon_days

	def _calculate(self) -> None:
		try:
			target, earliest, latest, horizon_days = self._parse_inputs()
			results = find_matching_years(
				target,
				earliest,
				latest,
				horizon_days=horizon_days,
			)
		except ValueError as exc:
			messagebox.showerror("Invalid input", str(exc))
			return

		self.tree.delete(*self.tree.get_children())

		if not results:
			self.status_var.set(
				f"No matching year found for {target.isoformat()} between {earliest} and {latest}."
			)
			return

		for index, result in enumerate(results, start=1):
			next_change = (
				"No mismatch in horizon"
				if result.next_change_date is None
				else result.next_change_date.isoformat()
			)
			self.tree.insert(
				"",
				tk.END,
				values=(
					index,
					result.programmable_year,
					result.programmed_date.isoformat(),
					result.working_days,
					next_change,
				),
			)

		best = results[0]
		self.status_var.set(
			"Best result: set device to "
			f"{best.programmed_date.isoformat()} "
			f"and keep it for {best.working_days} days."
		)


def main() -> None:
	app = CalendarMatcherApp()
	app.mainloop()


if __name__ == "__main__":
	main()
