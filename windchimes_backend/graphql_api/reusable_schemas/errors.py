from typing import Optional

from pydantic import ValidationError
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
            name="forbidden-error",
            explanation=explanation,
            technical_explanation=technical_explanation,
        )


@strawberry.type
class ValidationErrorGraphQL(GraphQLApiError):
    dot_separated_field_location: str
    """
    Path to an invalid field, can be just a
    field name (`email`) or a dot separated path if the field nested
    (`user.contacts.email`)
    """

    def __init__(self, dot_separated_field_location: str, explanation: str):
        """Creates validation error strawberry schema object for returning in GraphQL

        Args:
            dot_separated_field_location: Path to an invalid field, can be just a
            field name (`email`) or a dot separated path if the field nested
            (`user.contacts.email`)
            explanation: Error message, e.g. "Must be longer than 3 chars"
        """

        super().__init__(
            name="validation-error",
            explanation=f'"{dot_separated_field_location}" is invalid: {explanation}',
            technical_explanation=f"{dot_separated_field_location}: {explanation}",
        )

        self.dot_separated_field_location = dot_separated_field_location

    @staticmethod
    def create_from_pydantic_validation_error(
        pydantic_validation_error: ValidationError, field_prefix: Optional[str] = None
    ):
        """
        Creates "validation error" schema object for graphql usage from pydantic
        validation error

        Args:
            pydantic_validation_error: Pydantic validation error object
            field_prefix: prefix/namespace to append to the field location
                (`dot_separated_field_location` field). E.g. prefix `user` and field
                `email` in pydantic error will result `user.email` as field location

        Raises:
            ValueError: if pydantic validation error does not have any errors
                (empty `errors()` func result)
        """

        errors = pydantic_validation_error.errors()

        if len(errors) == 0:
            raise ValueError()

        first_error = errors[0]

        first_error_field_location = ".".join(
            [str(location_item) for location_item in first_error["loc"]]
        )

        if field_prefix is not None:
            first_error_field_location = field_prefix + "." + first_error_field_location

        return ValidationErrorGraphQL(
            explanation=first_error["msg"],
            dot_separated_field_location=first_error_field_location,
        )
