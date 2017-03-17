"""Wrapper around access to writing prompt subreddit.

"""

import time
import random
from collections import namedtuple

import praw  # reddit API wrapper
import praw.models

from readings import Preferences, Story, Topic, logger
from readings.database import Database, NullDatabase
from readings.wrappers import coroutine


reddit = praw.Reddit(client_id='lN-QXLdQhwdmOg', client_secret=None,
                     user_agent='Comment Extraction (by /u/aluriak)', implicit=True)
reddit.read_only = True


@coroutine
def stories(prefs:Preferences, database:Database, *, echo:bool=True):
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
    for subnum, submission in enumerate(submissions_generator):
        if echo:
            print('\rFound: {} submissions'.format(subnum), end='', flush=True)
        unvalid_reason = unvalid_submission(submission, prefs)
        if unvalid_reason:
            logger.info("Submission {} is unvalid because {}".format(submission.id, unvalid_reason))
            continue
        topic = Topic.from_praw(submission)
        if topic.author in prefs.unwanted_authors:
            logger.info("Submission {} have a non wanted author '{}'.".format(submission.id, topic.author))
            continue
        comments = submission.comments
        for num, comment in enumerate(comments, start=1):
            if isinstance(comment, praw.models.MoreComments):
                logger.info("Story {} is unreachable (MoreComment).".format(comment.id))
                continue  # TODO: handle MoreComments objects properly
            unvalid_reason = unvalid_comment(comment, prefs)
            if unvalid_reason:
                logger.info("Story {} is unvalid because {}".format(comment.id, unvalid_reason))
                continue
            story = Story.from_praw(comment, topic=topic)
            if database.already_read(story):
                logger.info("Story {} already read.".format(story.uid))
                continue
            if story.author in prefs.unwanted_authors:
                logger.info("Submission {} have a non wanted author '{}'.".format(submission.id, topic.author))
                continue
            if echo:
                print()
            prefs = (yield Story.from_praw(comment)) or prefs
            if not isinstance(prefs, Preferences):
                raise ValueError("Coroutine stories expect to receive Preferences instances, not " + repr(prefs))
            assert 0. <= prefs.topic_diversity <= 1., "invalid topic diversity ratio ({})".format(prefs.topic_diversity)
            if random.random() < prefs.topic_diversity:
                logger.info("Change of topic (diversity).")
                break
            if prefs.max_per_topic and num > int(prefs.max_per_topic):
                logger.info("Change of topic (max per topic reached).")
                break


def unvalid_comment(comment, prefs:Preferences) -> False or str:
    """Truthy if given comment/story is invalid according to given Preferences.

    The returned value is False if comment is valid.
    Else, it's a non-empty string that describes the problem.

    """
    char_size = sum(1 for c in comment.body if c.strip())
    line_size = sum(1 for l in comment.body.splitlines() if l.strip())
    return next(iter(reason for reason, unvalid in {
        "Deleted comment": comment.body.lower() == '[deleted]',
        "Not enough lines ({}/{})".format(line_size, prefs.min_line_number):
            prefs.min_line_number > line_size,
        "Not enough chars ({}/{})".format(char_size, prefs.min_char_number):
            prefs.min_char_number > char_size,
        "Low score ({}/{})".format(comment.score, prefs.minimal_score):
            prefs.minimal_score > comment.score,
    }.items() if unvalid), False)


def unvalid_submission(submission, prefs:Preferences) -> False or str:
    """Truthy if given submission/topic is invalid according to given Preferences.

    The returned value is False if submission is valid.
    Else, it's a non-empty string that describes the problem.

    """
    return next(iter(reason for reason, unvalid in {
        "Not a [WP]": not submission.title.lower().startswith(Topic.WP_HEADER.lower()),
        "Low upvote ratio ({}/{})".format(submission.upvote_ratio, prefs.minimal_topic_upvote_ratio):
            prefs.minimal_topic_upvote_ratio > float(submission.upvote_ratio),
        "Low upvote number ({}/{})".format(submission.ups, prefs.minimal_topic_upvote):
            prefs.minimal_topic_upvote > int(submission.ups),
        "Not at the right time ({})".format(submission.created_utc): prefs.timeframe > submission.created_utc,
    }.items() if unvalid), False)
