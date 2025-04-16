import streamlit as st

def render():

    with st.sidebar:

        st.title('Settings')

        with st.expander(label='Retrieval', expanded=True):
            
            top_k = st.number_input(
                label='Top k', key='top_k',
                min_value=10, max_value=500, step=10, value=100,
                help='Select number of results to display'
            )

            text_weightage = st.slider(
                label='Text Weight', key='text_weightage',
                min_value=0.0, max_value=1.0, step=0.1, value=0.5,
                help='Select weightage of text'
            )

        with st.expander(label='Filters', expanded=True):
            
            figure_types = st.multiselect(
                label='Figure Type', key='figure_type',
                help='Select figure types to retrieve',
                options=[
                    'Flowchart','Drawing','Diagram','Photo','Math','Chemistry','Code'
                ]
            )

            cpc_sections = st.multiselect(
                label='CPC Section', key='cpc_sections',
                help='Select CPC sections',
                options=['A','B','C','D','E','F','G','H','Y']
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

    return {
        'retrieval': {
            'top_k': top_k,
            'text_weightage': text_weightage
        },
        'filters': {
            'cpc_sections': cpc_sections,
            'figure_types': figure_types
        },
        'clustering': {
            'cluster_model': cluster_model,
            'top_k': cluster_top_k,
            'n_clusters': n_clusters,
            'with_description': with_description
        }
    }
        
