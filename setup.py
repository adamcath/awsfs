from setuptools import setup

setup(
    name='awsfs',
    version='0.1.0.dev1',
    description='Treat AWS resources like a filesystem for command-line bliss.',
    long_description=open('README.rst').read(),
    url='https://github.com/adamcath/awsfs',
    author='Adam Cath',
    author_email='adam.cath@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='aws fuse cloud boto tools iaas',
    packages=['awsfs'],
    install_requires=['boto3>=1.2', 'fusepy>=2', 'botocore>=1.3'],
    entry_points={
        'console_scripts': ['awsfs=awsfs.__main__:main']
    }
)
