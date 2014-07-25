import pandas

from PyHighcharts import Highstock, Highchart

class MultiChart(object):
    def __init__(self, charts):
        self.charts = list(charts)

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
    if 'title' in kwargs:
        options.update({'title' : {'text': kwargs['title']}})
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
    if 'title' in kwargs:
        options.update({'title' : {'text': kwargs['title']}})
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
    if 'title' in kwargs:
        options.update({'title' : {'text': kwargs['title']}})
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
    if 'title' in kwargs:
        options.update({'title' : {'text': kwargs['title']}})
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
    for name, (x,y) in pairs.iteritems():
        H.add_data_set(zip(df[x], df[y]), type='scatter', name=name)
    options = {'chart': {'zoomType': 'xy'}}
    if 'title' in kwargs:
        options.update({'title' : {'text': kwargs['title']}})
    H.set_options(options)

    return H


