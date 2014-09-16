import os.path
import random

import pandas

from jinja2 import Template

from PyHighcharts import Highstock, Highchart

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

def __getOptionUpdatesFromKwargs(kwargs):
    options = {}
    if 'title' in kwargs:
        options.update({'title' : {'text': kwargs['title']}})
    if 'x_title' in kwargs:
        options.update({'xAxis': {'title' : {'text': kwargs['x_title']}}})
    if 'y_title' in kwargs:
        options.update({'yAxis': {'title' : {'text': kwargs['y_title']}}})
    return options

def createBarChart(df, **kwargs):
    """Create line chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    Other parameters
    ----------------
    title : string, optional
        Chart title
    """
    index = df.index
    H = Highchart(width=500, height=500, renderTo='container')
    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='bar', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

def createColumnChart(df, **kwargs):
    """Create line chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    Other parameters
    ----------------
    title : string, optional
        Chart title
    """
    index = df.index
    H = Highchart(width=500, height=500, renderTo='container')
    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='bar', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

def createLineChart(df, **kwargs):
    """Create line chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    Other parameters
    ----------------
    title : string, optional
        Chart title
    """
    is_dates = False
    index = df.index
    if isinstance(index, pandas.DatetimeIndex):
        is_dates = True
        index = index.to_pydatetime()

    H = Highchart(width=500, height=500, renderTo='container')

    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='line', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    if is_dates:
        options.update({'xAxis': {'type': 'datetime'}})
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

def createStockChart(df, **kwargs):
    """Create stock chart from DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    
    Other parameters
    ----------------
    title : string, optional
        Chart title
    """
    is_dates = False
    index = df.index
    if isinstance(index, pandas.DatetimeIndex):
        is_dates = True
        index = index.to_pydatetime()

    H = Highstock(width=500, height=500, renderTo='container')

    for colname, data in df.iteritems():
        H.add_data_set(zip(index, data), type='line', name=colname)
    options = {'chart': {'zoomType': 'x'}}
    if is_dates:
        options.update({'xAxis': {'type': 'datetime'}})
    options.update(__getOptionUpdatesFromKwargs(kwargs))
    H.set_options(options)

    return H

def createScatterChart(df, pairs, **kwargs):
    """Scatter plot pairs of columns of given DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data
    pairs : dict
        Dict mapping names to pairs (tuples) of columns names
        in df.  This describes each series that will be plotted

    Other parameters
    ----------------
    title : string, optional
        Chart title
    """
    H = Highchart(width=500, height=500, renderTo='container')
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


