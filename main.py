#!/usr/bin/env python
# -*- coding: utf-8 -*-

# old-electronics-fix-max-year-limit
# Some old electronic devices can not store the current year in their
# digital calendar anymore, therefore this Python script can calculate
# an earlier year for which day, month and weekday match for as many
# days as possible with those in the current year.
# This is useful if you still would like to have the correct day, month
# and weekday (but not the year) i.e. shown on a LCD display.
# Disclaimer: I do not take any responsibility. Use at your own risk.

import datetime

earliest_year_programmable = 2000 # i.e. the manufacturing year of the device
latest_year_programmable = 2020 # i.e. the latest year which can be stored in the device

current_time = datetime.datetime.now()

match_years = []

y = earliest_year_programmable
while y < latest_year_programmable:
	stime = str(current_time.day) + "/" + str(current_time.month) + "/" + str(y)
	test_timestamp = datetime.datetime.strptime(stime, "%d/%m/%Y")
	if test_timestamp.weekday() == current_time.weekday():
		match_years.append(test_timestamp)
	y += 1

if match_years == []:
	print("Sorry, no matching years have been found in the years between", earliest_year_programmable, "and", latest_year_programmable, ":(")
else:
	for match_year in match_years:
		count_current_timestamp = current_time
		count_test_timestamp = match_year
		for i in range(5*365):
			count_current_timestamp += datetime.timedelta(days=1)
			count_test_timestamp += datetime.timedelta(days=1)
			if count_current_timestamp.day != count_test_timestamp.day and count_current_timestamp.month != count_test_timestamp.month:
				found_year = True
				print("Programming year [", match_year.year, "] at current date", current_time, "works for [", i, "days ], next date change must be done on", count_current_timestamp)
				break

input()
