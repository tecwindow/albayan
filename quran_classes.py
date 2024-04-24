"""
This file is part of the Qurani project, created by Nacer Baaziz.
Copyright (c) 2023 Nacer Baaziz
Qurani is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Qurani is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Qurani. If not, see https://www.gnu.org/licenses/.
You are free to modify this file, but please keep this header.
For more information, visit: https://github.com/baaziznasser/qurani
"""

#code start here


import sqlite3

class quran_mgr:
	def __init__(self):
		self.show_ayah_number = True
		self.aya_to_line = False
		self.current_pos = 1
		self.max_pos = 604
		self.type = 0
		self.data_list = []
		self.conn = None
		self.cursor = None
		self.text = ""

	def load_quran(self, db_path):
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()

	def get_surah(self, surah_number):
		self.current_pos = surah_number
		self.max_pos = 114
		self.type = 1
		self.current_pos = self.max_pos if self.current_pos > self.max_pos else self.current_pos

		self.cursor.execute(f"SELECT * FROM quran WHERE sura_number={surah_number}")
		rows = self.cursor.fetchall()
		self.data_list = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], None, None) for row in rows]
		return self.get_text()

	def get_hizb(self, hizb_number):
		self.current_pos = hizb_number
		self.max_pos = 60
		self.type = 3
		self.current_pos = self.max_pos if self.current_pos > self.max_pos else self.current_pos

		self.cursor.execute(f"SELECT * FROM quran WHERE hizb={hizb_number}")
		rows = self.cursor.fetchall()
		self.data_list = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], None, None) for row in rows]
		return self.get_text()

	def get_juzz(self, juzz_number):
		self.current_pos = juzz_number
		self.max_pos = 30
		self.type = 4
		self.current_pos = self.max_pos if self.current_pos > self.max_pos else self.current_pos
		self.cursor.execute(f"SELECT * FROM quran WHERE juz={juzz_number}")
		rows = self.cursor.fetchall()
		self.data_list = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], None, None) for row in rows]
		return self.get_text()

	def get_quarter(self, quarter_number):
		self.current_pos = quarter_number
		self.max_pos = 240
		self.type = 2
		self.current_pos = self.max_pos if self.current_pos > self.max_pos else self.current_pos

		self.cursor.execute(f"SELECT * FROM quran WHERE hizbQuarter={quarter_number}")
		rows = self.cursor.fetchall()
		self.data_list = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], None, None) for row in rows]
		return self.get_text()

	def get_page(self, page_number):
		self.current_pos = page_number
		self.max_pos = 604
		self.type = 0
		self.current_pos = self.max_pos if self.current_pos > self.max_pos else self.current_pos

		self.cursor.execute(f"SELECT * FROM quran WHERE page={page_number}")
		rows = self.cursor.fetchall()
		self.data_list = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], None, None) for row in rows]
		return self.get_text()

	def get_range(self, from_surah = False, from_ayah = False, to_surah = False, to_ayah = False):
		self.current_pos = -1
		self.max_pos = -1
		self.type = 5

		#check from_surah real number
		if from_surah >= 1:
			self.cursor.execute(f"select number from quran WHERE sura_number = {from_surah}")
			result = self.cursor.fetchall()
			if from_ayah < 1:
				from_ayah = 1
			elif from_ayah > len(result):
				from_ayah = len(result	)
			else:
				from_ayah = int(result[0][0])+(int(from_ayah)-1)

		#check to_surah real number
		if to_surah >= 1:
			self.cursor.execute(f"select number from quran WHERE sura_number = {to_surah}")
			result = self.cursor.fetchall()
			if to_ayah < 1:
				to_ayah = len(result)
			elif to_ayah > len(result):
				to_ayah = len(result	)
			else:
				to_ayah = int(result[0][0])+(int(to_ayah)-1)

		if to_ayah:
			from_ayah = 1 if from_ayah is False else from_ayah
			query = f"SELECT * FROM quran WHERE number BETWEEN {from_ayah} AND {to_ayah}"
		elif from_ayah and to_ayah is False:
			query = f"SELECT * FROM quran WHERE  number >= {from_ayah}"
		else:
			query = f"SELECT * FROM quran WHERE number > 1'"
		self.cursor.execute(query)
		rows = self.cursor.fetchall()
		self.data_list = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], None, None) for row in rows]
		return self.get_text()


	def next(self):
		if self.current_pos >= self.max_pos:
			return ""
		self.current_pos += 1
		if self.type == 0:
			return self.get_page(self.current_pos)
		elif self.type == 1:
			return self.get_surah(self.current_pos)
		elif self.type == 2:
			return self.get_quarter(self.current_pos)
		elif self.type == 3:
			return self.get_hizb(self.current_pos)
		else:
			return self.get_juzz(self.current_pos)


	def back(self):
		if self.current_pos <= 1:
			return ""
		self.current_pos -= 1

		if self.type == 0:
			return self.get_page(self.current_pos)
		elif self.type == 1:
			return self.get_surah(self.current_pos)
		elif self.type == 2:
			return self.get_quarter(self.current_pos)
		elif self.type == 3:
			return self.get_hizb(self.current_pos)
		else:
			return self.get_juzz(self.current_pos)


	def goto(self, goto):
		if goto > self.max_pos:
			return ""
		self.current_pos = goto

		if self.type == 0:
			return self.get_page(self.current_pos)
		elif self.type == 1:
			return self.get_surah(self.current_pos)
		elif self.type == 2:
			return self.get_quarter(self.current_pos)
		elif self.type == 3:
			return self.get_hizb(self.current_pos)
		else:
			return self.get_juzz(self.current_pos)


	def get_text(self):
		if not self.data_list:
			return ""

		text = ""
		start = 0

		for ayah_index, ayah in enumerate(self.data_list):
			ayah_text = ayah[0]
			ayah_number = ayah[4]
			if int(ayah_number) == 1:
				text += f"{ayah[2]} {ayah[3]}\n|\n"
				if  ayah[3] != 1:
					ayah_text = ayah_text.replace("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", f"بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n")

			if self.show_ayah_number:
				ayah_text += f" ({ayah_number})"

			if self.aya_to_line:
				ayah_text = f"{ayah_text}\n"
			else:
				ayah_text += " "

			text += ayah_text

			end = start + len(ayah_text)
			self.data_list[ayah_index] += (start, end)
			start = end+1

		text += "|"
		self.text = text
		return text
