from setuptools import setup

setup(
    name="ikt111",
    version="0.1.0",
    description="Games for IKT111",
    author="Jahn Thomas Fidje, Nicolai Eliassen Pedersen",
    author_email="jtfidje@gmail.com, nicolaiep@uia.no",
    packages=["ikt111_games"],
    install_requires=[
        "numpy==1.19.1",
        "pygame==2.0.0"
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)