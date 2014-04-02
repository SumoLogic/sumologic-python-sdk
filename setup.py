import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "sumologic-sdk",
    version = "0.1.2",
    packages = find_packages(),

    install_requires = ['requests>=2.2.1'],

    # PyPI metadata
    author = "Yoway Buorn",
    author_email = "yoway@sumologic.com",
    description = "Sumo Logic Python SDK",
    license = "PSF",
    keywords = "sumo logic python sdk rest api log management analytics logreduce splunk security siem collector forwarder",
    url = "https://github.com/SumoLogic/sumologic-python-sdk",
	zip_safe = True
)
