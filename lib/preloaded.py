import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from lib.epub_parser import extract_ch_data, extract_chapters

# Defining the preloaded series and associated files
folder_wot = "C:\\Users\\Phoenix\\Documents\\Literature\\Fiction\\Robert Jordan\\"
preload_folder = "res\\preloads\\"
preloaded_dicts = {
    "War and Peace":{ "loaded": False, "books_ready": [],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Tolstoy] War and Peace.epub",
                "include_secs": [0,1,2],
                "sec_bs_tags": {'element':"p", 'class': ["h4","h3 sgc-2", "tx15 sgc-2"]}},
            ]},
    "A Tale of Two Cities": { "loaded": False, "books_ready": [],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Dickens] A Tale of Two Cities.epub",
                "include_secs": [0,1,2],
                "sec_bs_tags": {'element':"p", 'class': ["h4","h3 sgc-2", "tx15 sgc-2"]}},
            ]},
    "Pride and Prejudice":{ "loaded": False, "books_ready": [],
        "books":[{"title": "", "book_num": 1,
                "filename": preload_folder+"[Austen] Pride and Prejudice.epub",
                "include_secs": [0,1,2],
                "sec_bs_tags": {'element':"p", 'class': ["h4","h3 sgc-2", "tx15 sgc-2"]}},
            ]},
    }

# Gather additional preloads from root/user/ (if they exist)
import user.preloads
preloaded_dicts.update(user.preloads.preloaded_dicts)

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

