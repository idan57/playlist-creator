# playlist-creator
## Overview
Our API is was created as part of the course "Introduction to Optimization" with Ariel Rosenfeld at Bar-Ilan University.

You are able to run our API by providing the following as args:

-h, --help            show this help message and exit \
-s SONGS_PATH, --songs_path SONGS_PATH Path to songs in a directory\
-r ARTISTS_LIST, --artists_list ARTISTS_LIST Path to artists file list \
-l ALBUMS_LIST, --albums_list ALBUMS_LIST Path to albums file list \
-g GENRES_LIST, --genres_list GENRES_LIST Path to genres file list \
-d DOWN, --down DOWN  Minimum time for playlist \
-u UP, --up UP        Maximum time for playlist \
-m MINIMUM_SONGS, --minimum_songs MINIMUM_SONGS Minimum songs required from input\
-c COUNTRY, --country COUNTRY  Country name to base playlist on \

### SONGS_PATH
Should be a path to songs in the following format: "ARTIST NAME - SONG NAME"


### ARTISTS_LIST
txt file like follows:

Elton John \
David Bowie \
Queen \
Pink Floyd \
Rod Stewart \
Eric Clapton \
Prince \
John Lennon \
Bob Dylan \
Led Zeppelin

### ALBUMS_LIST
txt file like follows:

After Hours,The Weeknd \
Evolve,Imagine Dragons

### GENRES_LIST
json file like follows:

{ \
	"pop": 2, \
	"rock": 1, \
	"metal": 2 \
}

The numbers are the number of songs you want from each genre. 