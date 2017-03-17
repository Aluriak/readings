"""Setup the readings logger."""

import logging


# Basic logging
logger = logging.getLogger('readings')
logger.setLevel(logging.DEBUG)


# Write in term
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


# Write in file
handler = logging.FileHandler('logs/readings.log')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
