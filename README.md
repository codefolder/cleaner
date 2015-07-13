# cleaner
Allows to bulk-clean a bunch of user-defined directories like trash, temporary files, thumbnails, etc.

#To run on linux:
python cleaner.py

A successful run will create a cleaner.pickle file in the user home directory to store the settings.

#Getting an error?

1) Cleaner depends on tkinter (tk) for GUI, so, for instance, if you are on Ubuntu, install it like this:

sudo apt-get install python3-tk

2) Since cleaner was refactored for Python 3, your system path to python may still point to Python 2. On Ubuntu, python3 points to the correct interpreter, so you could try:

python3 cleaner.py
