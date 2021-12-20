# -*- coding: utf-8 -*-

import os
# to import from mod directory
from app.mod.classes import * #я знаю что так плохо
from app.mod.actions import *
import yaml
import app.mod.accents as accents
import pandas as pd
import re

from flask import (
    Blueprint, g, render_template, request, Response, flash
)

BP = Blueprint('eqphone', __name__, subdomain='eqphone') if os.environ.get('BLUEPRINTS_TYPES', "domains") == "domains" else Blueprint('eqphone', __name__, url_prefix='/eqphone')


@BP.url_value_preprocessor
def bp_url_value_preprocessor(endpoint, values):
    g.url_prefix = 'eqphone'


def init_app(app):
    pass



@BP.route('/', methods=('GET', 'POST'))
@BP.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        res = []
        t = request.form['text']
        text = re.sub(r'[^\w\s]','', t)
        text_for_load = text.split("\r\n")
        for i in range(1, len(text_for_load)):
            if len(text_for_load[i]) > 0 and len(text_for_load[i-1]) > 0:  
                res.append(f"<b>Сравнение строк {i} и {i+1}:</b>")
                pattern1 = accents.get_accents_stat(text_for_load[i-1])
                pattern2 = accents.get_accents_stat(text_for_load[i]) 
                pattern1, pattern2, print_str = differ(pattern1, pattern2)
#                 pattern1, pattern2 = union(pattern1), union(pattern2)
#                 res.append(print_str)
                res.extend([pattern1, pattern2, "<br>", print_str, "<br>" ])
        # calc res as html text
    else:
        t = res = ''
    return render_template('eqphone/base.html', text=t, res="<br>".join(res))

