import strawberry

from windchimes_backend.graphql_api.reusable_schemas.example import (
    Example,
    ExampleInput,
)


def create_example(input: ExampleInput) -> Example:
    return Example(text=f'example mutation, name: "{input.name}"')


create_example_mutation = strawberry.mutation(resolver=create_example)
