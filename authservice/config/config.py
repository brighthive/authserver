"""Application Configuration

This module contains a general-purpose configuration class, subclasses for
different application environments, and a factory for creating configuration
objects based on the determined environment.

"""

import os
import json
from datetime import datetime


class Configuration(object):
    """Base configuration class.

    This is the base configuration class. It should be extended by other configuration classes on a per
    environment basis.

    """

    RELATIVE_PATH = os.path.dirname(os.path.relpath(__file__))
    ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    ROOT_PATH = ABSOLUTE_PATH.split(RELATIVE_PATH)[0]
    SETTINGS_FILE = os.path.join(ABSOLUTE_PATH, 'settings.json')

    @staticmethod
    def get_app_status():
        """Retrieves information about the API for health check.

        """
        try:
            with open(Configuration.SETTINGS_FILE, 'r') as fh:
                settings = json.load(fh)
        except Exception:
            settings = {}

        settings['api_status'] = 'OK'
        settings['timestamp'] = str(datetime.utcnow())
        return settings
