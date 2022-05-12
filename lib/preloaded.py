import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

# Defining the preloaded series and associated files
preloaded_dicts = {"Wheel of Time":{ 
                        "books":[{"title": "", "book_num": 1,
                                "filename": "Jordan, Robert - 01 - The Eye of the World.epub"},
                            {"title": "", "book_num": 2,
                                    "filename": "Jordan, Robert - 02 - The Great Hunt.epub"},
                            {"title": "", "book_num": 3,
                                    "filename": "Jordan, Robert - 03 - The Dragon Reborn.epub"},
                            {"title": "", "book_num": 4,
                                    "filename": "Jordan, Robert - 04 - The Shadow Rising.epub"},
                            {"title": "", "book_num": 5,
                                    "filename": "Jordan, Robert - 05 - The Fires of Heaven.epub"},
                            {"title": "", "book_num": 6,
                                    "filename": "Jordan, Robert - 06 - Lord of Chaos.epub"},
                            {"title": "", "book_num": 7,
                                    "filename": "Jordan, Robert - 07 - A Crown of Swords.epub"},
                            {"title": "", "book_num": 8,
                                    "filename": "Jordan, Robert - 08 - The Path of Daggers.epub"},
                            {"title": "", "book_num": 9,
                                    "filename": "Jordan, Robert - 09 - Winter's Heart.epub"},
                            {"title": "", "book_num": 10,
                                    "filename": "Jordan, Robert - 10 - Crossroads of Twilight.epub"},
                            {"title": "", "book_num": 11,
                                    "filename": "Jordan, Robert - 11 - Knife of Dreams.epub"},
                            {"title": "", "book_num": 12,
                                    "filename": "Jordan, Robert - 12 - The Gathering Storm.epub"},
                            {"title": "", "book_num": 13,
                                    "filename": "Jordan, Robert - 13 - Towers of Midnight.epub"},
                            {"title": "", "book_num": 14,
                                    "filename": "Jordan, Robert - 14 - A Memory of Light.epub"}
                            ]},
                    "Lord of the Rings": {
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
                    "Harry Potter":{
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


def extract_chapters(file_loader_obj, secs = None, method_label = None, title_bs_tags = None):
    # Takes a file_loader and extracts chapter data from specified sections
    book = epub.read_epub(file_loader_obj)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    if secs == None:
        secs = range(len(items))

    all_ch_data = []
    for i in secs:
        # print(i)
        ch_data = extract_ch_data(items[i].get_body_content(), 
                                    method_label=method_label,
                                    title_bs_tags=title_bs_tags)
        ch_data["bs_sec"] = i
        # print(ch_data['name'])
        all_ch_data.append(ch_data)
    return all_ch_data

def extract_ch_data(html, method_label = None, title_bs_tags = None):
    # Takes HTML and returns the title
    soup = BeautifulSoup(html, 'html.parser')
    # text = soup.find_all(text=True)
    # text = soup.get_text()

    if method_label == "WoT1":
        # Extract ch title elements using the tags passed
        ch_title_elements = soup.find_all(title_bs_tags['element'], {'class':title_bs_tags['class']})
        ch_title = [item.text.strip() for item in ch_title_elements]
        # Extract all the body text (everything after last element of ch title)
        all_text = soup.get_text() 
        ch_text = all_text[all_text.find(ch_title[-1])+len(ch_title[-1]):].strip()
        #ch_text = ch_text[0:25]+'  ...  '+ch_text[-25:]
        # Cleaning titles (must do after getting rest of text, or it won't match title found in text)
        ch_title = [' '.join([wd.strip() for wd in text.split()]) for text in ch_title]
        # Assemble chapter info dict
        ch_data = {"name": " ".join(ch_title), "text": ch_text}
    return ch_data


wot_sec_dicts = {1:[6]+list(range(8,61)),
                2: list(range(9,60)),
                3: list(range(9,66)),
                4: list(range(9,67)),
                5: list(range(9,66)),
                6: list(range(9,66))}
wot_mlabels = {1:"WoT1", 2:"WoT1", 3:"WoT1", 4:"WoT1",
                5:"WoT1", 6:"WoT1"}
wot_bs_tags = {1:{'element':"p", 'class': ["h4","h3 sgc-2", "tx15 sgc-2"]},
                2: {'element':"p", 'class': ["h47", "tx428 sgc-2", "tx428"]},
                3: {'element':"h2", 'class': ["h2", "h2a"]},
                4: {'element':"h2", 'class': ["h2", "h2a"]},
                5: {'element':["h2", "h3"], 'class':["h2", "h3"]},
                6: {'element':["h2"], 'class':["h2", "h2a", "h2c"]}}


# Extract chapters from each books of WoT
series_index = "Wheel of Time"
folder_wot = "C:\\Users\\Phoenix\\Documents\\Literature\\Fiction\\Robert Jordan\\"
for book_dict in preloaded_dicts[series_index]["books"]:
    # Set some of the basic book attributes
    filename = book_dict["filename"]
    file_full_path = folder_wot+filename
    book = epub.read_epub(file_full_path)
    book_dict["title"] = book.get_metadata("DC", "title")[0][0]
    book_dict["file_type"] = filename[filename.find(".")+1:]
    book_dict["chapters"] = [{'name':"TBD", 'text':"",'bs_sec':0}]

for book_dict in preloaded_dicts[series_index]["books"][0:6]:#0,1,2,3,4]: #[0,1,2]:
    # Grab the filename and some metatdata
    filename = book_dict["filename"]
    book_num = book_dict['book_num']
    file_full_path = folder_wot+filename
    # Extract the chapters
    ch_data = extract_chapters(file_full_path, secs = wot_sec_dicts[book_num], 
                                method_label = wot_mlabels[book_num],
                                title_bs_tags = wot_bs_tags[book_num])
    # print(ch_data)
    # print(" ")
    book_dict["chapters"] = ch_data


book_index = 4

file_loader_obj1 = folder_wot+preloaded_dicts[series_index]["books"][book_index]["filename"]
book = epub.read_epub(file_loader_obj1)
items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

# WoT #1 starts on sec 7 (ie sec 6 is the prologue, sec 7 is ch 1)
sec = 55

# print(book.get_metadata("DC", "title")[0][0])

# ch_data = items[sec].get_body_content()

# soup = BeautifulSoup(items[sec].get_body_content(), 'html.parser')
# print(soup.prettify()[0:900])

# ch_data = [item.text.strip() for item in soup.find_all(["h2", "h3"], {"class":["h2", "h3"]})]

# all_text = soup.get_text() 
# ch_data = all_text[all_text.find(ch_title)+len(ch_title):].strip()

# print("")
# print((ch_data[0:900]))

