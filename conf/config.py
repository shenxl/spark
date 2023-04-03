# -*- coding: utf-8 -*-
import os
from .conf_dev import devConfig
from .conf_prod import prodConfig

def get_config():
    env = os.environ.get('ENV')
    if env == 'prod':
        return prodConfig()
    else:
        return devConfig()