import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class EventsTracker:
    _EVENTS_FILE_PATH = "analytics/events.txt"
    _DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    _FOLDER_NAME = "analytics"

    def save_event(self, user: str, event: str):
        if not os.path.exists(self._FOLDER_NAME):
            os.makedirs(self._FOLDER_NAME)

        date_time = datetime.now()
        current_datetime_string = date_time.strftime(self._DATE_FORMAT)

        log_event = current_datetime_string + " user: " + user + ", event: " + event + '\n'
        logger.info(log_event)

        with open(self._EVENTS_FILE_PATH, 'a') as file:
            file.write(log_event)
