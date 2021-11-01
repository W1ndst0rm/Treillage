from setuptools import setup, find_packages

import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='treillage',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Unofficial Wrapper library for the Filevine API',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/W1ndst0rm/Treillage",
    author='Levi Jumonville',
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3,<4',
        'pandas>=1,<2',
        'PyYAML>=5,<6',
        'PyJWT>=1.6.4,<2',
        'cryptography>=35,<36'
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
