from setuptools import setup, find_packages

setup(
    name='actinide',
    version='0.1',
    packages=find_packages(),
    scripts=['bin/actinide-repl'],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
        'hypothesis',
    ],
)
