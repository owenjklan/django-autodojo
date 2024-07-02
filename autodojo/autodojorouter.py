from typing import Any

import ninja
from django.apps import apps
from django.db import models


from autodojo.autodojoview import AutoDojoView
from autodojo.constants import SPECIAL_METHODS_TRANSLATION, DEFAULT_METHODS


class AutoDojoRouter:
    def __init__(
        self,
        *,
        app_label: str = None,
        model: str | models.Model = None,
        http_methods: list[str] = DEFAULT_METHODS,
        auth_class: type = None,
        response_schema_configs: dict[str, dict[str, Any]] = None,
        request_schema_configs: dict[str, dict[str, Any]] = None,
    ):
        """ """
        # Despite the kwargs all having defaults, the following args MUST be non-None.
        # The reason the signature is like this is so the call can be somewhat self-describing
        required_kwargs = ["app_label", "model"]
        self._enforce_required_kwargs(locals(), required_kwargs)

        self.response_schema_configs = (
            response_schema_configs if response_schema_configs else {}
        )
        self.request_schema_configs = (
            request_schema_configs if request_schema_configs else {}
        )

        self.app_label = (
            app_label  # Must be set before _resolve_orm_model_class() is called
        )
        self.model_class = self._resolve_orm_model_class(model)
        self.model_class_name = self.model_class._meta.object_name

        # Things we might add to the Router
        self.auth_class = auth_class

        # The generated router will be "mounted" here in the urlpatterns
        self.base_url_path = f"/{self.model_class._meta.verbose_name_plural}/"

        # Now, let's wire everything up in the router
        self._router = ninja.Router(auth=self.auth_class)

        # Generate required method implementations
        # TODO: allow control/configuration of status-code specific
        #       response configurations.
        for http_method in http_methods:
            auto_view = AutoDojoView(
                self.model_class,
                http_method,
                request_schema_config=self.request_schema_configs.get(
                    http_method, None
                ),
                response_schema_config=self.response_schema_configs.get(
                    http_method, None
                ),
            )

            # "GETLIST" in particular will need to be translated to "GET"
            actual_method_verb = SPECIAL_METHODS_TRANSLATION.get(
                http_method, http_method
            )

            self._router.add_api_operation(
                auto_view.url_path,
                methods=[actual_method_verb],
                response=auto_view.response_config,
                view_func=auto_view.view_func,
                tags=[self.model_class_name],
            )

    @property
    def router(self) -> ninja.Router:
        return self._router

    @property
    def add_router_args(self) -> tuple[str, ninja.Router]:
        return self.base_url_path, self._router

    def _enforce_required_kwargs(
        self, called_args: dict, required_kwargs: list[str]
    ) -> None:
        for arg, value in called_args.items():
            if arg not in required_kwargs:
                continue

            if value is None:
                raise ValueError(f"'{arg}' cannot be None")

    def _resolve_orm_model_class(self, model: str | models.Model) -> models.Model:
        if isinstance(model, models.Model):
            return model

        if not isinstance(model, str):
            raise ValueError(f"'{model}' is not a string or ORM Model class")

        # Look-up the class from Django's Apps configurations
        model_class = apps.get_model(self.app_label, model)
        return model_class
