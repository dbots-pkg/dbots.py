import setuptools
import re

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

version = ''
with open('dbots/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

with open("README.md", "r") as f:
    readme = f.read()

setuptools.setup(
    name = "dbots",
    version = version,
    author = "Snazzah",
    description = "Discord bot list poster and stats retriever",
    long_description = readme,
    long_description_content_type = "text/markdown",
    url = "https://github.com/dbots-pkg/dbots.py",
    packages = setuptools.find_packages(),
    install_requires = requirements,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
)