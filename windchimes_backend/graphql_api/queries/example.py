import strawberry

from windchimes_backend.graphql_api.reusable_schemas.example import (
    Example,
    ExampleInput,
)


async def get_example(input: ExampleInput):
    return Example(text=f'example query with a name "{input.name}"')


example_query = strawberry.field(resolver=get_example, graphql_type=Example)
