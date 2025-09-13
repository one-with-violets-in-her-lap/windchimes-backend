import strawberry


@strawberry.input
class ExampleInput:
    name: str


@strawberry.type
class Example:
    text: str
