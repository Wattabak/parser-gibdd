from pkg_resources import parse_requirements
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gibdd_crashes',
    version='0.1',
    author="Vlad Tabakov",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="./parser_gibdd", include="parser_gibdd", exclude="./tests"),
    include_package_data=True,
    install_requires=[str(ir.key) for ir in parse_requirements("requirements.txt")],
    entry_points='''
        [console_scripts]
        gibdd=parser_gibdd.cli.shell:main
    ''',
    python_requires='>=3.8',
)
