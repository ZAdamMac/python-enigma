import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python_enigma",
    version="1.3.1",
    author="Zachary Adam-MacEwen",
    maintainer="Jeffrey P Goldberg",
    maintainer_email="jeffrey@goldmark.org",
    description="A simple module which adds Enigma Machine-emulating functionality to your python projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://github.com/ZAdamMac/python-enigma",
    packages=setuptools.find_packages()
)
