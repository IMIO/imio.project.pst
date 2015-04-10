from collective.excelexport.interfaces import IStyles
from collective.excelexport.styles import Styles

from zope.component import adapts
from zope.interface import implements, Interface

import xlwt


class PSTPolicyStyles(Styles):

    headers = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; '
                         'align: wrap on, vert centre, horiz center; '
                         'borders: top thin, bottom thin, left thin, right thin; '
                         'pattern: pattern solid, back_colour yellow, fore_colour yellow; '
                         )

    content = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold off; '
                     'align: wrap on, vert centre, horiz left;'
                     'borders: top thin, bottom thin, left thin, right thin;'
                     'pattern: pattern solid, back_colour light_yellow, fore_colour light_yellow'
                     )


class PSTOSStyles(Styles):

    def __init__(self, context):
        pass

    implements(IStyles)
    adapts(Interface)

    headers = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; '
                         'align: wrap on, vert centre, horiz center; '
                         'borders: top thin, bottom thin, left thin, right thin; '
                         'pattern: pattern solid, back_colour yellow, fore_colour yellow; '
                         )

    content = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold off; '
                     'align: wrap on, vert centre, horiz left;'
                     'borders: top thin, bottom thin, left thin, right thin;'
                     'pattern: pattern solid, back_colour bright_green, fore_colour bright_green'
                     )


class PSTOOStyles(Styles):

    def __init__(self, context):
        pass

    implements(IStyles)
    adapts(Interface)

    headers = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; '
                         'align: wrap on, vert centre, horiz center; '
                         'borders: top thin, bottom thin, left thin, right thin; '
                         'pattern: pattern solid, back_colour yellow, fore_colour yellow; '
                         )

    content = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold off; '
                     'align: wrap on, vert centre, horiz left;'
                     'borders: top thin, bottom thin, left thin, right thin;'
                     'pattern: pattern solid, back_colour light_orange, fore_colour light_orange'
                     )


class PSTActionStyles(Styles):

    def __init__(self, context):
        pass

    implements(IStyles)
    adapts(Interface)

    headers = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; '
                         'align: wrap on, vert centre, horiz center; '
                         'borders: top thin, bottom thin, left thin, right thin; '
                         'pattern: pattern solid, back_colour yellow, fore_colour yellow; '
                         )

    content = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold off; '
                     'align: wrap on, vert centre, horiz left;'
                     'borders: top thin, bottom thin, left thin, right thin;'
                     'pattern: pattern solid, back_colour sky_blue, fore_colour sky_blue'
                     )
