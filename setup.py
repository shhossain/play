from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='play',
    version='0.1',
    author='shhossain',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'play = play:main',
        ],
    },
)