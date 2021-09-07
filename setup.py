from setuptools import setup

setup(
    name="ikt111",
    version="1.0.0",
    description="Games for IKT111",
    author="Jahn Thomas Fidje, Nicolai Eliassen Pedersen",
    author_email="jtfidje@gmail.com, nicolaiep@uia.no",
    packages=["ikt111_games"],
    install_requires=[
        "numpy==1.19.1",
        "pygame==2.0.0"
    ]
)