# -*- coding: utf-8 -*-
from uwsgi_sloth.structures import ValuesAggregation

def test_ValuesAggregation():
    agr = ValuesAggregation()
    agr.add_values(range(1, 101))
    assert agr.get_result() == {'max': 100, 'avg': 50.5, 'min': 1}
    assert agr.avg == 50.5

    # Test merge with
    agr1 = ValuesAggregation(values=range(1, 11))
    agr2 = ValuesAggregation(values=range(-10, 0))
    agr3 = ValuesAggregation(values=range(100, 201))
    assert agr1.merge_with(agr2).get_result() == {'max': 10, 'avg': 0.0, 'min': -10}
    assert agr1.merge_with(agr3).get_result() == {
        'max': 200, 
        'avg': (sum(range(1, 11)) + sum(range(100, 201))) / 111.0, 
        'min': 1
    }

