import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class EventsTracker:
    _EVENTS_FILE_PATH = "analytics/events.txt"

    def save_event(self, user, event):
        folder_name = "analytics"

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        date_time = datetime.now()
        current_datetime_string = date_time.strftime("%Y-%m-%d %H:%M:%S")
        log_event = current_datetime_string + " user: " + user + ", event: " + event + '\n'
        logger.info(log_event)
        with open(self._EVENTS_FILE_PATH, 'a') as file:
            file.write(log_event)
