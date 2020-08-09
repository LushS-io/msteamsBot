import os
from setuptools import setup

NAME = "FileBot"
VERSION = os.environ["packageVersion"] if "packageVersion" in os.environ else "4.10.0"
REQUIRES = [
    "asyncio==3.4.3",
    "requests==2.23.0",
    "jsonpickle==1.2",
    "requests_oauthlib==1.3",
    "botbuilder-core==4.10.0"
    "botbuilder-schema==4.10.0",
    "botframework-connector==4.10.0",
    "botbuilder-integration-aiohttp==4.10.0",
    "botbuilder-dialogs==4.10.0"
]

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description="A FileBot built with BotFramework",
    author="Troy Kirin",
    url="https://troykirin.io/bots",
    keywords=["python", "bots", "ai", "botframework", "botbuilder"],
    install_requires=REQUIRES,
    packages=[
        "bots",
    ],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.8.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Alpha Development",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
