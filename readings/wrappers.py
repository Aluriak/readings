"""Definition of the preferences class"""


import time
import functools
from pprint import pprint
from collections import namedtuple

from readings import timeframe


LINK_HEAD = 'https://reddit.com/'

PreferencesBase = namedtuple('PreferencesBase', 'max_per_topic, topic_diversity, unwanted_authors, minimal_topic_upvote, minimal_topic_upvote_ratio, minimal_score, timeframe')
PreferencesBase.__new__.__defaults__ = 10, 0.01, {'WritingPromptsRobot'}, 0, 0, 0, timeframe.today


TopicBase = namedtuple('TopicBase', 'uid, text, author, upvote, upvote_ratio, gilded, sub_date')
StoryBase = namedtuple('StoryBase', 'uid, text, html, topic, author, permalink, score, gilded, sub_date')


UserResult = namedtuple('Result', 'isread')  # TODO: note, change_topic
UserResult.__new__.__defaults__ = False,


def coroutine(func):
    """Initialize given func at call by calling its next."""
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        ret = func(*args, **kwargs)
        next(ret)
        return ret
    return wrapped


class Preferences(PreferencesBase):
    """A tuple of preferences offering time stamp facilities."""
    time = timeframe


class Topic(TopicBase):
    """A tuple describing a topic (Writing Prompts' submission).

    Expose a constructor submission -> topic.

    """
    WP_HEADER = '[WP] '

    @staticmethod
    def from_praw(submission):
        # print('SUBMISSION:', dir(submission))
        # fields = "approved_by, archived, author, author_flair_css_class, author_flair_text, banned_by, brand_safe, clicked, comment_limit, comment_sort, comments, contest_mode, created, created_utc, distinguished, domain, downs, edited, flair, fullname, gilded, hidden, hide_score, id, is_self, likes, link_flair_css_class, link_flair_text, locked, media, media_embed, mod, mod_reports, name, num_comments, num_reports, over_18, permalink, quarantine, removal_reason, report_reasons, saved, score, secure_media, secure_media_embed, selftext, selftext_html, shortlink, spoiler, stickied, subreddit, subreddit_id, subreddit_name_prefixed, subreddit_type, suggested_sort, thumbnail, title, ups, upvote_ratio, url, user_reports, visited".replace(',', '').split()
        # pprint({field: getattr(submission, field) for field in fields})
        # input('<?>')
        return Topic(
            uid=submission.id,
            text=submission.title[len(Topic.WP_HEADER):],
            author=submission.author.name,
            upvote=int(submission.ups),
            upvote_ratio=float(submission.upvote_ratio),
            gilded=int(submission.gilded),
            sub_date=time.asctime(time.gmtime(submission.created_utc)),
        )


class Story(StoryBase):
    """A tuple describing a story (Writing Prompts' top level comment).

    Expose a constructor comment -> story.

    """

    @staticmethod
    def from_praw(comment, *, topic=None):
        """Return a new Story instance. Use given topic, or build a brand new
        one from comment data if not provided.

        """
        # fields = ['approved_by', 'archived', 'author', 'author_flair_css_class', 'author_flair_text', 'banned_by', 'block', 'body', 'body_html', 'clear_vote', 'controversiality', 'created', 'created_utc', 'delete', 'depth', 'distinguished', 'downs', 'downvote', 'edit', 'edited', 'fullname', 'gild', 'gilded', 'id', 'is_root', 'likes', 'link_id', 'mark_read', 'mark_unread', 'mod', 'mod_reports', 'name', 'num_reports', 'parent', 'parent_id', 'parse', 'permalink', 'refresh', 'removal_reason', 'replies', 'reply', 'report', 'report_reasons', 'save', 'saved', 'score', 'score_hidden', 'stickied', 'submission', 'subreddit', 'subreddit_id', 'subreddit_name_prefixed', 'subreddit_type', 'unsave', 'ups', 'upvote', 'user_reports']
        # pprint({field: getattr(comment, field) for field in fields})
        # input('<?>')
        author = '[deleted]' if not comment.author else comment.author.name
        return Story(
            uid=comment.id,
            text=comment.body,
            html=comment.body_html,
            topic=topic or Topic.from_praw(comment.submission),
            author=author,
            permalink=LINK_HEAD + comment.permalink(),
            score=comment.score,
            gilded=comment.gilded,
            sub_date=time.asctime(time.gmtime(comment.created_utc)),
        )
