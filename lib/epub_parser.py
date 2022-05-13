import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from numpy import median


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
        ch_text = ch_text[0:25]+'  ...  '+ch_text[-25:]
        # Cleaning titles (must do after getting rest of text, or it won't match title found in text)
        ch_title = [' '.join([wd.strip() for wd in text.split()]) for text in ch_title]
        # Assemble chapter info dict
        ch_data = {"name": " ".join(ch_title), "text": ch_text}
    return ch_data

def get_relevant_secs(epub_file):
    # Returns a list of the sections that appear to be actual chapters

    # Open the epub file
    book = epub.read_epub(epub_file)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    
    # Get the number of characters from the actual text of each section
    sec_lens = []
    for i in range(len(items)):
        soup = BeautifulSoup(items[i].get_body_content(), 'html.parser')
        # print(f"Section {i} text has {len(soup.get_text())} characters")
        sec_lens.append(len(soup.get_text()))
    
    # Section needs at least 20% of median length to be relevant
    char_len_thresh = median(sec_lens)/5 
    relevant_secs = [i for i in range(len(sec_lens)) if sec_lens[i] >= char_len_thresh]

    return relevant_secs