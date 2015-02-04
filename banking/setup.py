
from setuptools import setup, find_packages

setup(
        name='banking',
        version='1.0',
        packages=['banking',
            'banking.tools'],
        zip_safe=False,
        include_package_data=True,
        install_requires=[
            'tornado', 
            'passlib', 
            'flask', 
            'pymysql',
            'sqlalchemy', 
            'flask-sqlalchemy']
)
