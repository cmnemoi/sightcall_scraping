class Url:
    def __init__(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other):
        if not isinstance(other, Url):
            return False
        return self._value == other._value

    def __repr__(self):
        return f"Url('{self._value}')"
