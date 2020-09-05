from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='filevine',
    version='0.1.3',
    description='Wrapper library for the Filevine API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/W1ndst0rm/Filevine",
    author='Levi Jumonville',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'pandas',
        'PyYAML'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Legal Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet"
    ],
    python_requires='>=3.8'
)
