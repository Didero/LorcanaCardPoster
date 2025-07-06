import json, os, uuid, urllib.parse, urllib.request

import Globals
from PostData import PostData
from posters.Poster import Poster


class MastodonPoster(Poster):
	def __init__(self):
		super().__init__("mastodon", "instanceUrl", "accessToken")

	def post(self, postData: PostData):
		Globals.logger.info("Posting to Mastodon")
		boundary = uuid.uuid4().hex
		imageRequestData = _MultipartRequestBuilder(boundary).addPart(False, "description", postData.imageAltText).addPart(True, f"{postData.cardId}.jpg", postData.imageBytes, "image/jpeg").getResult()
		imageResultJson = self._sendRequest(self._credentials['instanceUrl'] + "/api/v2/media", f"multipart/form-data; boundary={boundary}", imageRequestData, self._credentials['accessToken'])
		imageId = imageResultJson['id']
		Globals.logger.info(f"Uploaded image to Mastodon, image ID is {imageId}")

		postRequestData = urllib.parse.urlencode({'status': postData.postText, 'media_ids[]': imageId}).encode("utf-8")
		postResultJson = self._sendRequest(self._credentials['instanceUrl'] + "/api/v1/statuses", "application/x-www-form-urlencoded", postRequestData, self._credentials['accessToken'])
		Globals.logger.info(f"Posted to Mastodon successfully, URL: {postResultJson['url']}")


class _MultipartRequestBuilder:
	_LINE_SEPARATOR = b"\r\n"
	_EMPTY_LINE = b""

	def __init__(self, partBoundary: str):
		self._partBoundary = f"--{partBoundary}".encode("utf-8")
		self._lines: list[bytes] = [self._partBoundary]

	def _addLine(self, line: str | bytes):
		if isinstance(line, str):
			line = line.encode("utf-8")
		self._lines.append(line)

	def addPart(self, isFile: bool, name: str, data: str | bytes, contentType: str | None = None):
		if isFile:
			self._addLine(f"Content-Disposition: form-data; name=\"file\"; filename=\"{name}\"")
		else:
			self._addLine(f"Content-Disposition: form-data; name=\"{name}\"")
		if contentType:
			self._addLine(f"Content-Type: {contentType}")
		self._lines.append(self._EMPTY_LINE)
		self._addLine(data)
		self._lines.append(self._partBoundary)
		return self

	def getResult(self) -> bytes:
		# Last boundary needs two dashes after the end to indicate it's the last boundary, and a newline at the end
		return self._LINE_SEPARATOR.join(self._lines) + "--".encode("utf-8") + self._LINE_SEPARATOR
