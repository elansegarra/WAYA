import streamlit as st
import pandas as pd
import numpy as np
from ebooklib import epub
import preloads.preloads
import re
from PIL import Image
from lib.epub_parser import get_relevant_secs, extract_chapters
from streamlit_sortables import sort_items
import time

# To run from command line (in lib folder): "streamlit run waya.py --server.port 8889"

im = Image.open("img/read-book-32x32.png")
st.set_page_config(page_title="WAYA: Who Are You Again?", page_icon=im, 
                    layout="centered", initial_sidebar_state="auto", menu_items=None)

# This hides the "Made by Streamlit" and hamburger menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

###########################################################################
#### Function Definitions #################################################
###########################################################################

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

def load_book(file_loader_obj):
    # Takes a file_loader object and returns a dictionary

    # Parse filetype and extract text
    file_type = file_loader_obj.name[file_loader_obj.name.find(".")+1:]
    
    if file_type == "txt":
        book_title = file_loader_obj.name
        all_text = file_loader_obj.read().decode('UTF-8')
        chapters = [{'name':"Ch 1 Who dun it?", 'text':'...'},
                    {'name':"Ch 2 But why?!", 'text':"...."} ]
        res = all_text[0:500]
    elif file_type == "epub":
        book = epub.read_epub(file_loader_obj)
        book_title = book.get_metadata("DC", "title")[0][0]
        relevant_secs = get_relevant_secs(file_loader_obj)
        chapters = extract_chapters(file_loader_obj, secs = relevant_secs)
        res = book.get_metadata('DC', 'title')
    else:
        st.error(f"File {file_loader_obj.name} is not a recognized file type.")
        res = "ERROR DIDNT UNDERSTAND FILE TYPE"

    # Check if chapters have unique titles (if not give them ids)
    ch_titles = [ch['name'] for ch in chapters]
    if len(set(ch_titles)) < len(ch_titles):
        for i in range(len(chapters)): 
            chapters[i]['name'] = str(i).zfill(2)+" "+chapters[i]['name']

    return {"filename": file_loader_obj.name,
            "title": book_title,
            "file_type": file_type,
            "chapters": chapters}

def merge_overlapping_strings(s1, s2, min_overlap = 1):
    biggest_overlap = 0
    # Go through all suffixes of s1 (starting with single char)
    for i in range(min_overlap,len(s1)):
        # Check if suffix of s1 matches prefix of s2
        if s1[-i:] == s2[:i]:
            biggest_overlap = i
    if biggest_overlap == 0: return(s1+s2)
    else:                    return(s1[:-biggest_overlap]+s2)

# Grab and initialize the preloaded series information
if "preloaded_dicts" not in st.session_state:
    preloaded_dicts = preloads.preloads.preloaded_dicts
    for key, series in preloaded_dicts.items():
        series["loaded"] = False
        if "books_ready" not in series:
            series['books_ready'] = list(range(len(series["books"])))
        for bk in series['books']:
            if "include_secs" not in bk:
                bk["include_secs"] = None
            if "sec_bs_tags" not in bk:
                bk["sec_bs_tags"] = None
    st.session_state["preloaded_dicts"] = preloaded_dicts
else:
    preloaded_dicts = st.session_state["preloaded_dicts"]

###########################################################################
#### App - Sidebar ########################################################
###########################################################################

# Initializing sessions state for currently loaded books
if 'loaded_books' not in st.session_state:
    st.session_state['loaded_books'] = None
if 'all_books' not in st.session_state:
    st.session_state['all_books'] = None

with st.sidebar:
    all_books = []
    st.title("Which Series or Book?")
    preload_or_upload = st.radio("How to pick your series?", 
                ["Open a preloaded series", "Upload your own series"])
    if preload_or_upload == "Open a preloaded series":
        preload_names = list(["--"]+list(preloaded_dicts.keys()))
        series_choice = st.selectbox("Pick a preloaded series:", preload_names)
        # Grab the dictionary associated with the chosen series
        if series_choice != "--":
            preload_dict = preloaded_dicts[series_choice]
            all_books = preload_dict['books']
            # Load the books (along with their associated chapters) if not done
            if preload_dict['loaded'] == False :
                load_progress = st.progress(0)
                with st.spinner(f'Loading books from {series_choice}...'):
                    parse_preload(series_choice, prog_bar=load_progress)
                time.sleep(0.5)
                load_progress.empty()
    elif preload_or_upload == "Upload your own series":
        uploaded_files = st.file_uploader("Upload book(s) (from the same series in order of reading)", 
                                    accept_multiple_files=True, type = ['txt', 'epub'])
        # Process the loaded book files (after checking if they have changed)
        if st.session_state['loaded_books'] != uploaded_files:      
            load_progress = st.progress(0)
            with st.spinner(f'Processing uploaded book(s)...'):
                for i in range(len(uploaded_files)):
                    uploaded_file = uploaded_files[i]
                    bk_data = load_book(uploaded_file)
                    bk_data["book_num"] = i+1
                    all_books.append(bk_data)
                    # parse_preload(series_choice, prog_bar=load_progress)
            time.sleep(0.5)
            load_progress.empty()
            st.session_state['loaded_books'] = uploaded_files
            st.session_state['all_books'] = all_books
        else:
            all_books = st.session_state['all_books']

    # Displaying and changing the order of books
    if len(all_books) > 0:
        with st.expander("Book Order"):
            # Extract current order and display the titles
            bk_titles = [bk['title'] for bk in all_books]
            resorted_bks = sort_items(bk_titles, direction='vertical')
            # If order has changed, then reorder the books accordingly
            if bk_titles != resorted_bks:
                new_books = []
                for bk in resorted_bks:
                    new_books.append(all_books[bk_titles.index(bk)])
                all_books = new_books
                st.session_state['all_books'] = all_books

    # Current Place Inputs (sets book names and associated chapters)    
    if len(all_books) == 0:
        st.title("Pick or Upload a book/series above.")
    else:
        # Gather information on what book and chapter the user is currently reading
        st.title("Where are you currently?")
        book_names = [book["title"] for book in all_books]
        curr_book = st.selectbox("Book:", book_names)
        curr_book_dict = next(bk for bk in all_books if bk["title"] == curr_book)
        curr_bk_chapters = curr_book_dict['chapters']
        chapter_names = [ch['name'] for ch in curr_bk_chapters]
        #st.text(chapter_names)
        curr_ch = st.selectbox("Chapter:", chapter_names)
        curr_ch_dict = next(ch for ch in curr_bk_chapters if ch["name"] == curr_ch)

        # Controls for the search results
        st.title("Result Display Controls")
        context_radius = st.slider("Context radius (measured in letters):",
                                min_value = 10, max_value = 500, value = 100, step=10,
                                help="The number of letters before and after the search term that will be displayed in the results.")
        group_res_by = st.radio("Group results by:", ["Book", "Chapter"])
        # group_chs_true = st.checkbox("Group results by chapter", value=False)

# st.write([bk['title'] for bk in all_books])

###########################################################################
#### App - Main Page ######################################################
###########################################################################

st.title("WAYA: Who Are You Again?")
if len(all_books) == 0:
    st.header("Three quick steps to spoiler free searching!")
    st.write("1. Pick a preloaded book series or upload your own files in the sidebar to the left.")
    st.write("2. Choose which book and chapter you are currently reading.")
    st.write("3. Enter a search term and only the results from before where you are will be displayed!")
else:
    search_value = st.text_input("Search:", placeholder="Type a name or phrase to search for here")

    res_window = st.container()
    if search_value != "":
        # res_window.text(f'The search term is "{search_value}"')

        search_res = []
        for book in all_books:
            for ch in book['chapters']:
                # Quick indicator for if this is the current book being read
                curr_reading_this_book = (book['book_num'] == curr_book_dict['book_num'])
                # Small tweaks for when either chapter has multiple sections
                this_ch_sec, curr_ch_sec = ch['bs_sec'], curr_ch_dict['bs_sec']
                if isinstance(this_ch_sec, list): this_ch_sec = this_ch_sec[0]
                if isinstance(curr_ch_sec, list): curr_ch_sec = curr_ch_sec[0]
                # Skip searching all chapters after (and including) chapter currently being read
                if curr_reading_this_book & (this_ch_sec >= curr_ch_sec): break
                # Go through each instance of finding the search term
                for res in re.finditer(search_value, ch['text'],flags=re.IGNORECASE):
                    res_start = max(0,res.start()-context_radius)
                    res_end = res.start()+context_radius+len(search_value)
                    context = ch['text'][res_start:res_end]
                    # Check if overlap with previous result instance
                    contexts_overlap = ( (len(search_res) > 0) and 
                        (res_start - search_res[-1]["res_ind_start"] <= context_radius + len(search_value)) )
                    same_bk_ch = ( (len(search_res) > 0) and 
                        (search_res[-1]["book"] == book["title"]) and 
                        (search_res[-1]["chapter"] == ch["name"]) )
                    if contexts_overlap and same_bk_ch:
                        # Flag previous res for overlap and merge
                        search_res[-1]["overlap"] = True
                        context = merge_overlapping_strings(search_res[-1]["context"], context)
                    search_res.append({"book":book["title"], "chapter":ch['name'], 
                                        "res_ind_start":res_start, 
                                        "overlap": False, "context":context})
            # Skip searching rest of books after searching the book currently being read
            if (book['title'] == curr_book_dict['title']): break

        # Creating text with search value highlighted
        search_pattern = re.compile(search_value, re.IGNORECASE)
        # highlight = f'<span style="background-color:Yellow;">{search_value}</span>'
        highlight_start = '<span style="background-color:Yellow;">'
        highlight_end = '</span>'
        
        # Result title with total results found
        res_window.title(f"Results ({len(search_res)} instances found)")
        
        # Displaying the search results, grouped by book (and by ch is specified)
        book_res_cur = None
        ch_res_cur = None
        if len(search_res)>0:
            # Inserting results into dataframe and creating dictionary of counts by book and chapter
            res_df = pd.DataFrame(search_res)
            res_counts = res_df.groupby(by='book').agg('count')['context'].to_dict()
            res_counts_ch = res_df.groupby(by=['book','chapter']).agg('count')['context'].to_dict()

            # Iterate over results to display each
            for res_item in search_res:
                # Skip if flagged due to overlapping contexts
                if res_item["overlap"]: continue
                # Display book or chapter headings depending on choice
                if group_res_by == "Chapter":
                    # Check if the book has changed
                    if book_res_cur != res_item['book']:
                        book_res_cur = res_item['book']
                        ch_res_cur = None
                        res_window.write(f"{book_res_cur} ({res_counts[book_res_cur]} results found)")
                    # Check if chapter has changed
                    if ch_res_cur != res_item['chapter']:
                        ch_res_cur = res_item['chapter']
                        group_exp_text = f"{ch_res_cur} ({res_counts_ch[book_res_cur,ch_res_cur]} results found)"
                        res_group_exp = res_window.expander(group_exp_text)    
                elif group_res_by == "Book":
                    # Check if the book has changed
                    if book_res_cur != res_item['book']:
                        book_res_cur = res_item['book']
                        group_exp_text = f"{book_res_cur} ({res_counts[book_res_cur]} results found)"
                        res_group_exp = res_window.expander(group_exp_text)
                else:
                    raise Exception(f"The value of group_res_by={group_res_by} is not recognized")
                
                # Highlight the search terms in the context and display the context
                context = res_item['context']
                context_highlit = ""
                i = 0
                for m in search_pattern.finditer(context):
                    context_highlit += "".join([context[i:m.start()], highlight_start,
                                                context[m.start():m.end()], highlight_end])
                    i = m.end()
                context_highlit += context[m.end():]
                # context_highlit = search_pattern.sub(highlight, res_item['context']) # Old way, replaces case
                res_group_exp.markdown('"'+context_highlit+'"', unsafe_allow_html=True)
        
        # res_window.write(search_res)

