# 📚 WAYA: Who Are You Again?
**Spoiler free book text searching**

While reading a book, have you ever come across a character that made you ask "Who are you again?", but then been afraid to search for infomation online in case it lead to spoilers?

WAYA is here to jog your memory by searching through the text of a book or series for past references without showing you passages you haven't read yet. WAYA is perfect for those book series with gazillions of characters (I'm looking at you Wheel of Time). 

Check out a live version of the application [here](https://elansegarra-waya-waya-9tlbj4.streamlitapp.com/)!

Using WAYA is quick and easy:
 1. Choose a preloaded book series or upload your own.
 2. Choose which book and chapter you are currently reading.
 3. Search for any character or phrase without worrying about spoilers!

Features include:
 - Several preloaded book series from project Gutenberg.
 - Ability to upload and parse your own EPUB book files.
 - Flexibility to adjust the context window around search results.
 - Launch a local version with that preloads your most used book files.

## Running WAYA Locally
To run the app locally simply install streamlit (and one additional dependency) and launch from the command line.
```
pip install streamlit streamlit-sortables
streamlit run WAYA/waya.py
```

## Setting Up Custom Preloads
To set up custom preloads you will need the .EPUB files for the books and to define some parsing parameters for these files.
The .EPUB files should be placed in the `WAYA/preloads` folder and the parsing parameters should be added to the others found in `WAYA/preloads/preloads.py`.

In particular, for every additional series (which might consist of only one book) you must add another element to the `preloaded_dicts` dictionary variable where the key is the name of the book series (e.g. "Wheel of Time") and the value is a dictionary of parameters analagous to those already found in that file.
This inner dictionary has one necessary key (`books`) and one optional key (`books_ready`), both of which are described below:
- `books` (necessary): The value is a list of dictionaries that each represent a book in the series. Each dictionary contains the following keys
  - `title` (necessary): Name of the book in the series.
  - `filename` (necessary): Path and filename of the .EPUB file of this book in the series.
  - `book_num` (optional): Number of the book in the series.
  - `include_secs` (optional): List of indices of the sections of the .EPUB file that should be included when parsing the file. An element of this list can also be a list of indices if sections should be combined (e.g. [0,1,[2,3],4] will combine the third and fourth sections). If not included, the default is to parse all sections which will likely include title pages, copyright pages, and other elements of the book that might be irrelevant for searching.
  - `sec_bs_tags` (optional): A dictionary that defines the html elements that will contain chapter/section titles. If included it should have 2 keys: `element` (string indicating which html element to search, e.g. "h2" or "h3" or "p") and `class` (list of class tags used to further identify chapter titles). If not included the parser will attempt to identify chapter titles from the first few lines of text, but this may not function well if the EPUB file is poorly formatted.
- `books_ready` (optional): The value is a list of integers indicating the indices of the books that will be parsed and included from the list under the "books" key. All other books defined there will be ignored. For instance, if there are 7 books and the value of "books_ready" is [0,1,3,5] then the first, second, fourth, and sixth books will be loaded while the third and seventh books will be ignored. If this key is not included then the default is to include all books found.
