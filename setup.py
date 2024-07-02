import setuptools

setuptools.setup(
    name="autodojo",
    version="0.1.0",
    url="https://github.com/owenjklan/autodojo",
    author="Owen Klan",
    author_email="owen.j.klan@gmail.com",
    description=(
        "AutoDojo allows automatic creation of boilerplate Schemas and Views for basic CRUD operations on Django ORM Model classes."
    ),
    long_description=open("README.md").read(),
    packages=setuptools.find_packages(),
    install_requires=["Django >=3.1", "pydantic >=2.0,<3.0.0", "django-ninja >=1.1.0"],
)
