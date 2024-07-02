from typing import Callable, Any, Optional

from django.db.models.fields.related import ForeignKey
from django.http import HttpRequest
from django.db.models import Model

from ninja import ModelSchema

from autodojo.defaults import DefaultErrorResponseSchema
from autodojo.generators.base_classes import AutoDojoViewGenerator
from autodojo.generators.utility import ensure_unique_name


class AutoDojoPatchGenerator(AutoDojoViewGenerator):
    """
    Generator for PATCH
    """

    default_request_schema_config = {"exclude": ("id",), "optional_fields": "__all__"}
    default_response_schema_config = {"name": "Generated{model}Out"}

    def generate_view_func(self) -> Callable:
        def patch_view_func(
            request: HttpRequest, id: int, payload: ModelSchema, *args, **kwargs
        ):
            """
            Re-usable helper for patching objects, updating only supplied fields.

            Returns HTTP response code and response dictionary.

            If successful, 200 status will be returned and a dictionary of the updated
            object, suitable for JSON response.

            If the requested object doesn't, exist, then 404 status will be returned with
            an error message.
            """
            call_args = locals()
            # Look up the object being modified, if it exists
            try:
                patched_object = self.model_class.objects.get(pk=id)
            except self.model_class.DoesNotExist:
                return 404, {
                    "api_error": f"Requested {self.model_class_name} object does not exist",
                }

            patch_fields = payload.dict(exclude_unset=True)

            for attr, value in patch_fields.items():
                # Determine if the supplied attribute is a foreign key or not
                # Check for a field of the supplied attribute name
                field_meta = self.model_class._meta.get_field(attr)

                if field_meta.__class__ is ForeignKey:
                    # Ninja appears to take  Model.fk_field and treat "fk_field" and "fk_field_id" the same.
                    # For the purpose of reporting the attribute name, ensure it always ends with "_id" when
                    # used in messages
                    message_attr = attr if attr.endswith("_id") else f"{attr}_id"
                    related_model: Model
                    try:
                        related_model = field_meta.related_model
                        related_model_name = related_model._meta.object_name
                        referenced_object = related_model.objects.get(pk=value)
                    except related_model.DoesNotExist:
                        return 404, {
                            "api_error": f"{related_model_name} referenced by '{message_attr}' does not exist",
                        }

                    setattr(patched_object, attr, referenced_object)
                else:
                    setattr(patched_object, attr, value)

            patched_object.save()
            patched_object.refresh_from_db()

            return 200, patched_object

        returned_func = ensure_unique_name(self.model_class, patch_view_func)
        return returned_func

    @property
    def url_path(self) -> str:
        return "/{int:id}"

    @property
    def response_config(self) -> dict[int, Optional[Any]]:
        return {200: self.response_schema, 404: DefaultErrorResponseSchema}

    def patch_view_signature(self, view_func: Callable) -> Callable:
        """
        To ensure that Ninja supplies our view with the appropriate payload
        schema object, we need to ensure the 'payload' argument is correctly
        annotated. This cannot be done until runtime, because we create
        the type (the ModelSchema) at runtime.
        """
        view_func.__annotations__["payload"] = self.request_schema
        return view_func
