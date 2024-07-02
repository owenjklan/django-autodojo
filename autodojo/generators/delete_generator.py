from typing import Callable, Any, Optional

from django.http import HttpRequest
from ninja import Schema

from autodojo.defaults import DefaultErrorResponseSchema
from autodojo.generators.base_classes import AutoDojoViewGenerator
from autodojo.generators.utility import ensure_unique_name


class AutoDojoDeleteGenerator(AutoDojoViewGenerator):
    """
    Generator for DELETE endpoint
    """

    def generate_view_func(self) -> Callable:
        def delete_view_func(request: HttpRequest, id: int, *args, **kwargs):
            try:
                deleted_object = self.model_class.objects.get(pk=id)
            except self.model_class.DoesNotExist:
                return 404, {
                    "api_error": f"Requested {self.model_class_name} object does not exist",
                }

            deleted_object.delete()

            return 200, None  # Empty response body on successful delete

        returned_func = ensure_unique_name(self.model_class, delete_view_func)

        return returned_func

    @property
    def url_path(self) -> str:
        return "/{int:id}"

    @property
    def response_config(self) -> dict[int, Optional[Any]]:
        return {200: None, 404: DefaultErrorResponseSchema}
