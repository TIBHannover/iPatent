import streamlit as st
from streamlit_cropper import st_cropper

from src.components import (
    sidebar, searchbar, gridview
)

from backend.app import Server

from shared.utils.common import load_config
from shared.utils.image import preprocess
from shared.utils.constants import BOX_COLOR, ASPECT_RATIO

@st.cache_resource
def start_server():
    return Server()


def main():

    config = load_config()

    st.set_page_config(
        page_title=config['app']['page_title'],
        page_icon="🖼️",
        layout="wide"
    )

    server = start_server()

    settings = sidebar.render()
    
    results = None
    col1, col2 = st.columns(2)

    text_query, image_query = None, None

    with col1:
        text_query, uploaded_file = searchbar.render()

    with col2:

        subcol1, subcol2 = st.columns([2,1])

        with subcol1:
            uploaded_image, cropped_img = None, None
            if uploaded_file is not None:
                uploaded_image = preprocess(uploaded_file)
                cropped_img = st_cropper(uploaded_image)

        with subcol2:
            if cropped_img:
                st.write("Query Preview")
                _ = cropped_img.thumbnail((224,224))
                st.image(cropped_img)
                image_query = preprocess(cropped_img)

    if st.button(
            label="Search", key="search_button"
        ):
            if text_query or image_query:
                with st.spinner("Searching..."):
                    results = server.search(
                        text_query=text_query, image_query=image_query,
                        text_weight=settings['retrieval']['text_weightage'],
                        limit=settings['retrieval']['top_k']
                    )
            else:
                st.warning("Please enter a search query or upload an image")

    if results:

        tabs = st.tabs(['Ranked Grid View', 'Cluster View'])

        with tabs[0]:
            gridview.render(
                results,
                top_k=settings['retrieval']['top_k'],
                per_row=settings['retrieval']['per_row'])

        with tabs[1]:

            with st.spinner("Clustering..."):

                clustered_results = server.cluster(
                    results=results,
                    model_name=settings['clustering']['cluster_model'],
                    n_clusters=settings['clustering']['n_clusters'],
                    top_k=settings['clustering']['top_k']
                )

            with st.spinner("Generating cluster titles and descriptions. This may take a while..."):

                if settings['clustering']['with_description']:

                    cluster_contents = server.generate_titles_and_desrciptions(
                        clustered_results=clustered_results
                    )

                    for cluster_id, content in cluster_contents.items():
                        if cluster_id in clustered_results:
                            clustered_results[cluster_id]['title'] = content['title']
                            clustered_results[cluster_id]['description'] = content['description']

            gridview.render_cluster(
                clustered_results=clustered_results,
                w_desc=settings['clustering']['with_description']
            )

if __name__ == "__main__":
    main()