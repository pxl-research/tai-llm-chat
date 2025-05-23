import json
import pprint as pp

import pandas as pd
import requests


def get_models(tools_only=True, names_only=True, as_dataframe=False):
    models_url = 'https://openrouter.ai/api/v1/models'
    if tools_only:
        models_url += '?supported_parameters=tools'

    response = requests.get(models_url)

    model_list = json.loads(response.text)
    print(f'{len(model_list['data'])} models are available.')

    # no experimental
    filtered_data = [m for m in model_list['data']
                     if 'beta' not in m['id']
                     and '-exp' not in m['id']
                     and ':free' not in m['id']]

    # context
    filtered_data = [m for m in filtered_data if m['context_length'] >= 16000]  # at least medium-size context

    # price
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['completion']) * 1000000 < 20]  # completion pricing
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['prompt']) * 1000000 < 10]  # prompt pricing
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['prompt']) > 0]  # remove free ones because they are rate limited

    print(f'{len(filtered_data)} models left after filtering ...\n')

    # sorting by provider, then pricing
    filtered_data.sort(
        key=lambda m: (m['id'].split('/')[0], float(m['pricing']['prompt']), float(m['pricing']['completion'])))

    if names_only and not as_dataframe:
        names = []
        for model in filtered_data:
            names.append(model['id'])
        return no_duplicates(names)

    md_data = []
    for model in filtered_data:
        ppm_p = float(model['pricing']['prompt']) * 1000000
        ppm_c = float(model['pricing']['completion']) * 1000000
        md_data.append([model['id'].split('/')[0],
                        model['id'],
                        ppm_p,
                        ppm_c,
                        model['context_length'],
                        model['top_provider']['max_completion_tokens']])

    df_models = pd.DataFrame(md_data,
                             columns=['provider',
                                      'model_name',
                                      'prompt_price',
                                      'completion_price',
                                      'context_length',
                                      'max_completion_tokens'])
    df_models = df_models.drop_duplicates()
    df_models.style.background_gradient()

    pd.set_option('display.width', 200)
    pd.set_option('display.precision', 3)

    df_models.to_csv('or_pricing.csv')

    return df_models


def no_duplicates(list_with_duplicates):
    return list(dict.fromkeys(list_with_duplicates))


# uncomment to see pricing in terminal
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     pp.pprint(get_models(tools_only=False, as_dataframe=True))
