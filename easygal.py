#!/usr/bin/python3

# EasyGal - A simple, photo gallery for the web based on Python3.
# Copyright (C) 2015  Andreas Hofmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from bottle import Bottle, static_file, run
from mako.template import Template

from PIL import Image

try:
    import exifread
except ImportError:
    exifread = None

import os

class EasyGal:
    STATIC_ROOT = "./static/"

    def __init__(self, settings=None):
        if settings == None:
            import settings as s
            self.settings = s
        else:
            self.settings = settings

        self._app = Bottle()

        self._img_root = self.settings.DATA_ROOT+"/images/"
        self._thumb_root  = self.settings.DATA_ROOT+"/thumbnails/"

        self._setup_routes()
        self._create_directories()

    def _setup_routes(self):
        for kw in dir(self):
            attr = getattr(self, kw)
            if hasattr(attr, 'route_from'):
                self._app.route(attr.route_from)(attr)

    def _create_directories(self):
        if not os.path.exists(self._img_root):
            os.makedirs(self._img_root)
        if not os.path.exists(self._thumb_root):
            os.makedirs(self._thumb_root)

    @staticmethod
    def _convert_fraction(fraction):
        try:
            first, last = fraction.split("/")
            return float(first) / float(last)
        except ValueError:
            return float(fraction)

    def _get_images(self, directory=None):
        d = self._img_root
        if directory:
            d += directory
        return [os.path.join(directory, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]

    def _get_galleries(self):
        g = [d for d in os.listdir(self._img_root) if os.path.isdir(os.path.join(self._img_root, d))]
        g.sort()
        return g

    # Images + thumbnails

    def _thumbnail(self, gallery, filename, width=""):
        if not width.isdigit():
            width = "600"

        w = int(width)
        if w > 1200:
            width = "1200"
        else:
            width = str(round(w, -2))

        thumbdir = os.path.join(self._thumb_root, gallery, width)
        thumb = os.path.join(thumbdir, filename)
        image = os.path.join(self._img_root, gallery, filename)

        if not os.path.exists(thumbdir):
            os.makedirs(thumbdir)

        if not os.path.isfile(thumb) or os.path.getmtime(thumb) < os.path.getmtime(image):
            basewidth = int(width)
            img = Image.open(image)
            wpercent = (basewidth / float(img.size[0]))
            if wpercent >= 1:
                return static_file(filename, root=os.path.join(self._img_root, gallery))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(thumb)

        return static_file(filename, root=thumbdir)
    _thumbnail.route_from = [ '/thumb/<gallery>/<width>/<filename>',
                             '/thumb/<gallery>/<filename>' ]

    def _image(self, gallery, filename):
        return static_file(os.path.join(gallery, filename), root=self._img_root)
    _image.route_from = [ '/img/<gallery>/<filename>' ]

    # Static files (js/css)

    def _static(self, filename):
        return static_file(filename, root=self.STATIC_ROOT)
    _static.route_from = [ '/static/<filename>' ]

    # Buttons in navbar

    def _view_gallery(self, selection):
        imgs = self._get_images(selection)
        images = []
        for i in imgs:
            text = ""
            if exifread:
                try:
                    with open(os.path.join(self._img_root, i), 'rb') as f:
                        tags = exifread.process_file(f)

                        fstop = self._convert_fraction(str(tags['EXIF FNumber']))
                        flength = self._convert_fraction(str(tags['EXIF FocalLength']))

                        text += "Shot on " + str(tags['EXIF DateTimeOriginal'])
                        text += " with a " + str(tags['Image Make'])
                        text += " " + str(tags['Image Model'])
                        text += ", " + str(flength) + "mm"
                        text += ", F" + str(fstop)
                        text += ", "+ str(tags['EXIF ExposureTime']) + "s"
                        text += ", ISO " + str(tags['EXIF ISOSpeedRatings'])
                        text += ", " + str(tags['EXIF ExposureBiasValue']) + " EV"
                        text += " in " + str(tags['EXIF ExposureProgram'])
                        text += ". Edited with " + str(tags['Image Software']) + "."
                except:
                    text = ""

            images.append([i, text])

        return Template(filename='templates/gallery.html').render(imgs=images, name=selection)
    _view_gallery.route_from = '/gallery/<selection>'

    # Generic view
    def _generic_site(self, site):
        sites = self.settings.SITES
        content = "Not found"
        for s in sites:
            if s[0].lower() == site:
                content = s[1]
                break
        return Template(filename='templates/generic.html').render(content=content)
    _generic_site.route_from = [ '/<site>' ]

    # Root directory

    def _index(self):
        sites = []
        galleries = []
        for s in self.settings.SITES:
            sites.append(s[0])
            if s[0].lower() == "gallery":
                galleries = self._get_galleries()
        return Template(filename='templates/index.html').render(sitename=self.settings.SITE_NAME, sites=sites, galleries=galleries)
    _index.route_from = [ '/' ]

    def get_app(self):
        return self._app

    def run(self):
        return run(g.get_app(), host=self.settings.HOST, port=self.settings.PORT, reloader=True, server='auto')

if __name__ == "__main__":
    g = EasyGal()
    g.run()
