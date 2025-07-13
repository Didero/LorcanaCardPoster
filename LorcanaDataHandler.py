import io, json, os, random, urllib.request, zipfile

import Globals
from PostData import PostData

_DATA_PATH = os.path.join(Globals.basepath, "data")
_METADATA_FILEPATH = os.path.join(_DATA_PATH, "metadata.json")
_CARDSTORE_FILEPATH = os.path.join(_DATA_PATH, "cardstore.json")
_HISTORY_FILEPATH = os.path.join(_DATA_PATH, "postHistory.json")
_SCHEDULE_FILEPATH = os.path.join(_DATA_PATH, "postSchedule.json")

_SCHEDULE_FORMAT_VERSION = 1

def updateIfNecessary(forceUpdate: bool = False):
	if forceUpdate:
		Globals.logger.info("Update forced, updating")
		_update()
	elif not os.path.isfile(_METADATA_FILEPATH) or not os.path.isfile(_CARDSTORE_FILEPATH) or not os.path.isfile(_SCHEDULE_FILEPATH):
		Globals.logger.info("Missing file, updating")
		_update()
	else:
		with open(_METADATA_FILEPATH, "r") as metadataFile:
			localMetadata = json.load(metadataFile)
		with urllib.request.urlopen("https://lorcanajson.org/files/current/en/metadata.json") as metadataConnection:
			remoteMetadata = json.load(metadataConnection)
		if localMetadata["generatedOn"] != remoteMetadata["generatedOn"]:
			Globals.logger.info(f"Updating from {localMetadata['generatedOn']} to {remoteMetadata['generatedOn']}")
			_update()

def _update():
	with urllib.request.urlopen("https://lorcanajson.org/files/current/en/allCards.json.zip") as cardstoreZipConnection:
		with zipfile.ZipFile(io.BytesIO(cardstoreZipConnection.read()), "r", compression=zipfile.ZIP_LZMA) as cardstoreZip:
			with cardstoreZip.open("allCards.json") as cardstoreFile:
				cardstore = json.load(cardstoreFile)
	os.makedirs(_DATA_PATH, exist_ok=True)
	with open(_METADATA_FILEPATH, "w") as metadataFile:
		json.dump(cardstore["metadata"], metadataFile)
	with open(_CARDSTORE_FILEPATH, "w", encoding="utf8") as cardstoreFile:
		json.dump(cardstore, cardstoreFile)
	rebuildSchedule(cardstore)

def rebuildSchedule(cardstore=None) -> dict[str, int | list[int]]:
	Globals.logger.info("Building schedule")
	if not cardstore:
		with open(_CARDSTORE_FILEPATH, "r", encoding="utf8") as cardstoreFile:
			cardstore = json.load(cardstoreFile)
	if os.path.isfile(_HISTORY_FILEPATH):
		with open(_HISTORY_FILEPATH) as historyFile:
			history: list[int] = json.load(historyFile)
	else:
		history = []
	cardIds: list[int] = [c["id"] for c in cardstore["cards"] if c["id"] not in history]
	random.shuffle(cardIds)
	schedule = {"version": _SCHEDULE_FORMAT_VERSION, "cardIds": cardIds}
	with open(_SCHEDULE_FILEPATH, "w") as scheduleFile:
		json.dump(schedule, scheduleFile)
	return schedule

def buildNextPostData() -> PostData | None:
	if not os.path.isfile(_CARDSTORE_FILEPATH):
		updateIfNecessary()
	if os.path.isfile(_SCHEDULE_FILEPATH):
		with open(_SCHEDULE_FILEPATH, "r") as scheduleFile:
			schedule: dict[str, int | list[int]] = json.load(scheduleFile)
	else:
		schedule = rebuildSchedule()
	if "version" not in schedule or schedule["version"] != _SCHEDULE_FORMAT_VERSION:
		Globals.logger.info("Schedule version mismatch")
		schedule = rebuildSchedule()
	# Load next card ID from the schedule
	cardId: int = schedule["cardIds"].pop(0)
	Globals.logger.info(f"Building post data for card ID {cardId}")
	# Find the card data
	with open(_CARDSTORE_FILEPATH, "r", encoding="utf8") as cardstoreFile:
		cardstore = json.load(cardstoreFile)
	for card in cardstore['cards']:
		if card['id'] == cardId:
			Globals.logger.info(f"Downloading image from '{card['images']['full']}'")
			with urllib.request.urlopen(urllib.request.Request(card['images']['full'], headers={"User-Agent": "Lorcana/2024.4", "x-unity-version": "2022.3.44f1"})) as imageConnection:
				imageBytes = imageConnection.read()
			setData = cardstore['sets'][card['setCode']]
			postText = f"{card['fullName']}\nStory: {card['story']}\nFrom set {card['setCode']} \"{setData['name']}\", released on {setData['releaseDate']}"
			postData = PostData(cardId, postText, imageBytes, _getCardDescription(card))
			break
	else:
		Globals.logger.error(f"No card for ID '{cardId}' found")
		return None
	# Once posting succeeded, update schedule and history
	with open(_SCHEDULE_FILEPATH, "w") as scheduleFile:
		json.dump(schedule, scheduleFile)
	if os.path.isfile(_HISTORY_FILEPATH):
		with open(_HISTORY_FILEPATH, "r") as historyFile:
			history = json.load(historyFile)
	else:
		history = []
	history.append(cardId)
	with open(_HISTORY_FILEPATH, "w") as historyFile:
		json.dump(history, historyFile)
	return postData

def _getCardDescription(card):
	parts: list[str] = [
		f"Cost: {card['cost']}; " + ("Inkable" if card['inkwell'] else "Uninkable"),
		f"Name: {card['name']}"
	]
	if 'version' in card:
		parts.append(f"Subtitle: {card['version']}")
	parts.append(f"Type: {card['type']}")
	if 'subtypesText' in card:
		parts.append(f"Subtype{'' if len(card['subtypes']) == 1 else 's'}: {card['subtypesText']}")
	# Time for numbers!
	if 'moveCost' in card:
		parts.append(f"Move cost: {card['moveCost']}")
	if 'strength' in card:
		parts.append(f"Strength: {card['strength']}")
	if 'willpower' in card:
		parts.append(f"Willpower: {card['willpower']}")
	if 'lore' in card:
		parts.append(f"Lore: {card['lore']}")
	# Actual card text
	if card['fullText']:
		parts.append("")
		parts.append("Card text:")
		parts.append(card['fullText'])
	if 'flavorText' in card:
		parts.append("")
		parts.append("Flavor text:")
		parts.append(card['flavorText'])
	if card['fullText'] or 'flavorText in card':
		parts.append("")
	# Bottom information
	parts.append(f"Artist: {card['artistsText']}")
	parts.append(f"Identifier: {card['fullIdentifier']}")
	parts.append(f"Rarity: {card['rarity']}")
	return "\r\n".join(parts)
