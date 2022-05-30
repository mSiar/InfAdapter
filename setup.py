import os
from setuptools import setup


def read():
    return open(os.path.join(os.path.dirname(__file__), "README.md")).read()


setup(
    name="auto_tuner",
    version="0.0.1",
    keyword="ML Inference Service Autoscaling Auto-Configuration Kubernetes Cloud Computing",
    packages=["auto_tuner"],
    long_description=read(),
    install_requires=[
        "kubernetes==17.17.0",
        "gym==0.24.0",
        "ray[rllib]==1.9.0",
        "aioredis==1.3.1",
        "simpy==4.0.1",
        "matplotlib==3.4.2",
        "PyQt5==5.15.4",
        "tensorflow==2.7.0",
        "python-decouple==3.5",
        "kserve==0.8.0",
        "tensorflow-serving-api==2.7.0",
        "grpcio==1.39.0",
        "protobuf==3.20.0",
        "numpy==1.19.2",
        "pillow==8.3.2",
    ]
)
