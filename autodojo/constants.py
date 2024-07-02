# Special methods, especially "GETLIST" 'just work' in terms of lookup
# for generator classes etc, but the HTTP method used will need to be
# translated.
SPECIAL_METHODS_TRANSLATION = {
    "GETLIST": "GET",
}
DEFAULT_METHODS = (
    "GET",
    "GETLIST",  # Special method to differentiate from get-single-object
    "POST",
    "PATCH",
    "PUT",
    "DELETE",
)
