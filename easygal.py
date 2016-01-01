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

from bottle import Bottle, static_file, run, request, response, abort
from mako.template import Template

from PIL import Image

import json

try:
    import exifread
except ImportError:
    exifread = None

import os

def check_login(view):
    def wrapper(*args, **kwargs):
        try:
            _self = args[0]
        except:
            abort(500, "Internal error")

        if not request.get_cookie('authorized', secret=_self._secret):
            abort(401, "Not authorized")

        return view(*args, **kwargs)
    return wrapper

class EasyGal:
    STATIC_ROOT = "./static/"

    def __init__(self, settings=None):
        if settings == None:
            import settings as s
            self.settings = s
        else:
            self.settings = settings

        self._app = Bottle()

        self._secret = self.settings.SECRET
        self._img_root = self.settings.DATA_ROOT+"/images/"
        self._thumb_root  = self.settings.DATA_ROOT+"/thumbnails/"

        self._setup_routes()
        self._create_directories()

    def _setup_routes(self):
        for kw in dir(self):
            attr = getattr(self, kw)
            if hasattr(attr, 'route_from'):
                self._app.route(attr.route_from)(attr)
            if hasattr(attr, 'post_from'):
                self._app.post(attr.post_from)(attr)
            if hasattr(attr, 'delete_from'):
                self._app.delete(attr.delete_from)(attr)

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
    _static.route_from = [ '/static/<filename:path>' ]

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

    # Login handlers

    def _login(self):
        # TODO: Set up DB connection + verify user
        user = request.forms.get('user')
        pw = request.forms.get('password')
        if user == "admin" and pw == "admin":
            response.set_cookie('authorized', user, secret=self._secret)
            return user
        abort(401, "Not authorized")
    _login.post_from = [ '/login' ]

    def _logout(self):
        if request.get_cookie('authorized', secret=self._secret):
            response.set_cookie('authorized', '')
        return 'OK'
    _logout.post_from = [ '/logout' ]

    # Upload handler
    @check_login
    def _upload(self, gallery=""):
        upload = request.files.get('files[]')

        gallery_str = ""

        if gallery:
            gallery_str = gallery + "\\/"

        _filename   = upload.filename
        _url        = "\\/img\\/" + gallery_str + _filename
        _thumburl   = "\\/thumb\\/" + gallery_str + _filename
        _deleteurl  = "\\/delete\\/" + gallery_str + _filename

        name, ext = os.path.splitext(_filename)

        error = None

        if ext not in ('.png','.jpg','.jpeg'):
            error = "Filetype not allowed"
        else:
            savepath = os.path.join(self._img_root, gallery, _filename)
            try:
                upload.save(savepath, True)
                data = { 'files' : [
                    {
                        "name" : _filename,
                        "size" : os.path.getsize(savepath),
                        "url" : _url,
                        "thumbnailUrl": _thumburl,
                        "deleteUrl" : _deleteurl,
                        "deleteType" : "DELETE"
                    },
                ] }
            except:
                error = "Could not store file"

        if error:
            data = { 'files' : [
                {
                    "name": _filename,
                    "size": 0,
                    "error": error
                },
            ]}

        return json.dumps(data)
    _upload.post_from = [ '/upload/<gallery>' ]

    @check_login
    def _delete(self, image, gallery=""):
        result = "false"

        name, ext = os.path.splitext(image)
        if ext in ('.png','.jpg','.jpeg'):
            delpath = os.path.join(self._img_root, gallery, image)
            if os.path.exists(delpath):
                os.remove(delpath)
                result = "true"

        data = { 'files' : [
            {
                'filename' : result
            },
        ]}
        return json.dumps(data)
    _delete.delete_from = [ '/delete/<gallery>/<image>' ]

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
        user = request.get_cookie('authorized', secret=self._secret)
        if not user:
            user = ''
        return Template(filename='templates/index.html').render(user=user, sitename=self.settings.SITE_NAME, sites=sites, galleries=galleries)
    _index.route_from = [ '/' ]

    def get_app(self):
        return self._app

    def run(self):
        return run(g.get_app(), host=self.settings.HOST, port=self.settings.PORT, reloader=True, server='auto')

if __name__ == "__main__":
    g = EasyGal()
    g.run()
