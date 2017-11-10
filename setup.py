from setuptools import setup, find_packages

setup(
    name="sumologic-sdk",
    version="0.1.7",
    packages=find_packages(),
    install_requires=['requests>=2.2.1', 'aiohttp>=2.3.1'],
    # PyPI metadata
    author="Yoway Buorn, Melchi Salins",
    author_email="it@sumologic.com, melchisalins@icloud.com",
    description="Sumo Logic Python SDK",
    license="PSF",
    keywords="sumologic python sdk rest api log management analytics logreduce splunk security siem collector forwarder",
    url="https://github.com/SumoLogic/sumologic-python-sdk",
    zip_safe=True
)
