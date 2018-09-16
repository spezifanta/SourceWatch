import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='SourceWatch',
    version='0.0.1',
    author='Alex Kuhrt',
    author_email='alex@qrt.de',
    description='A library to query information of Goldsrc and Source servers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SourceWatch/SourceWatch',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
