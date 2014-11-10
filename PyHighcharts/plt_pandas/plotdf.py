import os.path
import random
import datetime

import pandas

from jinja2 import Template

from PyHighcharts import Highstock, Highchart

def indent(text, indents=1):
    if not text or not isinstance(text, str):
        return ''
    jointext = ''.join(['\n'] + ['    '] * indents)
    return jointext.join(text.split('\n'))

class Appender(object):
    """
    A function decorator that will append an addendum to the docstring
    of the target function.

    This decorator should be robust even if func.__doc__ is None
    (for example, if -OO was passed to the interpreter).

    Usage: construct a docstring.Appender with a string to be joined to
    the original docstring. An optional 'join' parameter may be supplied
    which will be used to join the docstring and addendum. e.g.

    add_copyright = Appender("Copyright (c) 2009", join='\n')

    @add_copyright
    def my_dog(has='fleas'):
        "This docstring will have a copyright below"
        pass
    """
    def __init__(self, addendum, join='', indents=0):
        if indents > 0:
            self.addendum = indent(addendum, indents=indents)
        else:
            self.addendum = addendum
        self.join = join

    def __call__(self, func):
        func.__doc__ = func.__doc__ if func.__doc__ else ''
        self.addendum = self.addendum if self.addendum else ''
        docitems = [func.__doc__, self.addendum]
        func.__doc__ = self.join.join(docitems)
        return func

MULTICHART_TEMPLATE="""
<html>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
<head>
{{ needs }}
</head>
<body>
{% for chart in charts %}
    <div id="{{ chart.container }}" style="width: 100%;"></div>
{% endfor %}

{% for chart in charts %}
<script type='text/javascript'>
    {{ chart.data }}
</script>
{% endfor %}
</body>
</html>
"""
class TemplateChart(object):
    def __init__(self, idx, chart):
        self.chart = chart
        self.idx = idx
        self.container = 'chart%d' % idx
        self.chart.options['chart'].renderTo = self.container
        self.data = self.chart.generate()

class MultiChart(object):
    def __init__(self, charts=None):
        if charts is None:
            charts = []
        self.charts = list(charts)
        self.template = Template(MULTICHART_TEMPLATE)

    def addChart(self, chart):
        self.charts.append(chart)

    def write(self, temp_dir='.', fname=None):
        template_charts = []
        for idx, chart in enumerate(self.charts):
            template_charts.append(TemplateChart(idx, chart))

        html = self.template.render(needs=self.charts[0].need(), charts=template_charts)
        if fname is None:
            new_filename = "%x.html" % (random.randint(pow(16, 5), pow(16, 6)-1))
        else:
            new_filename = fname
        new_fn = os.path.join(temp_dir, new_filename)
        with open(new_fn, 'wb') as file_open:
            file_open.write(html)

otherparams = \
"""
    Other parameters
    ----------------
    title : string, optional
        Chart title
    x_title: string, optional
        X-axis title
    y_title: string, optional
        Y-axis title
    size: tuple, option
        Tuple with (width, height)
"""

def __getOptionUpdatesFromKwargs(kwargs):
    options = {}
    if 'title' in kwargs:
        options.update({'title' : {'text': kwargs['title']}})
    if 'x_title' in kwargs:
        options.update({'xAxis': {'title' : {'text': kwargs['x_title']}}})
    if 'y_title' in kwargs:
        options.update({'yAxis': {'title' : {'text': kwargs['y_title']}}})
    return options

def __getIndex(index):
    is_dates = False
    if isinstance(index, pandas.DatetimeIndex):
        is_dates = True
        index = index.to_pydatetime()
    elif isinstance(index[0], datetime.date):
        is_dates = True
        index = [datetime.datetime(d.year,d.month,d.day) for d in index]
    elif isinstance(index[0], datetime.date):
        is_dates = True
    return index, is_dates

@Appender(otherparams)
def createBarChart(df, **kwargs):
    """Create line chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    """

    index = df.index
    size = kwargs.get('size', (500,500))
    H = Highchart(width=size[0], height=size[1], renderTo='container')
    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='bar', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

@Appender(otherparams)
def createColumnChart(df, **kwargs):
    """Create line chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    """
    index = df.index
    size = kwargs.get('size', (500,500))
    H = Highchart(width=size[0], height=size[1], renderTo='container')
    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='bar', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

@Appender(otherparams)
def createLineChart(df, **kwargs):
    """Create line chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    """
    index, is_dates = __getIndex(df.index)

    size = kwargs.get('size', (500,500))
    H = Highchart(width=size[0], height=size[1], renderTo='container')

    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='line', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    if is_dates:
        options.update({'xAxis': {'type': 'datetime'}})
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

@Appender(otherparams)
def createStockChart(df, **kwargs):
    """Create stock chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    """
    index, is_dates = __getIndex(df.index)

    size = kwargs.get('size', (500,500))
    H = Highstock(width=size[0], height=size[1], renderTo='container')

    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='line', name=colname)
    options = {'chart': {'zoomType': 'x'}, 
               'legend': {'enabled': True},
               'tooltip': {'shared': False},
                }
    if is_dates:
        options.update({'xAxis': {'type': 'datetime'}})
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

@Appender(otherparams)
def createScatterChart(df, pairs, **kwargs):
    """Scatter plot pairs of columns of given DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    pairs : dict
        Dict mapping names to pairs (tuples) of columns names
        in df.  This describes each series that will be plotted

    """
    size = kwargs.get('size', (500,500))
    H = Highchart(width=size[0], height=size[1], renderTo='container')
    if isinstance(pairs, dict):
        data = sorted(pairs.iteritems(), key=lambda x: x[0])
    else:
        data = pairs
    for name, (x,y) in data:
        H.add_data_set(zip(df[x], df[y]), type='spline', name=name)
    options = {'chart': {'zoomType': 'xy'}}
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H


