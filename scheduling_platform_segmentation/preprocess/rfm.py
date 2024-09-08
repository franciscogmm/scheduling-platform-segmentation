import numpy as np
from copy import deepcopy
from scheduling_platform_segmentation.constants import TRAD_RF_SEGMENTS_LIST, QUANTILE_LIST

def calculate_weighted_recency(row):
    """this function computes the recency metric, weighted by the tenure. 
    formula is different depending on the tenure because of how the formulas
    behave in the respective ranges.

    The weighted recency metric takes into account the tenure of a user when
    considering how long ago the user last spent

    1 - row['recency'] / row['tenure'] => 1 - # of days ago over total possible days

    """

    if row['tenure'] <= 2:
        return row['recency'] / row['tenure']
    else:
        return (1 - row['recency'] / row['tenure']) ** 2

def clean_weighted_recency(row):
    """explicitly bound the metric from 0 and 1

    """
    if row['weighted_recency'] < 0:
        return 0
    elif row['weighted_recency'] > 1:
        return 1
    else:
        return row['weighted_recency']
    
def generate_quantile_dictionary(pdf, quantile_list):
    """generate quantile dictionary for each metric. the quantile dict is going to be used to create rwfm scores

    :param pdf: _description_
    :type pdf: _type_
    :return: _description_
    :rtype: _type_
    """

    dict_quantile = {}
    quantiles = pdf[[f'recency', f'weighted_recency', f'frequency', f'monetary']].quantile(q=quantile_list)
    dict_quantile[f'recency'] = dict(quantiles[f'recency'])
    dict_quantile[f'weighted_recency'] = dict(quantiles[f'weighted_recency'])
    dict_quantile[f'frequency'] = dict(quantiles[f'frequency'])
    dict_quantile[f'monetary'] = dict(quantiles[f'monetary'])
    return dict_quantile

def generate_conditions(pdf, dict_quantile, metric, reverse=0):
    """generate conditions, values pair for RWFM scores based on quartiles generate for specific run_date

    """
    metric_keys = list(dict_quantile[metric].keys())
    conditions = [
        (pdf[metric] <= dict_quantile[metric][metric_keys[0]]),
        (pdf[metric] > dict_quantile[metric][metric_keys[0]]) & (pdf[metric] <= dict_quantile[metric][metric_keys[1]]),
        (pdf[metric] > dict_quantile[metric][metric_keys[1]]) & (pdf[metric] <= dict_quantile[metric][metric_keys[2]]),
        (pdf[metric] > dict_quantile[metric][metric_keys[2]]) & (pdf[metric] <= dict_quantile[metric][metric_keys[3]]),
        (pdf[metric] > dict_quantile[metric][metric_keys[3]])
        ]

    if reverse == 0:
        values = [1,2,3,4,5]
    else:
        values = [5,4,3,2,1]

    return conditions, values

def generate_trad_rf_segments(pdf, weighted=0):
    """tag each user with traditional RF segments based on RWFM data

    """
    pdf_copy = deepcopy(pdf)
    if weighted == 0:
        recency = 'r'
    else:
        recency = 'w'
    conditions = [
        (pdf_copy[recency] >= 1) & (pdf_copy[recency] <= 2) & (pdf_copy['f'] >= 1) & (pdf_copy['f'] <= 2), # hibernating
        (pdf_copy[recency] >= 1) & (pdf_copy[recency] <= 2) & (pdf_copy['f'] >= 3) & (pdf_copy['f'] <= 4), # at_risk
        (pdf_copy[recency] >= 1) & (pdf_copy[recency] <= 2) & (pdf_copy['f'] == 5), # cant_lose
        (pdf_copy[recency] == 3) & (pdf_copy['f'] >= 1) & (pdf_copy['f'] <= 2), # about_to_sleep
        (pdf_copy[recency] == 3) & (pdf_copy['f'] == 3), # need_attention
        (pdf_copy[recency] >= 3) & (pdf_copy[recency] <= 4) & (pdf_copy['f'] >= 4) & (pdf_copy['f'] <= 5), # loyal_customers
        (pdf_copy[recency] == 4) & (pdf_copy['f'] == 1), # promising
        (pdf_copy[recency] == 5) & (pdf_copy['f'] == 1), # new_customers
        (pdf_copy[recency] >= 4) & (pdf_copy[recency] <= 5) & (pdf_copy['f'] >= 2) & (pdf_copy['f'] <= 3), # potential_loyalists
        (pdf_copy[recency] == 5) & (pdf_copy['f'] >= 4) & (pdf_copy['f'] <= 5), # champions
    ]

    values = TRAD_RF_SEGMENTS_LIST
    labels = np.select(conditions, values)

    return labels
