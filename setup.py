import pathlib

from setuptools import find_packages, setup


VERSION = "0.0.1-alpha.1"

REPO_ROOT = pathlib.Path(__file__).parent

with open(REPO_ROOT / "README.md", encoding="utf-8") as f:
    README = f.read()

REQUIREMENTS = []

setup(
    name="comp",
    version=VERSION,
    description="Lightweight framework for structured and repeatable model validation",
    long_description=README,
    long_description_content_type="text/markdown",
    author="datavaluepeople",
    url="https://github.com/datavaluepeople/comp",
    license="MIT",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    python_requires=">=3.7",
)
