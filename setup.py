from setuptools import find_packages, setup
import pathlib
import os
import re
import glob
from itertools import chain

PLUGIN_NAME = "airflow_xtended_api"
PLUGIN_ROOT_FILE = "main"
PLUGIN_ENTRY_POINT = "XtendedApi"
HOME = pathlib.Path(__file__).parent
README = (HOME / "README.md").read_text()
CONFIG = HOME / PLUGIN_NAME / "config.py"


def get_requirements():
    return [
        "apache-airflow>=2.1.0",
        "boto3>=1.17.97",
        "pymongo>=3.11.4",
        "requests>=2.25.1",
    ]


def get_package_data():
    exts = ["js", "css", "html"]

    files = list(
        chain(*[glob.glob(f"{PLUGIN_NAME}/**/*.%s" % x, recursive=True) for x in exts])
    )
    return [x.split(os.sep, 1)[1] for x in files]


def get_version(config_file):
    pattern = re.compile(r"PLUGIN_VERSION = \s*.\s*([a-zA-Z0-9\.]*)\s*.\s*")
    for line in config_file.open():
        for match in re.finditer(pattern, line):
            return match.group(1)


setup(
    name=PLUGIN_NAME,
    packages=find_packages(include=[f"{PLUGIN_NAME}.*", PLUGIN_NAME]),
    include_package_data=True,
    package_data={PLUGIN_NAME: get_package_data()},
    entry_points={
        "airflow.plugins": [
            f"{PLUGIN_NAME} = {PLUGIN_NAME}.{PLUGIN_ROOT_FILE}:{PLUGIN_ENTRY_POINT}"
        ]
    },
    zip_safe=False,
    version=get_version(CONFIG),
    license="GNU AGPLv3",
    description="Exposes 'Xtended' Apache Airflow management capabilities via secure API",
    long_description=README,
    long_description_content_type="text/markdown",
    author="anr007",
    author_email="",
    url="https://github.com/anr007/airflow-xtended-api",
    keywords=["apache airflow", "plugin", "flask"],
    install_requires=get_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.6",
)
