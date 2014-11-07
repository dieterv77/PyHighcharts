from distutils.core import setup

setup(
    name='PyHighcharts',
    version='0.0.5',
    author='Dieter Vandenbussche',
    author_email='',
    packages=['PyHighcharts', 'PyHighcharts.highcharts', 'PyHighcharts.plt_pandas'],
    package_data={'PyHighcharts': ['templates/*.tmp']},
    url='',
    description='',
    long_description=open('README.md').read(),
)
