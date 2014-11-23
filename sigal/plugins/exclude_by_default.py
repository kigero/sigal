# -*- coding: utf-8 -*-

""" Only include media in an album that has been explicitly authorized via the
index.md file in that album.

Media is specified by listing the filenames to include.  Since markdown doesn't
have comments, this plugin uses a special HTML comment to list the files, so at
least the list won't be visible in the final HTML file (though it will be
visible in the HTML source unfortunately).  A specification block looks like
this:

<!---INC
file1.jpg
file2.png
-->

Only file1.jpg and file2.png will be processed.

Note that removing a file from this list will NOT remove the processed files
from the output directory.

"""

import logging
import os
from os.path import isfile, join
from sigal import signals

logger = logging.getLogger(__name__)

# Returns true if path (lower cased) is found in incs.
def should_include(incs, path):
   p = path.lower()
   for inc in incs:
       if p.endswith(inc):
           return True
   return False

def remove_unincluded(album):
    descfile = join(album.src_path, album.description_file)
    incs = []
    if isfile(descfile):
        # Check if the album has no title; if there is no title, it may be that 
        # the album's md file is strictly for listing files.  In this case the
        # default name - the folder name - should be used.  This code is copied
        # from gallery.py, in the Album constructor.
        if album.title.strip() == "":
            album.title = os.path.basename(album.path if album.path != '.'
                                      else album.src_path)

        # Process the album's md file for includes.
        adding = False
        for line in open(descfile, "r"):
            if line.startswith("<!---INC"):
                adding = True
            elif line.startswith("-->"):
                adding = False
            elif adding and not line.strip() == "":
                incs.append('/' + line.strip().lower())
    
    logger.debug(str(len(incs)) + ' includes for album ""' + album.title + '"')

    # Remove any file that should not be included.
    origsize = len(album.medias)
    album.medias[:] = [x for x in album.medias if should_include(incs, x.src_path)]
    newsize = len(album.medias)
    logger.debug('* ' + str(origsize - newsize) + ' media items removed (' + str(newsize) + ' left).')

    return album

def register(settings):
    signals.album_initialized.connect(remove_unincluded)
