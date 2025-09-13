import strawberry

from windchimes_backend.graphql_api.reusable_schemas.example import (
    Example,
    ExampleInput,
)


async def get_example(example_input: ExampleInput):
    return Example(text=f'example query with a name "{example_input.name}"')


example_query = strawberry.field(resolver=get_example, graphql_type=Example)
