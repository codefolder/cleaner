# cleaner
Allows to bulk-clean a bunch of user-defined directories like trash, temporary files, thumbnails, etc.

#To run on linux:
python cleaner.py

A successful run will create a cleaner.pickle file in the user home directory to store the settings.

#Getting an error?

1) Cleaner depends on Gtk 3 for GUI, so, for instance, if you are on Debian/Ubuntu, install it like this:

sudo apt-get install gir1.2-gtk-3.0 python-gi python3-gi python3-psutil

2) Since cleaner was refactored for Python 3, your system path to python may still point to Python 2. On Debian/Ubuntu, python3 points to the correct interpreter, so you could try:

python3 cleaner.py
