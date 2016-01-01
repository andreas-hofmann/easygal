# Data directory to use. Must be  writable.
# Directories containing images must be placed inside the
# "images" directory inside this folder.
DATA_ROOT = "./data/"

# The name of the site (will be visible in the top left corner)
SITE_NAME = "example-site"

# The IP/hostname to listen on
HOST      = "localhost"

# The port to listen on
PORT      = 8080

# Enabled sites in ["Site", "Content"]-format. "Gallery" does not need any
# content, it searches in DATA_ROOT/images/ for it's content.
# Links to the sites are placed in the navigation bar in the order they appear
# here.
SITES = [
    ["Home", "Home goes here"],
    ["Gallery"],
    ["About", "About goes here"],
]
