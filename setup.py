# coding: utf-8
"""Setup config file to package the configuration database."""
from os import walk, listdir
from setuptools import find_packages
from os.path import join
from setuptools import setup
import csst_client


def package_files(directory):
    """Get list of data files to add to the package."""
    paths = []
    for (path, _, file_names) in walk(directory):
        for filename in file_names:
            paths.append(join('..', path, filename))
    return paths


with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()

setup(name='csst_dfs_api_local',
      version=csst_client.__version__,
      author='CSST DFS Team.',
      description='CSST DFS Local APIs Library.',
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      url='',
      include_package_data=True,
      packages=['csst/dfs/api/local/ifs','csst/dfs/api/local/common'],
      install_requires=[
      ],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3 :: Only"
      ]
)
