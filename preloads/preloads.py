import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from lib.epub_parser import extract_ch_data, extract_chapters

# Defining the preloaded series and associated files
preload_folder = "preloads\\"
preloaded_dicts = {
    "The Divine Comedy (by Alighieri)":{ "loaded": False, "books_ready": [0,1,2],
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
    "War and Peace (by Tolstoy)":{ "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Tolstoy] War and Peace.epub",
                "include_secs": list(range(2,383)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "A Tale of Two Cities (by Dickens)": { "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Dickens] A Tale of Two Cities.epub",
                "include_secs": list(range(1,49)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "Pride and Prejudice (by Austen)":{ "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Austen] Pride and Prejudice.epub",
                "include_secs": list(range(1,62)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "Frankenstein (by Shelley)": { "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Shelley] Frankenstein.epub",
                "include_secs": list(range(1,29)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    "The Time Machine (by Wells)":{ "loaded": False, "books_ready": [0],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Wells] The Time Machine.epub",
                "include_secs": list(range(1,18)),
                "sec_bs_tags": {'element':"h2", 'class': []}},
            ]},
    }

# Gather additional preloads from a custom preload file (if it exists)
try:
    import preloads.my_preloads
    preloaded_dicts.update(preloads.my_preloads.preloaded_dicts)
except ImportError or ModuleNotFoundError:
    print("No additional user defined preloads found")