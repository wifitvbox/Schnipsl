#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
import sys
import os
import importlib
import importlib.util
import traceback
import re

# Non standard modules (install with pip)


ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules


class PluginManager():
	''' loads all schnipsl plugins
	'''

	def __init__(self, modref, plugin_root_dir):
		self.plugins = {}
		regex = re.compile(r'^spl_.+.py$')
		try:
			plugin_path = os.path.realpath(os.path.join(
				os.path.dirname(__file__), plugin_root_dir))
			list_subfolders_with_paths = [
				f.path for f in os.scandir(plugin_path) if f.is_dir()]
			for sub_folder in list_subfolders_with_paths:
				list_file_infos = [f for f in os.scandir(
					sub_folder) if f.is_file()]
				for file_info in list_file_infos:
					if regex.match(file_info.name):
						print(file_info.path)

						module_spec = importlib.util.spec_from_file_location(file_info.name, file_info.path)
						my_module = importlib.util.module_from_spec(module_spec)
						module_spec.loader.exec_module(my_module)

						instance = my_module.SplPlugin(modref)
						instance.run()
						self.plugins[file_info.name] =instance
		except Exception as e:
			print("Can't load plugin "+str(e))
			traceback.print_exc(file=sys.stdout)
