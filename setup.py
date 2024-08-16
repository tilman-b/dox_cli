from setuptools import setup, find_packages

setup(
    name="dox_cli",
    version="1.0.0",
    description="simple cli tool to interact with SAP document extraction service",
    packages=find_packages(),
    install_requires=[
        "click==8.1.7",
        "requests==2.32.3",
        "requests-oauthlib==2.0.0",
        "oauthlib~=3.2.2",
    ],
    entry_points={"console_scripts": ["dox = dox_cli.main:run"]},
)
