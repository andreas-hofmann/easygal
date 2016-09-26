# EasyGal - A simple photo gallery for the web based on Python3.

EasyGal is a straightforward gallery website, which displays the contents of a
directory as thumbnails on a webpage, throws in fancybox integration, displays
EXIF data for the images and allows to add some extra info/about/anything-pages.

As you may have guessed, it lacks all the fancy stuff which current photo
blogs, communities and the like are offering (comments, tags, rating system or
even user accouts). It is meant as a simple way to put up some photos on a
(private) website without much fuss - just copy your images to the
image-folder, and let the gallery do the rest.

## Installation
### Install required python modules
Using pip3:
`sudo pip3 install bottle mako PIL`

For EXIF-tag parsing, you also need exifread:
`sudo pip3 install exifread`

Under Debian-based systemss you may alternatively run:
`sudo apt-get install python3-bottle python3-mako python3-pil`

### Run the gallery
- Edit settings.py to suit your needs (see comments for details)
- Place some images in the data directory
- Either run it: `./easygal.py` - Or add the WSGI-script to your webserver's configuration.

### Example config for Apache2 under Debian
- Install mod\_wsgi for python3: `sudo apt-get install libapache2-mod-wsgi-py3`
- Add the following lines to your server configuration:
Make sure the data-directory specified in settings.py is writable!

        WSGIDaemonProcess easygal user=www-data group=www-data processes=1 threads=5
        WSGIScriptAlias / /var/www/easygal/easygal.wsgi

        <Directory /var/www/easygal>
            WSGIProcessGroup easygal
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>

- Restart apache: `sudo service apache2 restart`

## TODO
- Support for geotags in images

## Components used
* Bottle
* exifread
* Mako
* Python Imaging Library (PIL)
* jQuery
* bootstrap
* fancybox
