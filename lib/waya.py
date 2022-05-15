import streamlit as st
import pandas as pd
import numpy as np
import ebooklib
from ebooklib import epub
import preloaded
import re
from PIL import Image
from preloaded import parse_preload
from epub_parser import get_relevant_secs, extract_chapters
import time

# To run from command line (in lib folder): "streamlit run waya.py --server.port 8889"

im = Image.open("../img/read-book-32x32.png")
st.set_page_config(page_title="WAYA: Who Are You Again?", page_icon=im, 
                    layout="centered", initial_sidebar_state="auto", menu_items=None)

###########################################################################
#### Function Definitions #################################################
###########################################################################

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

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

def load_epub_book(file_loader_obj):
    return "What?!"

def merge_overlapping_strings(s1, s2, min_overlap = 1):
    biggest_overlap = 0
    # Go through all suffixes of s1 (starting with single char)
    for i in range(min_overlap,len(s1)):
        # Check if suffix of s1 matches prefix of s2
        if s1[-i:] == s2[:i]:
            biggest_overlap = i
    if biggest_overlap == 0: return(s1+s2)
    else:                    return(s1[:-biggest_overlap]+s2)

# Grab the preloaded series information
preloaded_dicts = preloaded.preloaded_dicts

###########################################################################
#### App Running ##########################################################
###########################################################################

# Sidebar
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
    elif preload_or_upload == "Upload your own series":
        uploaded_files = st.file_uploader("Upload book(s) (from the same series in order of reading)", 
                                    accept_multiple_files=True, type = ['txt', 'epub'])
        # Process the loaded book files       
        load_progress = st.progress(0)
        with st.spinner(f'Loading uploaded book(s)...'):
            for i in range(len(uploaded_files)):
                uploaded_file = uploaded_files[i]
            bk_data = load_book(uploaded_file)
                bk_data["book_num"] = i+1
            all_books.append(bk_data)
                # parse_preload(series_choice, prog_bar=load_progress)
        time.sleep(0.5)
        load_progress.empty()
            

    # Current Place Inputs (sets book names and associated chapters)    
    if len(all_books) == 0:
        st.title("Pick or Upload a book/series above.")
    else:
        # Load the books (along with their associated chapters) if not done
        if preload_dict['loaded'] == False :
            load_progress = st.progress(0)
            with st.spinner(f'Loading books from {series_choice}...'):
                parse_preload(series_choice, prog_bar=load_progress)
            time.sleep(0.5)
            load_progress.empty()

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

# st.write(all_books)


# Main Page

if len(all_books) == 0:
    st.title("Pick or Upload a book/series in the sidebar to the left.")
else:
    st.title("Who/What Do You Want to Search For?")
    search_value = st.text_input("Search:", placeholder="Type a name or phrase here")

    res_window = st.container()
    if search_value != "":
        # res_window.text(f'The search term is "{search_value}"')

        context_range = 150
        search_res = []
        for book in all_books:
            # Skip searching all books after the book currently being read
            if (book['book_num'] > curr_book_dict['book_num']): break
            for ch in book['chapters']:
                # Skip searching all chapters after (and including) chapter currently being read
                curr_reading_this_book = (book['book_num'] == curr_book_dict['book_num'])
                if curr_reading_this_book & (ch['bs_sec'] >= curr_ch_dict['bs_sec']): break
                # Go through each instance of finding the esarch term
                for res in re.finditer(search_value, ch['text'],flags=re.IGNORECASE):
                    res_start = max(0,res.start()-context_range)
                    res_end = res.start()+context_range+len(search_value)
                    context = ch['text'][res_start:res_end]
                    # Check if overlap with previous result instance
                    contexts_overlap = ( (len(search_res) > 0) and 
                        (res_start - search_res[-1]["res_ind_start"] <= context_range + len(search_value)) )
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

        # Creating text with search value highlighted
        search_pattern = re.compile(search_value, re.IGNORECASE)
        highlight = f'<span style="background-color:Yellow;">{search_value}</span>'
        
        # Result title with total results found
        res_window.title(f"Results ({len(search_res)} instances found)")
        
        # Displaying the search results, grouped by book
        book_res = ""
        if len(search_res)>0:
            # Inserting results into dataframe and creating dictionary of coutns by book
            res_df = pd.DataFrame(search_res)
            res_counts = res_df.groupby(by='book').agg('count')['context'].to_dict()

            for res_item in search_res:
                # Skip if flagged due to overlapping contexts
                if res_item["overlap"]: continue
                # Display book heading if different from past
                if book_res != res_item['book']:
                    book_res = res_item['book']
                    book_res_exp = res_window.expander(f"{res_item['book']} ({res_counts[book_res]} results found)")
                    
                # Display the context with search terms highlighted
                # search_res_highlit = res_item['context'].replace(search_value, highlight)
                search_res_highlit = search_pattern.sub(highlight, res_item['context'])
                book_res_exp.markdown('"'+search_res_highlit+'"', unsafe_allow_html=True)
        
        # res_window.write(search_res)

