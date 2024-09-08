import numpy as np
import pandas as pd
from copy import deepcopy
from scheduling_platform_segmentation.constants import TRAD_RF_SEGMENTS_LIST, QUANTILE_LIST
    
def generate_quantile_dictionary(pdf, quantile_list):
    """generate quantile dictionary for each metric. the quantile dict is going to be used to create rwfm scores

    :param pdf: _description_
    :type pdf: _type_
    :return: _description_
    :rtype: _type_
    """

    dict_quantile = {}
    quantiles = pdf[['tenure', 'recency', 'frequency', 'monetary',
                     ]].quantile(q=quantile_list)
    dict_quantile[f'tenure'] = dict(quantiles[f'tenure'])
    dict_quantile[f'recency'] = dict(quantiles[f'recency'])
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

def generate_trad_rf_segments(pdf):
    """tag each user with traditional RF segments based on RWFM data

    """
    pdf_final = pd.DataFrame([], columns=pdf.columns)
    pdf_final['wtd_rfm'] = None
    for i in range(1,6):
        pdf_copy = pdf[pdf['t']==i]
        recency = 'r'
        
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
        pdf_copy['wtd_rfm'] = np.select(conditions, values)
        pdf_final = pd.concat([pdf_final, pdf_copy])
    pdf_final['frequency'] = pdf_final['frequency'].astype(int)


    return pdf_final
