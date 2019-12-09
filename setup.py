# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in erpnext_telegram_integration/__init__.py
from erpnext_telegram_integration import __version__ as version

setup(
	name='erpnext_telegram_integration',
	version=version,
	description='Telegram Integration For Frappe - Erpnext',
	author='Youssef Restom',
	author_email='Youssef@totrox.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
