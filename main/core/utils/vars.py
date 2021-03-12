
get_user_search_fields = lambda field_name="user": (f"{field_name}__first_name", f"{field_name}__last_name",
                                                    f"{field_name}__email", f"{field_name}__username",)

USER_SEARCH_FIELDS = get_user_search_fields(field_name="user")

DLP_VARS = ("password",)
