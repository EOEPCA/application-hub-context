from setuptools import find_packages, setup

extra_files = []

setup(
    description="application-context-hub",
    url="https://github.com/EOEPCA/application-hub-context.git",
    author="Terradue",
    author_email="fabrice.brito@terradue.com",
    license="EUPL",
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    entry_points={},
    package_data={"": extra_files},
)
