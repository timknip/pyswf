from setuptools import setup, find_packages
setup(name='pyswf',
      version='1.1',
      description='SWF Parsing Utilities',
      author='Tim Knip',
      author_email='tim@floorplanner.com',
      url='https://github.com/timknip/pyswf',
      install_requires = ["lxml==2.3", "PIL==1.1.7"],
      packages=find_packages()
      )