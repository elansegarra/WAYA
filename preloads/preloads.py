import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from lib.epub_parser import extract_ch_data, extract_chapters

# Defining the preloaded series and associated files
folder_wot = "C:\\Users\\Phoenix\\Documents\\Literature\\Fiction\\Robert Jordan\\"
preload_folder = "res\\preloads\\"
preloaded_dicts = {
    "The Divine Comedy":{ "loaded": False, "books_ready": [0,1,2],
        "books":[{"title": "Vol 1: Inferno", "book_num": 1,
                    "filename": preload_folder+"[Alighieri] The Divine Comedy - 1 - Hell.epub",
                    "include_secs": list(range(1,35)),
                    "sec_bs_tags": {'element':"h2", 'class': []}},
                {"title": "Vol 2: Purgatorio", "book_num": 2,
                    "filename": preload_folder+"[Alighieri] The Divine Comedy - 2 - Purgatory.epub",
                    "include_secs": list(range(1,34)),
                    "sec_bs_tags": {'element':"h2", 'class': []}},
                {"title": "Vol 3: Paradiso", "book_num": 3,
                    "filename": preload_folder+"[Alighieri] The Divine Comedy - 3 - Paradise.epub",
                    "include_secs": list(range(1,34)),
                    "sec_bs_tags": {'element':"h2", 'class': []}}
            ]},
    "War and Peace":{ "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Tolstoy] War and Peace.epub",
                "include_secs": list(range(2,383)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "A Tale of Two Cities": { "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Dickens] A Tale of Two Cities.epub",
                "include_secs": list(range(1,49)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "Pride and Prejudice":{ "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Austen] Pride and Prejudice.epub",
                "include_secs": list(range(1,62)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "Frankenstein": { "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Shelley] Frankenstein.epub",
                "include_secs": list(range(1,29)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "The Time Machine":{ "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Wells] The Time Machine.epub",
                "include_secs": list(range(1,18)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    }

# Gather additional preloads from root/user/ (if they exist)
try:
    import user.preloads
    preloaded_dicts.update(user.preloads.preloaded_dicts)
except ImportError or ModuleNotFoundError:
    print("No user defined preloads found")

def parse_preload(series_name, book_subset = None, prog_bar = None):
    # Verify that the name is recognized
    assert series_name in preloaded_dicts.keys(), f"preload series {series_name} not found."
    # If book_subset is not passed set it to all books found in the series
    if book_subset is None:
        # book_subset = list(range(0,len(preloaded_dicts[series_name]["books"])))
        book_subset = preloaded_dicts[series_name]["books_ready"]
        if len(book_subset) == 0: return
    # Check that book_subset is in range
    assert(max(book_subset) < len(preloaded_dicts[series_name]["books"])), f"Book subet ({book_subset}) out of range"
    assert(0 <= min(book_subset)), f"Book subet ({book_subset}) out of range"
    
    # Load metadata from all book in series
    for book_dict in preloaded_dicts[series_name]["books"]:
        # Set some of the basic book attributes
        file_path = book_dict["filename"]
        book = epub.read_epub(file_path)
        if (book_dict["title"] == ""):
            book_dict["title"] = book.get_metadata("DC", "title")[0][0]
        book_dict["file_type"] = file_path[file_path.find(".")+1:]
        book_dict["chapters"] = [{'name':"TBD", 'text':"",'bs_sec':0}]
    
    # Create dict for tracking progress if progress bar passed
    prog_dict = None
    if prog_bar is not None:
        prog_dict = {"st_prog":prog_bar, 
                    "bk_contrib":1/len(book_subset),
                    "prog_curr": 0}
    # Load chapter data only for those in the subset
    for book_dict in [preloaded_dicts[series_name]["books"][i] for i in book_subset]:
        # Grab the filename and some metatdata
        file_path = book_dict["filename"]
        book_num = book_dict['book_num']
        # Extract the chapters
        ch_data = extract_chapters(file_path, secs = book_dict["include_secs"],
                                    title_bs_tags = book_dict["sec_bs_tags"],
                                    prog = prog_dict)
        book_dict["chapters"] = ch_data
        # Update progress bar (if passed)
        if prog_bar is not None:
            prog_dict["prog_curr"] += 1/len(book_subset)
    
    # Turn on flag indicating the series has been loaded
    preloaded_dicts[series_name]["loaded"] = True