from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent

long_description = (this_directory / "README.md").read_text()
with open((this_directory / "requirements.txt"), 'r') as f:
    install_requires = f.read().splitlines()

setup(name='DuckdbIS',

      version='0.2.6',

      description='Class for interacting with Duckdb databases',
      
      long_description=long_description,
      long_description_content_type='text/markdown',

      url='C:/Users/iain.shepherd/OneDrive - National Grid/Python/Imports/DuckdbIS',

      author='Iain Shepherd',

      author_email='iain.shepherd@nationalgrideso.com',

      license='MIT',

      packages = find_packages(),
      
      install_requires = install_requires,

      zip_safe=False)

