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

class quran_search:
	def __init__(self, no_tashkil=False, no_hamza=False, from_surah=False, from_ayah=False, to_surah=False, to_ayah=False):
		self.no_tashkil = no_tashkil
		self.no_hamza = no_hamza
		self.from_surah = from_surah
		self.from_ayah = from_ayah
		self.to_surah = to_surah
		self.to_ayah = to_ayah
		self.conn = sqlite3.connect('Verses.db')
		self.cursor = self.conn.cursor()

	def __del__(self):
		self.conn.close()

	def search(self, text_to_search):
		# set default values
		from_surah = self.from_surah
		to_surah = self.to_surah
		from_ayah = self.from_ayah
		to_ayah = self.to_ayah
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



		#set the query
		if to_ayah:
			from_ayah = 1 if from_ayah is False else from_ayah
			query = f"SELECT text, numberInSurah, sura_name, sura_number FROM quran WHERE text LIKE '%' || ? || '%' AND (number >= {from_ayah} AND number <= {to_ayah})"
		elif from_ayah and to_ayah is False:
			query = f"SELECT text, numberInSurah, sura_name, sura_number FROM quran WHERE text LIKE '%' || ? || '%' AND (number >= {from_ayah})"
		else:
			query = f"SELECT text, numberInSurah, sura_name, sura_number FROM quran WHERE text LIKE '%' || ? || '%'"

		if self.no_tashkil:
			# remove all tashkil from the text to search
			tashkil = ['َ', 'ً', 'ُ', 'ٌ', 'ِ', 'ٍ', 'ْ', 'ّ']
			for char in tashkil:
				text_to_search = text_to_search.replace(char, '')
				query = query.replace('WHERE text', f"WHERE REPLACE(text, '{char}', '')")
				query = query.replace('REPLACE(text', f"REPLACE(REPLACE(text, '{char}', '')")
		if self.no_hamza:
			# replace all hamzat with 'ا'
			hamzat = ['أ', 'إ', 'آ', 'ء', 'ؤ']
			for char in hamzat:
				text_to_search = text_to_search.replace(char, 'ا')
				# replace all hamzat with 'ا' in the SQL query
				query = query.replace('WHERE text', f"WHERE REPLACE(text, '{char}', 'ا')")
				query = query.replace('REPLACE(text', f"REPLACE(REPLACE(text, '{char}', 'ا')")
		self.cursor.execute(query, (text_to_search,))

		result = self.cursor.fetchall()
		return result
