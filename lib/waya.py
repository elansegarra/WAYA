import streamlit as st
import pandas as pd
import numpy as np
import ebooklib
from ebooklib import epub
import preloaded
import re

# To run from command line: "streamlit waya.py --server 8888"

st.set_page_config(page_title="WAYA: Who Are You Again?", page_icon=None, 
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
        all_text = file_loader_obj.read().decode('UTF-8')
        chapters = [{'name':"Ch 1 Who dun it?", 'text':'...'},
                    {'name':"Ch 2 But why?!", 'text':"...."} ]
        res = all_text[0:500]
    elif file_type == "epub":
        book = epub.read_epub(file_loader_obj)
        chapters = [{'name':"Ch 1 The Story so far", 'text':'...'},
                    {'name':"Ch 2 Something unexpected happens", 'text':"...."},
                    {'name':"Ch 3 B/C", 'text':"...."} ]
        res = book.get_metadata('DC', 'title')
    else:
        st.error(f"File {file_loader_obj.name} is not a recognized file type.")
        res = "ERROR DIDNT UNDERSTAND FILE TYPE"

    return {"filename": file_loader_obj.name,
            "title": file_loader_obj.name,
            "file_type": file_type,
            "chapters": chapters}

def load_epub_book(file_loader_obj):
    return "What?!"

# Grab the preloaded series information
preloaded_dicts = preloaded.preloaded_dicts

###########################################################################
#### App Running ##########################################################
###########################################################################

# Sidebar
with st.sidebar:
    st.title("Which Series or Book?")
    preload_or_upload = st.radio("How to pick your series?", 
                ["Open a preloaded series", "Upload your own series"])
    if preload_or_upload == "Open a preloaded series":
        preload_names = list(preloaded_dicts.keys())
        preload_choice = st.selectbox("Pick a preloaded series:", preload_names)
        # Grab the dictionary associated with the chosen series
        preload_dict = preloaded_dicts[preload_choice]
        all_books = preload_dict['books']
    elif preload_or_upload == "Upload your own series":
        uploaded_files = st.file_uploader("Upload a book or books (in order of reading)", 
                                    accept_multiple_files=True, type = ['txt', 'epub'])
        # Process the loaded book files
        book_names = []
        all_books = []
        for uploaded_file in uploaded_files:
            bk_data = load_book(uploaded_file)
            all_books.append(bk_data)

    # Current Place Inputs (sets book names and associated chapters)    
    if len(all_books) == 0:
        st.title("Pick or Upload a book/series above.")
    else:
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
                    search_res.append({"book":book["title"], "chapter":ch['name'], "context":context})

        # Creating text with search value highlighted
        highlight = f'<span style="background-color:Yellow;">{search_value}</span>'
        
        # Result title with total results found
        res_window.title(f"Results ({len(search_res)} instances found)")
        
        # Displaying the search results, grouped by book
        book_res = ""
        if len(search_res)>0:
            # Inserting results into dataframe and creating dictionary of coutns by book
            res_df = pd.DataFrame(search_res)
            res_counts = res_df.groupby(by='book').agg('count')['context'].to_dict()

            for res in search_res:
                # Display book heading if different from past
                if book_res != res['book']:
                    book_res = res['book']
                    book_res_exp = res_window.expander(f"{res['book']} ({res_counts[book_res]} results found)")
                    
                # Display the context with search terms highlighted
                search_res_highlit = res['context'].replace(search_value, highlight)
                book_res_exp.markdown('"'+search_res_highlit+'"', unsafe_allow_html=True)
        
        # res_window.write(search_res)

