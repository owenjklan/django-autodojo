from typing import Callable, Any, Optional

from django.http import HttpRequest

from autodojo.defaults import DefaultErrorResponseSchema
from autodojo.generators.base_classes import AutoDojoViewGenerator
from autodojo.generators.utility import ensure_unique_name


class AutoDojoGetListGenerator(AutoDojoViewGenerator):
    """
    Generator for GET all (ie: List all) endpoint
    """

    default_response_schema_config = {"name": "Generated{model}Out"}

    def generate_view_func(self) -> Callable:
        def get_list_view_func(request: HttpRequest, *args, **kwargs):
            object_collection = self.model_class.objects.all()
            return 200, object_collection

        returned_func = ensure_unique_name(self.model_class, get_list_view_func)

        return returned_func

    @property
    def url_path(self) -> str:
        return "/"

    @property
    def response_config(self) -> dict[int, Optional[Any]]:
        return {200: list[self.response_schema]}


class AutoDojoGetGenerator(AutoDojoViewGenerator):
    """
    Generator for GET single item endpoint
    """

    default_response_schema_config = {"name": "Generated{model}Out"}

    def generate_view_func(self) -> Callable:
        def get_view_func(request: HttpRequest, id: int, *args, **kwargs):
            try:
                db_object = self.model_class.objects.get(pk=id)
            except self.model_class.DoesNotExist:
                return 404, {
                    "api_error": f"Requested {self.model_class_name} object does not exist",
                }

            return 200, db_object

        returned_func = ensure_unique_name(self.model_class, get_view_func)

        return returned_func

    @property
    def url_path(self) -> str:
        return "/{int:id}"

    @property
    def response_config(self) -> dict[int, Optional[Any]]:
        return {200: self.response_schema, 404: DefaultErrorResponseSchema}
