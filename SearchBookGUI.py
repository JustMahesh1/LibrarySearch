import pandas as pd
import streamlit as st
import re

# Constants
MAX_RESULTS = 10  # Number of results per page

@st.cache_data
def load_data(file_path):
    """Load the data from the Excel file and cache it to improve performance."""
    try:
        data = pd.read_excel(file_path)
        return data
    except FileNotFoundError:
        st.error("The specified file was not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return pd.DataFrame()

def normalize_text(text):
    """Normalize text by removing punctuation, converting to lowercase, and removing extra spaces."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text.strip()

def search_books(keyword, books_df):
    """Search for books based on the provided keyword."""
    if keyword:
        try:
            keyword = normalize_text(keyword)  # Normalize the search keyword
            results = books_df[
                books_df.apply(lambda row: row.astype(str).apply(normalize_text).str.contains(keyword).any(), axis=1)
            ]
            return results
        except Exception as e:
            st.error(f"An error occurred during the search: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Load Excel data
books_df = load_data('books.xlsx')

# Theme selection
theme = st.radio("Switch Theme", ["Light", "Dark"], index=1)

# Set CSS based on the selected theme
if theme == "Light":
    css = """
    <style>
    body {
        background-color: #f5f5f5;
        color: #ffa500;
        font-family: Arial, sans-serif;
    }
    .stApp {
        background-color: #ffffff;
        color: #ffa500;
    }
    .card {
        background: linear-gradient(145deg, #ffffff, #e0e0e0);
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        padding: 20px;
        margin: 15px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #333;
        overflow: hidden;
        position: relative;
    }
    .card:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
    }
    .card-content {
        padding: 10px 0;
    }
    .card h3 {
        color: #333;
        margin: 0;
    }
    .card p {
        color: #555;
        margin: 5px 0;
    }
    .highlight {
        font-weight: bold;
        color: #ff5722;
    }
    </style>
    """
else:
    css = """
    <style>
    body {
        background-color: coral;
        color: white;
        font-family: Arial, sans-serif;
    }
    .stApp {
        background-color: #121212;
        color: blue;
    }
    @keyframes colorShift {
        0% {
            background: linear-gradient(145deg, #ff6f61, #ffcc70);
        }
        50% {
            background: linear-gradient(145deg, #ff5722, #ff9800);
        }
        100% {
            background: linear-gradient(145deg, #ff6f61, #ffcc70);
        }
    }
    .card {
        background: linear-gradient(145deg, #ff6f61, #ffcc70);
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        padding: 20px;
        margin: 15px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #333;
        overflow: hidden;
        position: relative;
        animation: colorShift 4s infinite;
    }
    .card:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
        background: linear-gradient(145deg, #ff5722, #ff9800);
        animation: none;
    }
    .card-content {
        padding: 10px 0;
    }
    .card h3 {
        color: #fff;
        margin: 0;
    }
    .card p {
        color: #f1f1f1;
        margin: 5px 0;
    }
    .highlight {
        font-weight: bold;
        color: #800080;
    }

    .highlight_labels {
        font-weight: bold;
        color: #00FFFF;
    }
    </style>
    """

st.markdown(css, unsafe_allow_html=True)

st.title("Welcome to SIWS Library Search")

# Initialize session state for the keyword, results, and current page if not already done
if 'keyword' not in st.session_state:
    st.session_state.keyword = ''
if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame()
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Text input for the search keyword
keyword = st.text_input("Try Titles Author names etc..")

if st.button("Search "):
    if books_df.empty:
        st.write("The book data could not be loaded.")
    else:
        # Perform the search and store results in session state
        st.session_state.keyword = keyword
        st.session_state.results = search_books(keyword.lower(), books_df)
        st.session_state.current_page = 1  # Reset to the first page

# Retrieve results from session state
results = st.session_state.results

if not results.empty:
    total_results = len(results)
    num_pages = (total_results // MAX_RESULTS) + (total_results % MAX_RESULTS > 0)

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.current_page > 1:
            if st.button("Previous"):
                st.session_state.current_page -= 1
                st.rerun()  # Ensure the page is updated immediately

    with col3:
        if st.session_state.current_page < num_pages:
            if st.button("Next"):
                st.session_state.current_page += 1
                st.rerun()  # Ensure the page is updated immediately

    # Display results for the current page
    start_idx = (st.session_state.current_page - 1) * MAX_RESULTS
    end_idx = start_idx + MAX_RESULTS
    current_results = results.iloc[start_idx:end_idx]

    for index, row in current_results.iterrows():
        # Create a card layout for each result
        card_html = f"""
        <div class="card">
            <div class="card-content">
                <h4>Accession No. : <span class="highlight">{row['Accession No.']}</span></h4>
		<h5><strong>Call No. :</strong> <span class="highlight">{row['Call No.']}</span></h5>
                <p><strong><span class="highlight_labels">Title :</strong></span> {row['Title']}</p>
                <p><strong><span class="highlight_labels">Author :</strong></span> {row['Author']}</p>
                <p><strong><span class="highlight_labels">Publisher :</strong></span> {row['Publisher']}</p>
                <p><strong><span class="highlight_labels">Year :</strong></span> {row['Year']}</p>
            </div>
	</div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    st.write(f"Total results: {total_results}")
    st.write(f"Number of pages: {num_pages}")
    st.write(f"Current page: {st.session_state.current_page}")

    st.write(f"Displaying {start_idx + 1} - {min(end_idx, total_results)} of {total_results} results")
else:
    if 'keyword' in st.session_state and st.session_state.keyword:
        st.write("No books found matching the keyword.")


st.markdown("Some features are optimized for desktop. Consider switching for a more complete view.")
# Add copyright notice at the end
st.markdown("<footer style='text-align: center; padding: 10px;'><p>&copy; 2024 SIWS Library Dept. All rights reserved.</p></footer>", unsafe_allow_html=True)

