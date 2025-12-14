from setuptools import setup, find_packages

# Lê o conteúdo do README.md para usar como descrição longa no PyPI
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Biblioteca Python para decodificar o protocolo de comunicação serial do multímetro VICTOR 86C/86D."

setup(
    name='victor86c_parser',
    version='1.0.1.1',
    description='Biblioteca Python para decodificar o protocolo de comunicação serial do multímetro VICTOR 86C/86D.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Amauri B. M. de Deus', 
    author_email='adeus.sjp@gmail.com',
    url='https://github.com/Gungsu/victor86c_library',
    project_urls={
        "Bug Tracker": "https://github.com/Gungsu/victor86c_library/issues",
        "Source Code": "https://github.com/Gungsu/victor86c_library",
    },
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)