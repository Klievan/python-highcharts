#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python-Highmaps is a Python wrapper for Highmaps graph library.
For Highcharts Licencing Visit:
http://shop.highsoft.com/highcharts.html
Project location : xxxxx
"""

from __future__ import unicode_literals
from optparse import OptionParser
from jinja2 import Environment, PackageLoader
# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

# from slugify import slugify
import json, uuid
import datetime, random, os, inspect
from _abcoll import Iterable
from options import BaseOptions, ChartOptions, \
    ColorsOptions, ColorAxisOptions, CreditsOptions, DrilldownOptions, ExportingOptions, \
    GlobalOptions, LabelsOptions, LangOptions, \
    LegendOptions, LoadingOptions, MapNavigationOptions, NavigationOptions, PaneOptions, \
    PlotOptions, SeriesData, SubtitleOptions, TitleOptions, \
    TooltipOptions, xAxisOptions, yAxisOptions, MultiAxis

from highmap_types import Series, SeriesOptions, HighchartsError
from common import Formatter, CSSObject, SVGObject, MapObject, JSfunction, RawJavaScriptText, \
    CommonObject, ArrayObject, ColorObject

CONTENT_FILENAME = "./content.html"
PAGE_FILENAME = "./page.html"

pl = PackageLoader('highmaps', 'templates')
jinja2_env = Environment(lstrip_blocks=True, trim_blocks=True, loader=pl)

template_content = jinja2_env.get_template(CONTENT_FILENAME)
template_page = jinja2_env.get_template(PAGE_FILENAME)
    
DEFAULT_POINT_INTERVAL = 86400000

class Highmaps(object):
    """
    Highcharts Base class.
    """
    #: chart count
    count = 0

    # this attribute is overriden by children of this
    # class
    CHART_FILENAME = None
    template_environment = Environment(lstrip_blocks=True, trim_blocks=True,
                                       loader=pl)

    def __init__(self, **kwargs):
        """
        This is the base class for all the charts. The following keywords are
        accepted:
        :keyword: **display_container** - default: ``True``
        """
        # set the model
        self.model = self.__class__.__name__  #: The chart model,
        self.div_name = kwargs.get("renderTo", "container")

        # an Instance of Jinja2 template
        self.template_page_highcharts = template_page
        self.template_content_highcharts = template_content
        
        # set Javascript src

        self.JSsource = [
                'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js',
                'http://code.highcharts.com/highcharts.js',
                'http://code.highcharts.com/maps/modules/map.js',
                'https://code.highcharts.com/maps/modules/data.js',
                'https://code.highcharts.com/maps/modules/exporting.js'
            ]

        # set CSS src

        self.CSSsource = [
                'https://www.highcharts.com/highslide/highslide.css',

            ]
        # set data
        self.data = []
        self.data_temp = []
        # data from jsonp
        self.jsonp_data_flag = False

        # set drilldown data
        self.drilldown_data = []
        self.drilldown_data_temp = []

        # map
        self.map = None

        # jsonp map
        self.jsonp_map_flag = kwargs.get('jsonp_map_flag', False)

        # javascript
        self.jscript_head_flag = False
        self.jscript_head = kwargs.get('jscript_head', None)
        self.jscript_end_flag = False
        self.jscript_end = kwargs.get('jscript_end', None)

        # accepted keywords
        self.div_style = kwargs.get('style', '')
        self.drilldown_flag = kwargs.get('drilldown_flag', False)
        self.date_flag = kwargs.get('date_flag', False)

        # None keywords attribute that should be modified by methods
        # We should change all these to _attr

        self.htmlcontent = ''  #: written by buildhtml
        self.htmlheader = ''
        #: Place holder for the graph (the HTML div)
        #: Written by ``buildcontainer``
        self.container = u''
        #: Header for javascript code
        self.containerheader = u''
        
        # Default Nulls // ?
        self.hold_point_start = None
        self.hold_point_interval = None
        self.start_date_set = None

        # Bind Base Classes to self
        self.options = {
            "chart": ChartOptions(),
            #"colorAxis": ColorAxisOptions(), # cannot put in until there is data
            "colors": ColorsOptions(),
            "credits": CreditsOptions(),
            #"data": #NotImplemented
            "drilldown": DrilldownOptions(),
            "exporting": ExportingOptions(),
            "labels": LabelsOptions(),
            "legend": LegendOptions(),
            "loading": LoadingOptions(),
            "mapNavigation": MapNavigationOptions(),
            "navigation": NavigationOptions(),
            "plotOptions": PlotOptions(),
            "series": SeriesData(),
            "subtitle": SubtitleOptions(),
            "title": TitleOptions(),
            "tooltip": TooltipOptions(),
            "xAxis": xAxisOptions(),
            "yAxis": yAxisOptions(),
        }

        self.setOptions = {
            "global": GlobalOptions(),
            "lang": LangOptions(),
        }

        self.__load_defaults__()

        # Process kwargs
        allowed_kwargs = [
            "width",
            "height",
            "renderTo",
            "backgroundColor",
            "events",
            "marginBottom",
            "marginTop",
            "marginRight",
            "marginLeft"
        ]

        for keyword in allowed_kwargs:
            if keyword in kwargs:
                self.options['chart'].update_dict(**{keyword:kwargs[keyword]})
        # Some Extra Vals to store:
        self.data_set_count = 0
        self.drilldown_data_set_count = 0


    def __load_defaults__(self):
        self.options["chart"].update_dict(renderTo='container')
        self.options["title"].update_dict(text='A New Highchart')
        self.options["credits"].update_dict(enabled=False)


    def title(self, title=None):
        """ Bind Title """
        if not title:
            return self.options["title"].text
        else:
            self.set_options("title", {'text':title})


    def colors(self, colors=None):
        """ Bind Color Array """
        if not colors:
            return self.options["colors"].__jsonable__() if self.options['colors'].__jsonable__() else None
        else:
            self.options["colors"].set_colors(colors)


    # def chart_background(self, background=None):
    #     """ Apply Chart Background """
    #     if not background:
    #         return self.options["chart"].backgroundColor
    #     else:
    #         self.options["chart"].update_dict(backgroundColor=background)

    def set_JSsource(self, new_src):
        if isinstance(new_src, list):
            for h in list:
                self.JSsource.append(h)
        elif isinstance(new_src, basestring):
            self.JSsource.append(new_src)
        else:
            raise OptionTypeError("Option: %s Not Allowed For Series Type: %s" % type(new_src))


    def set_CSSsource(self, new_src):
        if isinstance(new_src, list):
            for h in new_src:
                self.CSSsource.append(h)
        elif isinstance(new_src, basestring):
            self.CSSsource.append(new_src)
        else:
            raise OptionTypeError("Option: %s Not Allowed For Series Type: %s" % type(new_src))


    def add_data_set(self, data, series_type="map", name=None, **kwargs):
        """ Set data for series option in highcharts """
        self.data_set_count += 1
        if not name:
            name = "Series %d" % self.data_set_count
        kwargs.update({'name':name})
        if self.hold_point_start:
            kwargs.update({"pointStart":self.hold_point_start})
            self.hold_point_start = None
        if self.hold_point_interval:
            kwargs.update({"pointInterval":self.hold_point_interval})
            self.hold_point_interval = None

        if self.map and 'mapData' in kwargs.keys():
            kwargs.update({'mapData': self.map})
        series_data = Series(data, series_type=series_type, **kwargs)
       
        series_data.__options__().update(SeriesOptions(series_type=series_type, **kwargs).__options__())
        self.data_temp.append(series_data)


    def add_drilldown_data_set(self, data, series_type, id, **kwargs):
        """ Set data for drilldown option in highcharts """
        self.drilldown_data_set_count += 1
        if self.drilldown_flag == False:
            self.drilldown_flag = True
        
        kwargs.update({'id':id})
        series_data = Series(data, series_type=series_type, **kwargs)
       
        series_data.__options__().update(SeriesOptions(series_type=series_type, **kwargs).__options__())
        self.drilldown_data_temp.append(series_data)

    def add_data_from_jsonp(self, data_src, data_name = 'json_data', series_type="map", name=None, **kwargs):
        self.jsonp_data_flag = True
        self.jsonp_data_url = json.dumps(data_src)
        if data_name == 'data':
            data_name = 'json_'+ data_name
        self.jsonp_data = data_name
        self.add_data_set(RawJavaScriptText(data_name), series_type, name=name, **kwargs)

    def add_jscript(self, js_script, js_loc):
        if js_loc == 'head':
            self.jscript_head_flag = True
            self.jscript_head = js_script
        elif js_loc == 'end':
            self.jscript_end_flag = True
            self.jscript_end = js_script
        else:
            raise OptionTypeError("Not An Accepted script location: %s, either 'head' or 'end'" 
                                % js_loc)

    def set_map_source(self, map_src = "http://code.highcharts.com/mapdata/", map_name = 'geojson', jsonp_map = False):
        """Set Map data"""
        # The default is to use js script from highcharts' map collection: http://code.highcharts.com/mapdata/

        if  jsonp_map:
            self.jsonp_map_flag = True
            if map_name == 'data':
                map_name = 'geojson_'+ map_name
            self.map = map_name
            self.jsonp_map_url = json.dumps(map_src)
        else:
            map_src = map_src+map_name+'.js'
            self.set_JSsource(map_src)
            self.map = 'Highcharts.maps["' + map_name + '"]'

        if self.data_temp:
            self.data_temp[0].__options__().update({'mapData': MapObject(self.map)})

    def set_options(self, option_type, option_dict, force_options=False):
        """ Set Plot Options """
        if force_options:
            self.options[option_type].update(option_dict)
        elif option_type == 'plotOptions':
            for key in option_dict.keys():
                self.options[option_type].update_dict(**{key:SeriesOptions(key,**option_dict[key])})
        elif (option_type == 'yAxis' or option_type == 'xAxis') and isinstance(option_dict, list):
            self.options[option_type] = MultiAxis(option_type)
            for each_dict in option_dict:
                self.options[option_type].update(**each_dict)
        elif option_type == 'colorAxis':
            self.options.update({"colorAxis": ColorAxisOptions()})
            self.options[option_type].update_dict(**option_dict)
        else:
            self.options[option_type].update_dict(**option_dict)


    def set_dict_optoins(self, options):
        for key, option_data in options.items():
            self.set_options(key, option_data)


    def set_containerheader(self, containerheader):
        """Set containerheader"""
        self.containerheader = containerheader


    def __str__(self):
        """return htmlcontent"""
        self.buildhtml()
        return self.htmlcontent


    def file(self, filename = 'highmaps'):
        """ save htmlcontent as .html file """
        filename = filename + '.html'
        
        with open(filename, 'w') as f:
            self.buildhtml()
            f.write(self.htmlcontent)
        
        f.closed

    def buildcontent(self):
        """Build HTML content only, no header or body tags. To be useful this
        will require the attribute `juqery_on_ready` to be set which
        will wrap the js in $(function(){<regular_js>};)
        """
        self.buildcontainer()
        #self.buildjschart()
        self.option = json.dumps(self.options, encoding='utf8', cls = HighchartsEncoder)
        self.setoption = json.dumps(self.setOptions, cls = HighchartsEncoder) 
        self.data = json.dumps(self.data_temp, encoding='utf8', cls = HighchartsEncoder)
        
        if self.drilldown_flag: 
            tmp_dict = {} # put drilldown data set into a dict
            tmp_dict.update({'series': self.drilldown_data_temp})
            self.drilldown_data_temp = tmp_dict
            self.drilldown_data = json.dumps(self.drilldown_data_temp, encoding='utf8', \
                                            cls = HighchartsEncoder)
        self.htmlcontent = self.template_content_highcharts.render(chart=self).encode('utf-8')


    def buildhtml(self):
        """Build the HTML page
        Create the htmlheader with css / js
        Create html page
        Add Js code for highcharts
        """
        self.buildcontent()
        self.buildhtmlheader()
        self.content = self.htmlcontent.decode('utf-8') # need to ensure unicode
        self.htmlcontent = self.template_page_highcharts.render(chart=self).encode('utf-8')


    def buildhtmlheader(self):
        """generate HTML header content"""
        #Highcharts lib/ needs to make sure it's up to date
        
        if self.drilldown_flag:
            self.set_JSsource('http://code.highcharts.com/modules/drilldown.js')

        self.header_css = [
            '<link href="%s" rel="stylesheet" />' % h for h in self.CSSsource
        ]

        self.header_js = [
            '<script type="text/javascript" src="%s"></script>' % h for h in self.JSsource
        ]

        self.htmlheader = ''
        for css in self.header_css:
            self.htmlheader += css
        for js in self.header_js:
            self.htmlheader += js


    def buildcontainer(self):
        """generate HTML div"""
        if self.container:
            return
        # Create HTML div with style
        if self.options['chart'].width:
            if str(self.options['chart'].width)[-1] != '%':
                self.div_style += 'width:%spx;' % self.options['chart'].width
            else:
                self.div_style += 'width:%s;' % self.options['chart'].width
        if self.options['chart'].height:
            if str(self.options['chart'].height)[-1] != '%':
                self.div_style += 'height:%spx;' % self.options['chart'].height
            else:
                self.div_style += 'height:%s;' % self.options['chart'].height

        self.div_name = self.options['chart'].__dict__['renderTo'] # recheck div name
        self.container = self.containerheader + \
            '<div id="%s" style="%s"></div>\n' % (self.div_name, self.div_style)


    # def buildjschart(self):
    #     """generate javascript code for the chart"""
    #     self.jschart = ''


class TemplateMixin(object):
    """
    A mixin that override buildcontent. Instead of building the complex
    content template we exploit Jinja2 inheritance. Thus each chart class
    renders it's own chart template which inherits from content.html
    """
    def buildcontent(self):
        """Build HTML content only, no header or body tags. To be useful this
        will usually require the attribute `juqery_on_ready` to be set which
        will wrap the js in $(function(){<regular_js>};)
        """
        self.buildcontainer()
        # if the subclass has a method buildjs this method will be
        # called instead of the method defined here
        # when this subclass method is entered it does call
        self.buildjschart()
        self.htmlcontent = self.template_chart_highcharts.render(chart=self).encode('utf-8')


class HighchartError(Exception):
    """ Highcharts Error Class """
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.args = args


class HighchartsEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        json.JSONEncoder.__init__(self, *args, **kwargs)
        self._replacement_map = {}

    def default(self, obj):
        if isinstance(obj, RawJavaScriptText):
            key = uuid.uuid4().hex
            self._replacement_map[key] = obj.get_jstext()
            return key
        elif isinstance(obj, datetime.datetime):
            utc = obj.utctimetuple()
            obj = (u"Date.UTC({year},{month},{day},{hours},{minutes},{seconds},{millisec})"
                    .format(year=utc[0], month=utc[1]-1, day=utc[2], hours=utc[3],
                            minutes=utc[4], seconds=utc[5], millisec=obj.microsecond/1000))
            return RawJavaScriptText(obj)
        elif isinstance(obj, BaseOptions) or isinstance(obj, MultiAxis):
            return obj.__jsonable__()
        elif isinstance(obj, CSSObject) or isinstance(obj, Formatter) or isinstance(obj, JSfunction) \
            or isinstance(obj, MapObject): 
            return obj.__options__()
        elif isinstance(obj, SeriesOptions) or isinstance(obj, Series):
            return obj.__options__()
        elif isinstance(obj, CommonObject) or isinstance(obj, ArrayObject) or isinstance(obj, ColorObject):
            return obj.__options__()
        else:
            return json.JSONEncoder.default(self, obj)

    def encode(self, obj):
        result = json.JSONEncoder.encode(self, obj).decode('utf-8')
        for k, v in self._replacement_map.items():
            result = result.replace('"%s"' % (k,), v.decode('utf-8'))
        return result


class OptionTypeError(Exception):

    def __init__(self,*args):
        self.args = args


def _main():
    """
    Parse options and process commands
    """
    # Parse arguments
    usage = "usage: highcharts.py [options]"
    parser = OptionParser(usage=usage, version="python-highcharts - Charts generator with Highcharts library")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print messages to stdout")

    (options, args) = parser.parse_args()


if __name__ == '__main__':
    _main()