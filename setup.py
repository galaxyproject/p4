from setuptools import setup

setup(name="p4",
      version='1.0',
      description="proper prior planning...",
      author="Eric Rasche",
      author_email="esr@tamu.edu",
      install_requires=['pygithub3', 'pyyaml', 'parsedatetime'],
      tests_require=['nose', 'attrdict'],
      license='GPL3'
      )
