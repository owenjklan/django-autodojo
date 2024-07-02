from typing import Any, Type

from django.db import models

from ninja import ModelSchema, Schema

from autodojo.generators import (
    AutoDojoDeleteGenerator,
    AutoDojoGetGenerator,
    AutoDojoGetListGenerator,
    AutoDojoPatchGenerator,
    AutoDojoPostGenerator,
    AutoDojoPutGenerator,
)

# Mapping of HTTP method names to their generation class
method_generation_classes = {
    "GET": AutoDojoGetGenerator,
    "GETLIST": AutoDojoGetListGenerator,
    "PATCH": AutoDojoPatchGenerator,
    "DELETE": AutoDojoDeleteGenerator,
    "POST": AutoDojoPostGenerator,
    "PUT": AutoDojoPutGenerator,
}


class AutoDojoView:
    """
    This class handles the creation of everything necessary to handle
    a given HTTP method, including creating appropriate view function,
    suitable request and response schemas.

    Request and response schemas can be provided but will be automatically
    generated if not provided.

    If provided, the request_schema_config and response_schema_config
    dictionaries provide values to override defaults passed to the
    call to create_schema(). Note that if existing schema classes are
    passed in, then the presence of these dictionaries will raise an
    exception.

    For details of create_schema(), consult the Ninja documentation at
    https://django-ninja.dev/guides/response/django-pydantic-create-schema/

    This class can be used in isolation or used by the AutoDojoRouter
    to provide a more complete solution.
    """

    SUPPORTED_METHODS = [
        "GET",
        "GETLIST",  # Special method to differentiate get all from get individual
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
    ]

    def __init__(
        self,
        model_class: Type[models.Model],
        http_method: str,
        request_schema: Type[Schema] = None,
        response_schema: Type[Schema] = None,
        request_schema_config: dict[str, Any] = None,
        response_schema_config: dict[str, Any] = None,
        doc_string: str = None,
    ):
        if http_method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Unsupported HTTP method: {http_method}")

        # If ModelSchema classes have been explicitly provided, then
        # raise an exception if a matching schema config dictionary
        # has been provided. This is to highlight that the supplied
        # dictionary will not be used if an existing schema is provided.
        if request_schema and request_schema_config:
            raise ValueError(
                f"Supplied request_schema_config will be ignored because"
                f" request_schema class was supplied"
            )

        if response_schema and response_schema_config:
            raise ValueError(
                f"Supplied response_schema_config will be ignored because"
                f" response_schema class was supplied"
            )

        # Note model details, largely for string formatting convenience
        self.model_class = model_class
        self.model_class_name = model_class._meta.object_name
        self.model_singular = model_class._meta.model_name.lower()
        self.model_plural = model_class._meta.verbose_name_plural.lower()

        self.doc_string = doc_string

        try:
            self.generator_class = method_generation_classes[http_method](
                model_class=self.model_class,
                http_method=http_method,
                request_schema=request_schema,
                response_schema=response_schema,
                request_schema_config=request_schema_config,
                response_schema_config=response_schema_config,
            )
        except KeyError as ke:
            raise NotImplementedError(
                f"HTTP method has no generator class: {http_method}"
            )

        # Generate request and response schemas, if not provided
        self.request_schema = (
            request_schema
            if request_schema
            else self.generator_class.generate_request_schema()
        )
        self.response_schema = (
            response_schema
            if response_schema
            else self.generator_class.generate_response_schema()
        )

        self.url_path = self.generator_class.url_path

        self.response_config = self.generator_class.response_config
        self.view_func = self.generator_class.generate_view_func()

        # view_funcs receiving request schemas will need to patch
        # their signature type annotations at runtime.
        self.view_func = self.generator_class.patch_view_signature(self.view_func)

        # Update the view function's docstring, as this will be visible in
        # any Ninja-generated OpenAPI documentation.
        self.view_func = self.generator_class.patch_doc_string(
            self.view_func, docstring=self.doc_string
        )
