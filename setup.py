from setuptools import setup, find_packages
from os.path import join, dirname, abspath
import io

here = abspath(dirname(__file__))

with open(join(here, 'VERSION')) as VERSION_FILE:
    __versionstr__ = VERSION_FILE.read().strip()


with open(join(here, 'requirements.txt')) as REQUIREMENTS:
    INSTALL_REQUIRES = REQUIREMENTS.read().split('\n')


with io.open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sumologic-sdk",
    version=__versionstr__,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    # PyPI metadata
    author="SumoLogic, Yoway Buorn, Melchi Salins",
    author_email="it@sumologic.com, melchisalins@icloud.com, apps-team@sumologic.com",
    description="Sumo Logic Python SDK",
    license="PSF",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="sumologic python sdk rest api log management analytics logreduce security siem collector forwarder",
    url="https://github.com/SumoLogic/sumologic-python-sdk",
    zip_safe=True
)
