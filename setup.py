from pathlib import Path

from setuptools import setup, find_packages

PACKAGE_ROOT = Path(__file__).resolve().parent


def load_python_version(default: str,
                        version_file_path: Path = Path('.python-version'),
                        ) -> str:
    '''Retrieves the current project python version from the .python-version file

    returns default value if the version file does not exist or the path is wrong, or the file is empty
    '''
    if not isinstance(version_file_path, Path):
        version_file_path = Path(version_file_path)
    if not version_file_path.exists():
        return default
    with open(version_file_path, ) as file:
        version = file.read()
    if not version:
        return default
    return '>=' + version


def read_requirements(requirements_path: Path):
    return requirements_path.read_text().strip()


project_python_version = load_python_version(default='>=3.10')

setup(
    name='parser_gibdd',
    author='Vlad Tabakov',
    packages=find_packages(where=str(PACKAGE_ROOT), include='parser_gibdd', exclude='./tests'),
    include_package_data=True,
    install_requires=read_requirements(PACKAGE_ROOT / "requirements.txt"),
    extras_require={
        "dev": read_requirements(PACKAGE_ROOT / "requirements-dev.txt"),
    },
    entry_points={
        'console_scripts': [
            'gibdd = parser_gibdd.interface.shell:main'
        ]
    },
    python_requires=project_python_version,
    setuptools_git_versioning={
        "enabled": True,
    },
    setup_requires=["setuptools-git-versioning"],

)
