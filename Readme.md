# EasyGal - A simple, photo gallery for the web based on Python3.

EasyGal is a straightforward gallery website, which displays the contents of a
directory as thumbnails on a webpage, throws in fancybox integration, displays
EXIF data in the images and allows to add some extra info/about/anything-pages.

As you may have guessed, it lacks all the fancy stuff which current photo
blogs, communities and the like are offering (comments, tags, rating system or
even user accouts). It is meant as a simple way to put up some photos on a
(private) website without much fuss - just copy your images to the
image-folder, and let the gallery do the rest.

## Installation
### Install required python modules
Using pip3:
`pip3 install bottle mako`

For EXIF-tag parsing, you also need exifread:
`pip3 install exifread`

Under Debian-based you may run alternatively:
`sudo apt-get install python3-bottle python3-mako`

### Run the gallery
- Edit settings.py to suit your needs (see comments for details)
- Place some images in the data directory
- Run it: `./easygal.py`

## TODO
- Support for direct WSGI integration into Apache/nginx/etc.
- Web-upload for images
- Support for geotags in images

## Components used
* Bottle
* exifread
* Mako
* Python Imaging Library (PIL)
* jQuery
* bootstrap
* fancybox
