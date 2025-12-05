import logging, os, sys, time
from logging.handlers import RotatingFileHandler

import Globals, LorcanaDataHandler
from posters.BlueskyPoster import BlueskyPoster
from posters.MastodonPoster import MastodonPoster


def post():
	postData = LorcanaDataHandler.buildNextPostData()
	if postData:
		try:
			MastodonPoster().post(postData)
		except Exception as e:
			Globals.logger.error(f"Exception {type(e).__name__!r} occurred while posting about card ID {postData.cardId} to Mastodon: {e}")
		try:
			BlueskyPoster().post(postData)
		except Exception as e:
			Globals.logger.error(f"Exception {type(e).__name__!r} occurred while posting about card ID {postData.cardId} to Mastodon: {e}")


if __name__ == "__main__":
	startTime = time.perf_counter()
	# First set up logging
	Globals.logger.setLevel(logging.INFO)
	loggingFormatter = logging.Formatter('%(asctime)s (%(levelname)s) %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
	#Log everything to a file. Use a new file each time the program is launched
	if not os.path.isdir("logs"):
		os.mkdir("logs")
	logfilePath = os.path.join(Globals.basepath, "logs", "LorcanaCardPoster.log")
	loggingFileHandler = RotatingFileHandler(logfilePath, mode="w", backupCount=10, encoding="utf-8", delay=True)
	loggingFileHandler.setLevel(logging.DEBUG)
	loggingFileHandler.setFormatter(loggingFormatter)
	if os.path.isfile(logfilePath):
		loggingFileHandler.doRollover()
	Globals.logger.addHandler(loggingFileHandler)
	#Also print everything to the console
	loggingStreamHandler = logging.StreamHandler(sys.stdout)
	loggingStreamHandler.setLevel(logging.DEBUG)
	loggingStreamHandler.setFormatter(loggingFormatter)
	Globals.logger.addHandler(loggingStreamHandler)

	# Now actually do what we need to do
	if len(sys.argv) <= 1:
		sys.exit("ERROR: No argument passed, please pass one of 'update', 'forceupdate', 'post'")
	argument = sys.argv[1].lower()
	if argument == "update" or argument == "forceupdate":
		LorcanaDataHandler.updateIfNecessary(argument == "forceupdate")
	elif argument == "rebuildschedule":
		LorcanaDataHandler.rebuildSchedule()
	elif argument == "post":
		post()
	else:
		Globals.logger.error(f"Unknown argument {argument!r}")
	Globals.logger.info(f"Finished after {time.perf_counter() - startTime:.4f} seconds")
