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

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True, order=True)
class MatchResult:
	"""Result for one programmable year."""

	working_days: int
	programmable_year: int
	programmed_date: date
	next_change_date: date | None

	@property
	def works_indefinitely_in_horizon(self) -> bool:
		"""Return True if no mismatch was found within the checked horizon."""
		return self.next_change_date is None


def is_leap_year(year: int) -> bool:
	"""Return True if *year* is a Gregorian leap year."""
	return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def next_february_29_after(day: date) -> date | None:
	"""
	Return the first Gregorian February 29 strictly after *day*.

	The Gregorian leap-year cycle repeats every 400 years, so searching at most
	400 years is mathematically sufficient.
	"""
	for year in range(day.year, day.year + 401):
		if is_leap_year(year):
			leap_day = date(year, 2, 29)
			if leap_day > day:
				return leap_day
	return None


def first_month_day_mismatch(
	current_date: date,
	programmed_date: date,
	*,
	horizon_days: int,
) -> int | None:
	"""
	Return the number of days until month/day first differs, or None.

	Preconditions:
		- current_date and programmed_date have identical month/day.

	The weekday does not need separate simulation here: if both start weekdays
	are equal, both calendars advance by one weekday per elapsed day.

	Complexity:
		O(number of leap days inside the checked horizon), not O(days).
	"""
	if (current_date.month, current_date.day) != (
		programmed_date.month,
		programmed_date.day,
	):
		return 0

	elapsed = 0
	current_cursor = current_date
	programmed_cursor = programmed_date

	while elapsed < horizon_days:
		current_next_leap = next_february_29_after(current_cursor)
		programmed_next_leap = next_february_29_after(programmed_cursor)

		if current_next_leap is None or programmed_next_leap is None:
			return None

		current_offset = (current_next_leap - current_cursor).days
		programmed_offset = (programmed_next_leap - programmed_cursor).days

		next_relevant_offset = min(current_offset, programmed_offset)
		if elapsed + next_relevant_offset > horizon_days:
			return None

		if current_offset != programmed_offset:
			return elapsed + next_relevant_offset

		# Both calendars hit February 29 after the same elapsed time.
		# Move past that day; month/day still agrees on March 1.
		step = current_offset + 1
		current_cursor += timedelta(days=step)
		programmed_cursor += timedelta(days=step)
		elapsed += step

	return None


def valid_programmed_date(target: date, year: int) -> date | None:
	"""
	Return target's month/day in *year*, or None if the date is impossible.

	Example: February 29 is impossible in non-leap years.
	"""
	try:
		return date(year, target.month, target.day)
	except ValueError:
		return None


def find_matching_years(
	target: date,
	earliest_year: int,
	latest_year: int,
	*,
	horizon_days: int = 365 * 10 + 3,
) -> list[MatchResult]:
	"""
	Find programmable years that match target's month/day and weekday.

	Args:
		target: The real date shown by the current calendar.
		earliest_year: First programmable year, inclusive.
		latest_year: Last programmable year, inclusive.
		horizon_days: Maximum number of future days to check.

	Returns:
		Results sorted by best working duration first, then by year.
	"""
	if earliest_year > latest_year:
		raise ValueError("earliest_year must be less than or equal to latest_year")
	if horizon_days < 1:
		raise ValueError("horizon_days must be at least 1")

	results: list[MatchResult] = []

	for year in range(earliest_year, latest_year + 1):
		programmed = valid_programmed_date(target, year)
		if programmed is None:
			continue

		if programmed.weekday() != target.weekday():
			continue

		mismatch = first_month_day_mismatch(
			target,
			programmed,
			horizon_days=horizon_days,
		)

		if mismatch is None:
			results.append(
				MatchResult(
					working_days=horizon_days,
					programmable_year=year,
					programmed_date=programmed,
					next_change_date=None,
				)
			)
		else:
			results.append(
				MatchResult(
					working_days=mismatch,
					programmable_year=year,
					programmed_date=programmed,
					next_change_date=target + timedelta(days=mismatch),
				)
			)

	return sorted(results, key=lambda item: (-item.working_days, item.programmable_year))


def format_result(result: MatchResult) -> str:
	"""Create a human-readable one-line representation of a result."""
	if result.next_change_date is None:
		next_change = "no change needed inside the checked horizon"
	else:
		next_change = f"change again on {result.next_change_date.isoformat()}"

	return (
		f"Set device to {result.programmed_date.isoformat()} "
		f"({result.working_days} days; {next_change})"
	)


def main(argv: Iterable[str] | None = None) -> int:
	"""Small command-line entry point for quick checks."""
	import argparse

	parser = argparse.ArgumentParser(
		description="Find old programmable calendar years that match today's weekday."
	)
	parser.add_argument("--date", default=date.today().isoformat(), help="Target date, YYYY-MM-DD")
	parser.add_argument("--earliest", type=int, default=2000, help="Earliest programmable year")
	parser.add_argument("--latest", type=int, default=2020, help="Latest programmable year")
	parser.add_argument("--horizon", type=int, default=365 * 10 + 3, help="Days to check")

	args = parser.parse_args(list(argv) if argv is not None else None)

	target = date.fromisoformat(args.date)
	results = find_matching_years(
		target,
		args.earliest,
		args.latest,
		horizon_days=args.horizon,
	)

	if not results:
		print(
			"No matching programmable year was found for "
			f"{target.isoformat()} between {args.earliest} and {args.latest}."
		)
		return 1

	for result in results:
		print(format_result(result))

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
