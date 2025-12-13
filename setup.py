from setuptools import setup, find_packages

setup(
    name='victor86c_parser',
    version='1.0.1',
    description='Biblioteca Python para decodificar o protocolo de comunicação serial do multímetro VICTOR 86C/86D.',
    author='Amaur Baptista Moreira de Deus',
    author_email='adeus.sjp@gmail.com',
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)