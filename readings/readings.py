"""Define the main client interface for the whole package.

"""

from readings import remote
from readings import Preferences, Topic, UserResult
from readings.readers import term_reader
from readings.database import Database


def readings(reader:callable=term_reader, database:Database=Database(),
             prefs=Preferences(), **kwargs):
    """Create a Preferences instance from kwargs,
    run a database and a reader.

    reader -- callback called each time a story is found.
    prefs -- Preferences instance to use.
    kwargs -- override of Preferences parameters.

    See callback examples in readings/readings.py module.
    If a callback returns a falsy value, the loop is stopped and readings ends.
    Callback can return a new Preferences instance,
    or a new UserResult instance.


    """
    prefs = Preferences(**{**prefs._asdict(), **kwargs})
    searched = remote.stories(prefs, database)
    result = True
    try:
        while result:
            story = searched.send(prefs)
            result = reader(story)
            # handle user response
            prefs = result if isinstance(result, Preferences) else prefs
            user = result if isinstance(result, UserResult) else UserResult()
            if user.isread:
                database.mark_as_read(story)
    except KeyboardInterrupt:
        pass
    database.commit()
