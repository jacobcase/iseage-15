
from setuptools import setup, find_packages

setup(
        name='banking',
        version='1.0',
        packages=['banking'],
        zip_safe=False,
        include_package_data=True,
        install_requires=['tornado', 'flask', 'flask-sqlalchemy']
)
