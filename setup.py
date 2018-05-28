from setuptools import setup, find_packages


setup(
    name='pybet',
    version='0.2',
    packages=find_packages(),
    install_requires=['requests', 'bs4'],
    entry_points={
        'console_scripts': ['pybet=pybet.__main__:main']
    })
