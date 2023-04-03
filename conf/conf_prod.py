# -*- coding: utf-8 -*-
# config.py

import os
#'text-davinci-003'
class prodConfig:
    OPENAI_API_KEY = os.environ.get('OPENAI_SK')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL')
    WOA_URL = os.environ.get('WOA_URL')
    FIREBASE_KEY = os.environ.get('FIREBASE_KEY')
    FIREBASE_DB_URL =os.environ.get('FIREBASE_DB_URL')