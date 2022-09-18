from core.stock_models.models import BaseModel
import pandas as pd


def prepare_response(model: BaseModel) -> dict:
    df_info = pd.DataFrame.from_dict(
        model.full_info(), orient='index', columns=['Значение']
    ).round(3).fillna('-')

    res = []
    labels = list(range(len(model.consumption)))
    for idx, (i, j) in enumerate(zip(model.balance_start, model.income_order)):
        if j == 0:
            res.append({'x': idx, 'y': i})
        else:
            res.extend([{'x': idx, 'y': i - j}, {'x': idx, 'y': i}])

    response = {
        'labels': labels,
        'balance': res,
        'income_order': model.income_order.tolist(),
        'outcome_order': model.outcome_order.tolist(),
        'consumption': model.consumption.tolist(),
        'info': df_info.to_html(
            classes='table table-striped table-hover table-sm table-dark text-light',
            border=0,
            float_format=lambda i: '{:,.3f}'.format(i),
        ),
    }
    return response
