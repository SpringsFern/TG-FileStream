__version__="0.0.1"
class Version:
    version = __version__.split(".", maxsplit=3)
    major = int(version[0])
    minor = int(version[1])
    patch = int(version[2])

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
