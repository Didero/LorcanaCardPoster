import datetime, json, urllib.parse, urllib.request

import Globals
from PostData import PostData
from posters.Poster import Poster

class BlueskyPoster(Poster):
	def __init__(self):
		super().__init__("bluesky", "instanceUrl", "username", "appPassword")

	def post(self, postData: PostData):
		Globals.logger.info("Posting to Bluesky")
		# First create a session so we get a session token
		sessionRequestData = json.dumps({"identifier": self._credentials['username'],  "password": self._credentials['appPassword']}).encode("utf-8")
		sessionResultJson = self._sendRequest(self._credentials['instanceUrl'] + "/xrpc/com.atproto.server.createSession", "application/json", sessionRequestData)
		accessToken = sessionResultJson['accessJwt']
		Globals.logger.info("Started Bluesky session")

		# Upload the image
		imageResultJson = self._sendRequest(self._credentials['instanceUrl'] + "/xrpc/com.atproto.repo.uploadBlob", "image/jpeg", postData.imageBytes, accessToken)
		imageData = imageResultJson['blob']
		Globals.logger.info("Uploaded images to Bluesky")

		# Make the actual post
		now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
		postRequestData = {
			"repo": sessionResultJson['did'], "collection": "app.bsky.feed.post", "record": {
				"$type": "app.bsky.feed.post", "text": postData.postText, "createdAt": now, "langs": ["en-US"], "embed": {
					"$type": "app.bsky.embed.images",
					"images": [
						{
							"alt": postData.imageAltText,
							"image": imageData
						}
					]
				}
			}
		}
		postResultJson = self._sendRequest(self._credentials['instanceUrl'] + "/xrpc/com.atproto.repo.createRecord", "application/json", json.dumps(postRequestData).encode("utf-8"), accessToken)
		Globals.logger.info(f"Posted to Bluesky successfully, URL: {postResultJson['uri']}")
