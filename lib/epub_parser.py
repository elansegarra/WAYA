import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from numpy import log10


def extract_chapters(file_loader_obj, secs = None, title_bs_tags = None, 
                        prog = None):
    # Takes a file_loader and extracts chapter data from specified sections
    book = epub.read_epub(file_loader_obj)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    if secs == None:
        secs = range(len(items))

    all_ch_data = []
    for sec in secs:
        # Combine sections if this element is a list
        if isinstance(sec, list):
            sec_html = b""
            for sec_element in sec:
                sec_html = sec_html + items[sec_element].get_body_content()
        else:
            sec_html = items[sec].get_body_content()
        ch_data = extract_ch_data(sec_html, title_bs_tags=title_bs_tags)
        ch_data["bs_sec"] = sec
        # print(ch_data['name'])
        all_ch_data.append(ch_data)
        # Update the progress bar (if passed)
        if prog is not None:
            num_secs_done = secs.index(sec)+1
            prog_curr = prog["prog_curr"] + prog["bk_contrib"]*num_secs_done/len(secs)
            prog_curr = min(prog_curr, 1)
            prog["st_prog"].progress(prog_curr)

    # Check if chapters have unique titles (if not give them ids)
    ch_titles = [ch['name'] for ch in all_ch_data]
    if len(set(ch_titles)) < len(ch_titles):
        num_digits = int(log10(len(ch_titles))+1)
        for i in range(len(all_ch_data)): 
            all_ch_data[i]['name'] = str(i).zfill(num_digits)+" "+all_ch_data[i]['name']

    return all_ch_data

def extract_ch_data(html, title_bs_tags = None):
    # Takes HTML and returns the title

    soup = BeautifulSoup(html, 'html.parser')
    # text = soup.find_all(text=True)
    # text = soup.get_text()

    if title_bs_tags is not None:
        # Extract ch title elements using the tags passed
        ch_title_elements = soup.find_all(title_bs_tags['element'], {'class':title_bs_tags['class']})
        ch_title = [item.text.strip() for item in ch_title_elements if item.text.strip() != ""]
        # if "chapter-title" in title_bs_tags['class']: print(ch_title)
        # Extract all the body text (everything after last element of ch title)
        all_text = soup.get_text() 
        ch_text = all_text[all_text.find(ch_title[-1])+len(ch_title[-1]):].strip()
        # ch_text = ch_text[0:25]+'  ...  '+ch_text[-25:]
        # Cleaning titles (must do after getting rest of text, or it won't match title found in text)
        ch_title = [' '.join([wd.strip() for wd in text.split()]) for text in ch_title]
        # Assemble chapter info dict
        ch_data = {"name": " ".join(ch_title), "text": ch_text}
    else:
        # Grab all text and split by line breaks
        all_text = soup.get_text().split("\n")
        # Peg first few short lines for title and rest as text
        ch_title = ''
        ch_text_start = -1
        for i in range(len(all_text)):
            # Add next line if short and if title is not already too long
            if (len(ch_title) < 25) and (len(all_text[i]) < 50):
                ch_title += (" "+all_text[i])
            else:
                ch_text_start = i
                break
        # Checking if either too too much or too little pulled into the title
        if (len(ch_title) > 150) or (ch_text_start==0):
            ch_title = "Ch Title Unknown"
            ch_text = "\n".join(all_text)
        else: # OTherwise we simply say rest of text is the ch text
            ch_text = "\n".join(all_text[ch_text_start:])
        ch_data = {"name":ch_title.strip(), "text":ch_text}

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
    char_len_thresh = np.median(sec_lens)/10
    relevant_secs = [i for i in range(1,len(sec_lens)) if sec_lens[i] >= char_len_thresh]

    return relevant_secs