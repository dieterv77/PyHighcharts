import os.path
import random
import datetime
import collections

import numpy as np
import pandas

from jinja2 import Template

from PyHighcharts import Highstock, Highchart

default_size = (900,900)

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

def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

MULTICHART_TEMPLATE="""
<html>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
<head>
{{ needs }}
</head>
<body>
<ul>
{% for chart in charts %}
    <li><a href="#{{ chart.container }}">{{ chart.title }}</a></li>
{% endfor %}
</ul>
{% for chart in charts %}
    <a name="{{ chart.container }}" />
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
        self.title = chart.title()
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

    def write(self, temp_dir='.', fname=None, localurl=False):
        template_charts = []
        for idx, chart in enumerate(self.charts):
            template_charts.append(TemplateChart(idx, chart))

        html = self.template.render(needs=self.charts[0].need(), charts=template_charts)
        if localurl:
            html = html.replace('https://ajax.googleapis.com/ajax/libs/jquery/1.7.2','/js')
            html = html.replace('http://code.highcharts.com','/js')
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
        update(options, {'title' : {'text': kwargs['title']}})
    if 'x_title' in kwargs:
        update(options, {'xAxis': {'title' : {'text': kwargs['x_title']}}})
    if 'y_title' in kwargs:
        update(options, {'yAxis': {'title' : {'text': kwargs['y_title']}}})
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
    """Create bar chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    """

    index = df.index
    size = kwargs.get('size', default_size)
    H = Highchart(width=size[0], height=size[1], renderTo='container')
    for colname, data in df.iteritems():
        H.add_data_set(data.values, type='bar', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    update(options, {'xAxis': {'categories': index.tolist()}})
    update(options, __getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

@Appender(otherparams)
def createBoxChart(df, **kwargs):
    """Create box chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    """

    size = kwargs.get('size', default_size)
    H = Highchart(width=size[0], height=size[1], renderTo='container')
    df = df.dropna(axis=1, how='all')
    boxdata = pandas.DataFrame({'min': df.min(), 'max': df.max(), '0.25': df.quantile(0.25), '0.75': df.quantile(0.75), 'median': df.median()})
    boxdata = boxdata.reindex(columns=['min', '0.25', 'median', '0.75', 'max'])
    H.add_data_set(boxdata.values.tolist(), type='boxplot', name='Observations')
    options = {'chart': {'zoomType': 'x', 'type': 'boxplot'}}
    update(options, {'xAxis': {'categories': boxdata.index.tolist()}})
    update(options, __getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

@Appender(otherparams)
def createColumnChart(df, **kwargs):
    """Create columns chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    """
    index = df.index
    size = kwargs.get('size', default_size)
    H = Highchart(width=size[0], height=size[1], renderTo='container')
    for colname, data in df.iteritems():
        H.add_data_set(data, type='column', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    update(options, {'xAxis': {'categories': index.tolist()}})
    update(options, __getOptionUpdatesFromKwargs(kwargs))
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

    size = kwargs.get('size', default_size)
    H = Highchart(width=size[0], height=size[1], renderTo='container')

    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='line', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    if is_dates:
        update(options, {'xAxis': {'type': 'datetime'}})
    update(options, __getOptionUpdatesFromKwargs(kwargs))
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

    size = kwargs.get('size', default_size) 
    H = Highstock(width=size[0], height=size[1], renderTo='container')

    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='line', name=colname)
    options = {'chart': {'zoomType': 'x'}, 
               'legend': {'enabled': True},
               'tooltip': {'shared': False},
                }
    if is_dates:
        update(options, {'xAxis': {'type': 'datetime'}})
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

@Appender(otherparams)
def createScatterChart(df, pairs=None, **kwargs):
    """Scatter plot pairs of columns of given DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    pairs : dict
        Dict mapping names to pairs (tuples) of columns names
        in df.  This describes each series that will be plotted
    ref : If it is not None, then construct a regression line through
          first pair for reference.  If a tuple of size two is passed,
          it is treated as the (intercept, slope) of a line, otherwise
          OLS is used to determine the intercept and slope

    """
    size = kwargs.get('size', default_size)
    H = Highchart(width=size[0], height=size[1], renderTo='container')
    if pairs is None:
        pairs = {'data': (df.columns[0], df.columns[1])}
    if isinstance(pairs, dict):
        data = sorted(pairs.iteritems(), key=lambda x: x[0])
    else:
        data = pairs
    ref = kwargs.get('ref', None)
    for name, (x,y) in data:
        H.add_data_set(zip(df[x], df[y]), type='scatter', name=name)
        if ref is not None:
            xvals = np.linspace(min(df[x]), max(df[x]), 100)
            if isinstance(ref, tuple):
                if len(ref) != 2:
                    raise ValueError('Tuple should be of size 2')
                (a,b) = ref
                yvals = a + xvals * b 
                H.add_data_set(zip(xvals,yvals), type='spline', name='%s = %.3f + %.3f %s' % (y, a, b, x))
            else:
                import statsmodels.api as sm
                result = sm.OLS(df[y], sm.add_constant(df[[x]])).fit()
                params = result.params
                (a,b) = params['const'], params[x]
                yvals = a + xvals * b 
                H.add_data_set(zip(xvals,yvals), type='spline', name='%s = %.3f + %.3f %s (%.2f %%)' % (y, a, b, x, 100*result.rsquared))

    options = {'chart': {'zoomType': 'xy'}}
    update(options, __getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H


