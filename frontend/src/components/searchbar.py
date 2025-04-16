from typing import Optional, Tuple

import streamlit as st
from PIL import Image

def render() -> Tuple[str, Optional[Image.Image]]:
    """
    Create a search bar with text and image input.
    
    Returns:
        Tuple containing search query string and optional uploaded image
    """
    
    query = st.text_input(
            "Search images...",
            key="search_query",
            placeholder="Enter text to search..."
        )
    
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=['png', 'jpg', 'jpeg'],
        key="image_upload"
    )
    
    return query, uploaded_file