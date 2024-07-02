# What is AutoDojo?
AutoDojo came about as a result of the [django_books_api](https://github.com/owenjklan/django-books-api)
project which I started for myself as an educational / practice exercise.
I very quickly became uninterested in repeating code for boilerplate
CRUD operations on simple objects and as such, AutoDojo was born. This has
also become a very educational exercise in Python type annotations and
metaprogramming in general.

## Installation and use
Pending a better packaging effort, AutoDojo can be used in a Django
Ninja project by adding the following to your project's `requirements.txt`:

```text
autodojo @ git+https://github.com/owenjklan/django-autodojo.git
```

For an example of how to use it, take a look at [django_books_api](https://github.com/owenjklan/django-books-api).

## A high-level view on how this works.
The main class that kicks everything off is the `AutoDojoRouter`. This
will ultimately generate appropriate Ninja Schema objects for requests
and responses as well as view functions for performing basic CRUD operations.
The generated view functions are automatically hooked into a Ninja Router
instance that is ready to be hooked up to an existing NinjaAPI object.

---

Note that simple foreign key relations are handled but M2M relationships
do not have any automatic generation implementation, as of July 2024.

---

A simple example, pulled from `django_books_api` is as follows. The following
example is the entire `urls.py` from that project:

```python
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from autodojo import AutoDojoRouter

from books_api.extra import router as extras_router

book_response_schema_configs = {
    "GET": {"depth": 2},
    "GETLIST": {"depth": 2},
}

authors_response_schema_configs = {
    "GET": {"depth": 2},
    "GETLIST": {"depth": 2},
}

books_adr = AutoDojoRouter(
    app_label="books_api",
    model="Book",
    # auth_class=django_auth,  # AutoDojoRouter will create a Ninja Router class using this, if present.
    response_schema_configs=book_response_schema_configs,
)
authors_adr = AutoDojoRouter(
    app_label="books_api",
    model="Author",
    response_schema_configs=authors_response_schema_configs,
)
categories_adr = AutoDojoRouter(app_label="books_api", model="Category")
publishers_adr = AutoDojoRouter(app_label="books_api", model="Publisher")

api_v2 = NinjaAPI()
api_v2.add_router(*books_adr.add_router_args)
api_v2.add_router(*authors_adr.add_router_args)
api_v2.add_router(*categories_adr.add_router_args)
api_v2.add_router(*publishers_adr.add_router_args)

api_v2.add_router("/book/", extras_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v2/", api_v2.urls),
]
```

The `AutoDojoRouter` constructor only requires two pieces of information
at a minimum: The Django "app label" and the model class to generate for.
The model class can be specified as the Model class itself or a string.

The `book_response_schema_configs` dictionary is an example of the user
being able to pass overrides for values that will ultimately be used
with Ninja's `create_schema()` function.

Note the special `"GETLIST"`: This is a special value for HTTP method
names that the view generation will use to select a generator for listing
all of a specific object, rather than a single object.

`AutoDojoRouter` will return a Ninja `Router` object which has had
generated views already connected to it. Come time to add the generated
router object to the `NinjaAPI` instance, the `add_router_args` property
can be dereferenced to populate the mounting path and generated `Router`
object, for convenience with `NinjaAPI().add_router()`.

The example code above also includes an example of using a "vanilla"
view and router that was written manually, demonstrating that AutoDojo
can work alongside traditional approaches to connecting up views in Ninja.

### View Generation
Each HTTP method verb will have an `AutoDojoViewGenerator` class associated
with it. This base class is then subclassed to provide the view function
implementation, and default options for `create_schema` may be provided.

Although it hasn't been explicitly tested as of the time of writing (July, 2024),
the `AutoDojoView` class should be usable directly with little modification.
This and the ability to register custom generator classes will be part of a
future evolution. Of interest, however, might be that the current implementation
of `AutoDojoView` is designed to allow already-defined Ninja Schema classes
to be provided.

#### Order of resolution for `create_schema()` parameters
Because view generators might have their own defaults, and users can
also provide their own, the order of resolution for values to pass
to `create_schema()` is (higher numbers overwrite those of lower numbers):

1. The defaults (optionally) defined in the view generator class's 
   `default_request_schema_config` or `default_response_schema_config`
   properties.
2. Values provided by the `request_schema_config` and `response_schema_config`
   keyword arguments to the `AutoDojoView` constructor method

## No better documentation?
The next phase of this project is to use it as a vector to experiment
with using Sphinx for documentation generation. Watch this space.

## Wishlist of features
- Ability to register additional "Special Methods" like "GETLIST", including
  a custom view generator class implementation
- Out-of-the-box implementation for creating endpoints to manage M2M relations
- More thorough testing
- Some form of registry object to allow generated schema classes to
  be queried at runtime by code external to AutoDojo

## Additional Information
Guidance for how to set up enough of a Django environment to
be able to test without a full app was pulled directly from the
Django documentation pages [at this URL.](https://docs.djangoproject.com/en/4.1/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications)
