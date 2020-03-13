from setuptools import setup

REQUIRED = [
    'click>=7.0',
    'PyShp>=2.0.0'
]
setup(
    name='geepy',
    version=0.1,
    entry_points='''
        [console_scripts]
        geepy=gcli:commands
        ''',
    py_modules=['geepy','gcli'],
    install_requires=REQUIRED
)
