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

import settings

STATIC_ROOT = "./static/"

IMG_ROOT    = settings.DATA_ROOT+"/images/"
THUMB_ROOT  = settings.DATA_ROOT+"/thumbnails/"

egapp = Bottle()

# Helpers

def convert_fraction(fraction):
    try:
        first, last = fraction.split("/")
        return float(first) / float(last)
    except ValueError:
        return float(fraction)

def get_images(directory=None):
    d = IMG_ROOT
    if directory:
        d += directory
    return [os.path.join(directory, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]

def get_galleries():
    return [d for d in os.listdir(IMG_ROOT) if os.path.isdir(os.path.join(IMG_ROOT, d))]

# Images + thumbnails

@egapp.route('/thumb/<gallery>/<width>/<filename>')
@egapp.route('/thumb/<gallery>/<filename>')
def thumbnail(gallery, filename, width=""):
    if not width.isdigit():
        width = "600"

    w = int(width)
    if w > 1200:
        width = "1200"
    else:
        width = str(round(w, -2))

    thumbdir = os.path.join(THUMB_ROOT, gallery, width)
    thumb = os.path.join(thumbdir, filename)
    image = os.path.join(IMG_ROOT, gallery, filename)

    if not os.path.exists(thumbdir):
        os.makedirs(thumbdir)

    if not os.path.isfile(thumb) or os.path.getmtime(thumb) < os.path.getmtime(image):
        basewidth = int(width)
        img = Image.open(image)
        wpercent = (basewidth / float(img.size[0]))
        if wpercent >= 1:
            return static_file(filename, root=os.path.join(IMG_ROOT, gallery))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img.save(thumb)

    return static_file(filename, root=thumbdir)

@egapp.route('/img/<gallery>/<filename>')
def image(gallery, filename):
    return static_file(os.path.join(gallery, filename), root=IMG_ROOT)

# Static files (js/css)

@egapp.route('/static/<filename>')
def static(filename):
    return static_file(filename, root=STATIC_ROOT)

# Buttons in navbar

@egapp.route('/gallery/<selection>')
def view_gallery(selection):
    imgs = get_images(selection)
    images = []
    for i in imgs:
        text = ""
        if exifread:
            try:
                with open(os.path.join(IMG_ROOT, i), 'rb') as f:
                    tags = exifread.process_file(f)

                    fstop = convert_fraction(str(tags['EXIF FNumber']))
                    flength = convert_fraction(str(tags['EXIF FocalLength']))

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

# Generic view
@egapp.route('/<site>')
def generic_site(site):
    sites = settings.SITES
    content = "Not found"
    for s in sites:
        if s[0].lower() == site:
            content = s[1]
            break
    return Template(filename='templates/generic.html').render(content=content)

# Root directory

@egapp.route('/')
def index():
    sites = []
    galleries = []
    for s in settings.SITES:
        sites.append(s[0])
        if s[0].lower() == "gallery":
            galleries = get_galleries()
    return Template(filename='templates/index.html').render(sitename=settings.SITE_NAME, sites=sites, galleries=galleries)

if __name__ == "__main__":
    if not os.path.exists(IMG_ROOT):
        os.makedirs(IMG_ROOT)
    if not os.path.exists(THUMB_ROOT):
        os.makedirs(THUMB_ROOT)

    run(egapp, host=settings.HOST, port=settings.PORT, reloader=True)
