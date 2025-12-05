import unittest

import main, LorcanaDataHandler
from PostData import PostData
from posters.Poster import Poster

_DUMMY_POST_DATA = PostData(1, "post text", b"", "image alt text")


class _DummySuccessfulPoster(Poster):
	def __init__(self):
		super().__init__("mastodon")
		self.postAttempts = 0

	def post(self, postData):
		self.postAttempts += 1


class _DummyExceptionPoster(_DummySuccessfulPoster):
	def __init__(self, timesToFail: int = 1):
		super().__init__()
		self.timesToFail = timesToFail

	def post(self, postData):
		super().post(postData)
		if self.timesToFail > 0:
			self.timesToFail -= 1
			raise Exception("Dummy Exception")


class PostingTestCase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		# Speed up timeouts
		main.SECONDS_BETWEEN_RETRIES = 0.1
		# Overwrite the data retrieval method with a dummy one
		LorcanaDataHandler.buildNextPostData = lambda: _DUMMY_POST_DATA

	def test_posting_successfully(self):
		dummyPoster = _DummySuccessfulPoster()
		postResult = main.post(dummyPoster)
		self.assertTrue(postResult, "Posting should have succeeded")
		self.assertEqual(dummyPoster.postAttempts, 1, "Only one post attempt should have been made")

	def test_posting_singleException(self):
		dummyPoster = _DummyExceptionPoster()
		postResult = main.post(dummyPoster)
		self.assertTrue(postResult, "Posting should have succeeded")
		self.assertEqual(dummyPoster.postAttempts, 2, "Only one retry should have been needed")

	def test_posting_keepFailing(self):
		main.MAX_POST_RETRIES = 3
		dummyPoster = _DummyExceptionPoster(main.MAX_POST_RETRIES + 10)
		postResult = main.post(dummyPoster)
		self.assertFalse(postResult, "Posting should have failed after exceeding maximum retries")
		self.assertEqual(dummyPoster.postAttempts, main.MAX_POST_RETRIES, "Posting should have been tried the maximum amount of times")

	def test_posting_dontPostSuccessfullyTwice(self):
		successDummyPoster = _DummySuccessfulPoster()
		exceptionDummyPoster = _DummyExceptionPoster()
		postResult = main.post(successDummyPoster, exceptionDummyPoster)
		self.assertTrue(postResult, "Posting should have succeeded")
		self.assertEqual(successDummyPoster.postAttempts, 1, "The successful poster shouldn't have posted after the first time")
		self.assertEqual(exceptionDummyPoster.postAttempts, 2, "The poster that failed the first time should have succeeded the second time")


if __name__ == "__main__":
	unittest.main()
