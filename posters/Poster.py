import json, os, urllib.request

import Globals
from PostData import PostData

class Poster:
	_CREDENTIALS_FILEPATH: str = os.path.join(Globals.basepath, "credentials.json")

	def __init__(self, credentialsCategory: str, *mandatoryCredentialsKeys: str):
		if not os.path.isfile(self._CREDENTIALS_FILEPATH):
			raise FileNotFoundError(f"Credentials file {self._CREDENTIALS_FILEPATH!r} does not exist, aborting")
		with open(self._CREDENTIALS_FILEPATH, "r") as credentialsFile:
			credentials = json.load(credentialsFile)
		if credentialsCategory not in credentials:
			raise KeyError(f"No '{credentialsCategory}' entry found in the credentials file")
		self._credentials = credentials[credentialsCategory]
		if mandatoryCredentialsKeys:
			for mandatoryCredentialsKey in mandatoryCredentialsKeys:
				if mandatoryCredentialsKey not in self._credentials:
					raise KeyError(f"No '{mandatoryCredentialsKey}' key found in the '{credentialsCategory}' credentials")
				if not self._credentials[mandatoryCredentialsKey]:
					raise ValueError(f"Key '{mandatoryCredentialsKey}' in the '{credentialsCategory}' credentials is not filled in")

	@staticmethod
	def _sendRequest(url: str, contentType: str, dataToSend: bytes, accessToken: str | None = None) -> dict:
		request = urllib.request.Request(url, headers={"Content-Type": contentType}, data=dataToSend)
		if accessToken:
			request.add_header("Authorization", f"Bearer {accessToken}")
		with urllib.request.urlopen(request) as connection:
			return json.load(connection)

	def post(self, postData: PostData):
		pass
