import dataclasses

@dataclasses.dataclass
class PostData:
	cardId: int
	postText: str
	imageBytes: bytes
	imageAltText: str
