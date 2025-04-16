import streamlit as st
import pandas as pd
import plotly.express as px

from streamlit_plotly_events import plotly_events

def render(points):

    df = pd.DataFrame(points)

    selected_clusters = st.multiselect(
        "Select clusters to display:",
        options=df['cluster'].unique(),
        default=list(df['cluster'].unique())
    )

    filtered_df = df[df['cluster'].isin(selected_clusters)]

    fig = px.scatter_3d(
        filtered_df,
        x='x',
        y='y',
        z='z',
        color='cluster',
        hover_data=['patent'],  # Show image ID on hover
        custom_data=['image'],
        title="3D Cluster Plot",
        labels={"cluster": "Cluster"},
    )

    selected_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        override_height=700,
        override_width="100%",
    )

    if selected_points:
        selected = selected_points[0]
        selected_image = selected['customdata'][0]

        st.image(selected_image, use_container_width=True)
    else:
        st.info("Click on a point in the 3D plot to preview its image.")


    st.plotly_chart(fig)