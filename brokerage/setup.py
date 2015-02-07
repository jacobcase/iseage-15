
from setuptools import setup, find_packages

setup(
        name='brokerage',
        version='1.0',
        packages=['brokerage',
            'brokerage.tools'],
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
