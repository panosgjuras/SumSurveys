#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to transform Coimbra Survey data

@author: panosgtzouras
National Technical University of Athens
Research project: SUM
"""

import pandas as pd

def fixCoimbra(data):
    columns_to_remove = [col for col in data.columns if col.startswith('Points') or col.startswith('Feedback')]
    data_dropped = data.drop(columns=columns_to_remove)    
    return data_dropped
