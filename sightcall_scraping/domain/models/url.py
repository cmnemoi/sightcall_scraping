class Url:
    def __init__(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Url):
            return False
        return self._value == other._value
