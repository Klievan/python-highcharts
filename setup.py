import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

ns = {}
with open(os.path.join(here, 'highcharts', 'version.py')) as f:
   exec(f.read(), {}, ns)

setup(
    name='python-highcharts',
    version=ns['__version__'],
    author='Kyper Developers',
    author_email='developers@kyperdata.com',

    packages=find_packages(),
    package_data={
        'highcharts.highcharts': ['templates/*.html'],
        'highcharts.highmaps': ['templates/*.html'],
        'highcharts.highstock': ['templates/*.html']
    },
    url='https://git.kyper.co/kyper/kyper-data',
    description='Python Highcharts wrapper',
    install_requires=[
        "Jinja2",
        "future"
    ],
    classifiers         = [
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
