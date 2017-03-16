"""Wrapper around access to writing prompt subreddit.

"""

import time
import random
import logging
from collections import namedtuple

import praw  # reddit API wrapper
import praw.models

from readings import Preferences, Story, Topic
from readings.database import Database, NullDatabase
from readings.wrappers import coroutine


LOGGER = logging.getLogger()

reddit = praw.Reddit(client_id='lN-QXLdQhwdmOg', client_secret=None,
                     user_agent='Comment Extraction (by /u/aluriak)', implicit=True)
reddit.read_only = True


@coroutine
def stories(prefs:Preferences, database:Database):
    """Coroutine browsing stories depending of received preferences.

    This code is awful.

    """
    assert isinstance(database, Database)
    sub = reddit.subreddit('WritingPrompts')

    # Restrict submissions to a timeframe if possible, else take them all.
    if prefs.timeframe <= 0:
        submissions_generator = sub.stream.submissions()
    else:
        submissions_generator = sub.submissions(prefs.timeframe, time.time())

    # For each submission as topic, for each comment as story,
    #  yield story(topic) if prefs allowed it. Take account sent prefs.
    for submission in submissions_generator:
        if unvalid_submission(submission, prefs):
            LOGGER.info("Submission {} is unvalid.".format(submission.id))
            continue
        topic = Topic.from_praw(submission)
        if topic.author in prefs.unwanted_authors:
            LOGGER.info("Submission {} have a non wanted author '{}'.".format(submission.id, topic.author))
            continue
        comments = submission.comments
        for num, comment in enumerate(comments, start=1):
            if isinstance(comment, praw.models.MoreComments):
                LOGGER.info("Story {} is unreachable (MoreComment).".format(comment.id))
                continue  # TODO: handle MoreComments objects properly
            if unvalid_comment(comment, prefs):
                LOGGER.info("Story {} is unvalid.".format(comment.id))
                continue
            story = Story.from_praw(comment, topic=topic)
            if database.already_read(story):
                LOGGER.info("Story {} already read.".format(story.uid))
                continue
            if story.author in prefs.unwanted_authors:
                LOGGER.info("Submission {} have a non wanted author '{}'.".format(submission.id, topic.author))
                continue
            prefs = (yield Story.from_praw(comment)) or prefs
            if not isinstance(prefs, Preferences):
                raise ValueError("Coroutine stories expect to receive Preferences instances, not " + repr(prefs))
            assert 0. <= prefs.topic_diversity <= 1., "invalid topic diversity ratio ({})".format(prefs.topic_diversity)
            if random.random() < prefs.topic_diversity:
                LOGGER.info("Change of topic (diversity).")
                break
            if prefs.max_per_topic and num > int(prefs.max_per_topic):
                LOGGER.info("Change of topic (max per topic reached).")
                break


def unvalid_comment(comment, prefs:Preferences) -> bool:
    """True if given comment/story is invalid according to given Preferences"""
    return any((
        comment.body.lower() == '[deleted]',
        prefs.minimal_score > comment.score,
    ))


def unvalid_submission(submission, prefs:Preferences) -> bool:
    """True if given submission/topic is invalid according to given Preferences"""
    return any((
        not submission.title.lower().startswith(Topic.WP_HEADER.lower()),
        prefs.minimal_topic_upvote_ratio > float(submission.upvote_ratio),
        prefs.minimal_topic_upvote > int(submission.ups),
        prefs.timeframe > submission.created_utc,
    ))
