import strawberry


@strawberry.type
class GraphQLApiError:
    name: str

    technical_explanation: str
    """explanation of the error for developers

    can be given to the user to report the error somewhere
    """

    explanation: str = "An error occurred"
    """user-friendly explanation that can be displayed somewhere"""


class UnauthorizedErrorGraphQL(GraphQLApiError):
    def __init__(
        self,
        explanation="You must be logged in to perform this operation",
        technical_explanation="To perform this operation, you must be authorized, "
        + "Specify a bearer token in `Authorization` header",
    ):
        super().__init__(
            name="unauthorized-error",
            explanation=explanation,
            technical_explanation=technical_explanation,
        )


class ForbiddenErrorGraphQL(GraphQLApiError):
    def __init__(
        self,
        explanation="You don't have access to this resource",
        technical_explanation="You don't have access to this resource",
    ):
        super().__init__(
            name="unauthorized-error",
            explanation=explanation,
            technical_explanation=technical_explanation,
        )
