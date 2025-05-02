import streamlit as st

def render():

    with st.sidebar:

        st.markdown(
            """
            <h1 style='text-align: left; font-size: 2.25em; font-family: "Segoe UI", Arial, sans-serif; margin-bottom: 0.1em;'>
                iPatent
            </h1>
            <div style='text-align: left; color: #555; font-family: "Segoe UI", Arial, sans-serif; margin-top: 0; margin-bottom: 1.2em;'>
                Interactive Patent Search and Analysis
            </div>
            """, unsafe_allow_html=True
        )

        st.title('Settings')

        with st.expander(label='Retrieval', expanded=True):
            
            top_k = st.number_input(
                label='Select top k', key='top_k',
                min_value=10, max_value=500, step=10, value=100,
                help='Select number of results to display'
            )

            per_row = st.number_input(
                label='Select no. of results per row', key='per_row',
                min_value=1, max_value=10, step=1, value=6,
                help='Select number of results to display per row'
            )

            text_weightage = st.slider(
                label='Text Weight', key='text_weightage',
                min_value=0.0, max_value=1.0, step=0.1, value=0.5,
                help='Select weightage of text'
            )

        with st.expander(label='Clustering', expanded=True):
            
            cluster_model = st.selectbox(
                label='Model', key='clustering_model',
                options=['KMeans'],
                help='Select a clustering model'
            )

            n_clusters = st.number_input(
                label='Number of Clusters', key='n_clusters',
                min_value=2, max_value=10, step=1, value=5,
                help='Select the number of cluster groups'
            )

            cluster_top_k = st.number_input(
                label='Top k', key='cluster_top_k',
                min_value=10, max_value=500, step=10, value=100,
                help='Select number of results to cluster'
            )

            with_description = st.checkbox(
                label='Generate cluster descriptions', key='w_desc',
                help='Select to generate descriptions for each cluster using LLaVA-1.6-Vicuma LVLM'
            )

        st.markdown(
        """
        <a href="https://github.com/TIBHannover/iPatent/tree/workshop-submission" target="_blank">
            <img src="https://img.shields.io/badge/View%20on%20GitHub-grey?logo=github"
                alt="View on GitHub"
                style="border:0;height:30px;margin-top:20px;"/>
        </a>
        """, unsafe_allow_html=True)

    return {
        'retrieval': {
            'top_k': top_k,
            'per_row': per_row,
            'text_weightage': text_weightage
        },
        'clustering': {
            'cluster_model': cluster_model,
            'top_k': cluster_top_k,
            'n_clusters': n_clusters,
            'with_description': with_description
        }
    }
        
