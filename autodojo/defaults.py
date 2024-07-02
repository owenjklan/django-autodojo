from ninja import Schema


class DefaultErrorResponseSchema(Schema):
    api_error: str


class Default401ResponseSchema(Schema):
    """
    This simply ensures that a 401 response uses
    "api_error" rather than "detail" in the response JSON
    """

    api_error: str = "Unauthorized"
