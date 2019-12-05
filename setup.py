import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python_enigma",
    version="1.2.0dev4",
    author="Zachary Adam-MacEwen",
    author_email="zadammac@kenshosec.com",
    description="A simple module which adds Enigma Machine-emulating functionality to your python projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZAdamMac/python-enigma",
    packages=setuptools.find_packages()
)
