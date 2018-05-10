from setuptools import setup


setup(
	name='pybet',
	version='0.1',
	packages=['pybet'],
	install_requires=['requests', 'bs4'],
	entry_points={
		'console_scripts': ['pybet=pybet.__main__:main']
	})