"""
Converts the string names in the code into the displayed text, used for multi language support and easy changes
"""
import json
from resource_path import *


def load_lang(lang):
		with open(resource_path(f"localisations/{lang}.json"), "rt", encoding="utf-8") as f:
			l10n = json.load(f)
		return l10n


def reload():
	global l10n
	try:
		with open("settings.json", "rt") as f:
			loaded_settings = json.load(f)
			language = loaded_settings["language"]
			#should load the language as a string for the file name - without json
	except:
		language = "en-gb"
		print("THERE WAS AN ERROR LOADING SETTINGS WHILE TRYING TO LOAD LANGUAGES.")
	
	# load localisation file
	try:
		l10n = load_lang(language)
	except Exception as e:
		print(f"Error loading language localisation language. {e}\n\nAttempting to load en-gb instead.")
		try:
			l10n = load_lang("en-gb")
		except Exception as e:
			raise BaseException(f"Critical error in loading localisation.\n{e}")

reload()

def l10n_convert(string : str):
	try:
		result = l10n[string]
	except KeyError as e:
		result = "ERROR"
		print(f"Error converting string {string} to the l10n. Likely undefined?\n{e}")
	return result