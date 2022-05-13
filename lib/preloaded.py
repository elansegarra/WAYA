import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from epub_parser import extract_ch_data, extract_chapters

# Defining the preloaded series and associated files
folder_wot = "C:\\Users\\Phoenix\\Documents\\Literature\\Fiction\\Robert Jordan\\"
preloaded_dicts = {
    "Wheel of Time":{ "loaded": False,
        "books":[{"title": "", "book_num": 1,
                "filename": folder_wot+"Jordan, Robert - 01 - The Eye of the World.epub",
                "include_secs": [6]+list(range(8,61)),
                "sec_bs_tags": {'element':"p", 'class': ["h4","h3 sgc-2", "tx15 sgc-2"]}},
            {"title": "", "book_num": 2,
                "filename": folder_wot+"Jordan, Robert - 02 - The Great Hunt.epub",
                "include_secs": list(range(9,60)),
                "sec_bs_tags": {'element':"p", 'class': ["h47", "tx428 sgc-2", "tx428"]}},
            {"title": "", "book_num": 3,
                "filename": folder_wot+"Jordan, Robert - 03 - The Dragon Reborn.epub",
                "include_secs": list(range(9,66)),
                "sec_bs_tags": {'element':"h2", 'class': ["h2", "h2a"]}},
            {"title": "", "book_num": 4,
                "filename": folder_wot+"Jordan, Robert - 04 - The Shadow Rising.epub",
                "include_secs": list(range(9,67)),
                "sec_bs_tags": {'element':"h2", 'class': ["h2", "h2a"]}},
            {"title": "", "book_num": 5,
                "filename": folder_wot+"Jordan, Robert - 05 - The Fires of Heaven.epub",
                "include_secs": list(range(9,66)),
                "sec_bs_tags": {'element':["h2", "h3"], 'class':["h2", "h3"]}},
            {"title": "", "book_num": 6,
                "filename": folder_wot+"Jordan, Robert - 06 - Lord of Chaos.epub",
                "include_secs": list(range(9,66)),
                "sec_bs_tags": {'element':["h2"], 'class':["h2", "h2a", "h2c"]}},
            {"title": "", "book_num": 7,
                "filename": folder_wot+"Jordan, Robert - 07 - A Crown of Swords.epub",
                "include_secs": list(range(8,50)),
                "sec_bs_tags": {'element':["h2"], 'class':["h2", "h2b", "h2c"]}},
            {"title": "", "book_num": 8,
                "filename": folder_wot+"Jordan, Robert - 08 - The Path of Daggers.epub"},
            {"title": "", "book_num": 9,
                "filename": folder_wot+"Jordan, Robert - 09 - Winter's Heart.epub"},
            {"title": "", "book_num": 10,
                "filename": folder_wot+"Jordan, Robert - 10 - Crossroads of Twilight.epub"},
            {"title": "", "book_num": 11,
                "filename": folder_wot+"Jordan, Robert - 11 - Knife of Dreams.epub"},
            {"title": "", "book_num": 12,
                "filename": folder_wot+"Jordan, Robert - 12 - The Gathering Storm.epub"},
            {"title": "", "book_num": 13,
                "filename": folder_wot+"Jordan, Robert - 13 - Towers of Midnight.epub"},
            {"title": "", "book_num": 14,
                "filename": folder_wot+"Jordan, Robert - 14 - A Memory of Light.epub"}
            ]},
    "Lord of the Rings": { "loaded": False,
        "books":[{"title": "The Fellowship of the Ring",
                "book_num": 1,
                "filename": "TBD1.epub",
                "file_type": "epub",
                "chapters": [{"name": "Ch 1", "text": "So it begins"},
                            {"name": "Ch 2", "text": "More happens"}]},
            {"title": "The Two Towers",
                    "book_num": 2,
                    "filename": "TBD2.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"},
                                {"name": "Ch 2", "text": "More happens"},
                                {"name": "Ch 3", "text": "So it begins"}]},
            {"title": "The Return of the King",
                    "book_num": 3,
                    "filename": "TBD3.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"},
                                {"name": "Ch 2", "text": "More happens"},
                                {"name": "Ch 3", "text": "So it begins"},
                                {"name": "Ch 4", "text": "So it begins"}]},
            ]},
    "Harry Potter":{ "loaded": False,
        "books":[{"title": "Philosopher's Stone",
                "book_num": 1,
                "filename": "TBD1.epub",
                "file_type": "epub",
                "chapters": [{"name": "Ch 1", "text": "So it begins"}]},
            {"title": "Chamber of Secrets",
                    "book_num": 2,
                    "filename": "TBD2.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"}]},
            {"title": "Prisoner of Azkaban",
                    "book_num": 3,
                    "filename": "TBD3.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"}]},
            {"title": "Goblet of Fire",
                    "book_num": 4,
                    "filename": "TBD4.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"}]},
            {"title": "Order of the Phoenix",
                    "book_num": 5,
                    "filename": "TBD5.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"}]},
            {"title": "Half-Blood Prince",
                    "book_num": 6,
                    "filename": "TBD6.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"}]},
            {"title": "Deathly Hallows",
                    "book_num": 7,
                    "filename": "TBD7.epub",
                    "file_type": "epub",
                    "chapters": [{"name": "Ch 1", "text": "So it begins"}]},
            ]},}


def parse_preload(series_name, book_subset = None, prog_bar = None):
    # Verify that the name is recognized
    assert series_name in preloaded_dicts.keys(), f"preload series {series_name} not found."
    # If book_subset is not passed set it to all books found in the series
    if book_subset is None:
        book_subset = list(range(0,len(preloaded_dicts[series_name]["books"])))
    # Check that book_subset is in range
    assert(max(book_subset) < len(preloaded_dicts[series_name]["books"])), f"Book subet ({book_subset}) out of range"
    assert(0 <= min(book_subset)), f"Book subet ({book_subset}) out of range"
    
    # Load metadata from all book in series
    for book_dict in preloaded_dicts[series_name]["books"]:
        # Set some of the basic book attributes
        file_path = book_dict["filename"]
        book = epub.read_epub(file_path)
        book_dict["title"] = book.get_metadata("DC", "title")[0][0]
        book_dict["file_type"] = file_path[file_path.find(".")+1:]
        book_dict["chapters"] = [{'name':"TBD", 'text':"",'bs_sec':0}]
    
    # Load chapter data only for those in the subset
    prog_i = 1
    for book_dict in [preloaded_dicts[series_name]["books"][i] for i in book_subset]:
        # Update progress bar (if passed)
        if prog_bar is not None:
            prog_bar.progress(prog_i/len(book_subset))
            prog_i += 1
        # Grab the filename and some metatdata
        file_path = book_dict["filename"]
        book_num = book_dict['book_num']
        # Extract the chapters
        ch_data = extract_chapters(file_path, secs = book_dict["include_secs"], 
                                    method_label = "WoT1",
                                    title_bs_tags = book_dict["sec_bs_tags"])
        book_dict["chapters"] = ch_data
    
    # Turn on flag indicating the series has been loaded
    preloaded_dicts[series_name]["loaded"] = True



series_index = "Wheel of Time"
book_index = 5

file_loader_obj1 = preloaded_dicts[series_index]["books"][book_index-1]["filename"]
book = epub.read_epub(file_loader_obj1)
items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

# WoT #1 starts on sec 7 (ie sec 6 is the prologue, sec 7 is ch 1)
sec = 66

# print(book.get_metadata("DC", "title")[0][0])

# ch_data = items[sec].get_body_content()

# soup = BeautifulSoup(items[sec].get_body_content(), 'html.parser')
# print(soup.prettify()[0:900])

# ch_data = [item.text.strip() for item in soup.find_all(["h2", "h3"], {"class":["h2", "h3"]})]

# all_text = soup.get_text() 
# ch_data = all_text[all_text.find(ch_title)+len(ch_title):].strip()

# print("")
# print((ch_data[0:900]))

