"""Implementation of a database.

"""


import json
from readings import Story


DEFAULT_DB_FILE = 'data/database'


class Database:
    """Remember seen stories.

    Expose mark_as_read, already_read and commit methods,
    that allow client or readings to manipulate data.

    """

    def __init__(self, dbfilename:str=DEFAULT_DB_FILE):
        self._db_name = str(dbfilename)
        try:
            with open(self._db_name) as fd:
                data = fd.read()
                if not data.strip(): raise FileNotFoundError()  # empty file == no file
                self._db = json.loads(data)
            self.dirty = False
        except FileNotFoundError:
            self._db = {}
            self.dirty = True

    def commit(self):
        """Save modifications to file"""
        if self.dirty:
            # LOGGER.info("New database: {}".format(self._db))
            with open(self._db_name, 'w') as fd:
                json.dump(self._db, fd)
            self.dirty = False

    def mark_as_read(self, story:Story):
        """Add story id to database as a read object"""
        self._db.setdefault(story.topic.uid, []).append(story.uid)
        self.dirty = True

    def already_read(self, story:Story) -> bool:
        """True if given story is marked as 'read' in database"""
        topic = self._db.get(story.topic.uid)
        return topic and story.uid not in topic


class NullDatabase:
    """Like a Database, but in dry run and no file access."""

    def __init__(self, _:str=DEFAULT_DB_FILE):
        pass
    def already_read(self, story):
        pass
    def mark_as_read(self, story):
        pass
    def commit(self):
        pass
