from setuptools import setup, find_packages

setup(
    name='actinide',
    version='0.1.1',
    packages=find_packages(
        exclude=['tests', 'tests.*', '*.__pycache__', '*.__pycache__.*'],
    ),
    scripts=['bin/actinide-repl'],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
        'hypothesis',
    ],
)
