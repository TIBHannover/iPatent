import streamlit as st

import io
import base64

from PIL import Image

from shared.utils.constants import ESPACENET_URL

def encode_image(image):

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'<img src="data:image/png;base64,{img_str}" width="224" height="224"/>'

def render_label_pills(labels):
    if not labels:
        return

    st.markdown(
        """
        <style>
        .pill {
            display: inline-block;
            background-color: #e0f0ff;
            color: #007acc;
            border-radius: 25px;
            padding: 4px 12px;
            margin: 4px 4px 4px 0;
            font-size: 0.85rem;
            font-weight: 500;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    html = "".join([f'<span class="pill">{label}</span>' for label in labels])
    st.markdown(html, unsafe_allow_html=True)

def display_row(results, grid_size):

    grid_cols = st.columns(grid_size)

    for col, result in enumerate(results):
        with grid_cols[col]:
            
            image = Image.open(result['image'])
            _thumbnail = image.resize((224, 224))
            st.image(image=_thumbnail, width=224)
            
            patent_link = f'<a href="{ESPACENET_URL}+{result["patent"]}" target="_blank" style="color: rgb(46, 154, 255); text-decoration: underline;">{result["patent"]}</a>'

            html = f"""
            <div style="flex: 0 0 auto; text-align: center;">
                <span style="text-align: center;">{result["rank"]}: {patent_link}</span>
            </div>"""

            st.html(html)

def display_cluster_row(results):

    html = """
    <div style="display: flex; overflow-x: auto; gap: 16px; padding-bottom: 8px;">
    """

    for result in results:
        image = Image.open(result['image'])
        _thumbnail = image.resize((224, 224))
        img_html = encode_image(image=_thumbnail)

        patent_link = f'<a href="{ESPACENET_URL}+{result["patent"]}" target="_blank" style="color: rgb(46, 154, 255); text-decoration: underline;">{result["patent"]}</a>'

        html += f"""
        <div style="flex: 0 0 auto; text-align: center;">
            {img_html}<br>
            <span style="text-align: center;">{patent_link}</span>
        </div>
        """

    html += "</div>"

    st.html(html)

def render(results, top_k=None):
    
    grid_size = 10

    top_k_results = results[:top_k] if top_k else results

    batched_results = [
        top_k_results[i:i+grid_size] for i in range(0, len(top_k_results), grid_size)
    ]

    for batch in batched_results:
        display_row(batch, grid_size)

def render_cluster(clustered_results):

    for cluster_id, cluster_data in clustered_results.items():

        st.markdown(f"### 🔹 Cluster {cluster_id+1}")

        if 'description' in cluster_data:
            st.write(cluster_data.get("description", ""))

        unique_labels = cluster_data.get("labels", [])
        unique_labels = unique_labels[:min(10, len(unique_labels))]

        if unique_labels:
            render_label_pills(unique_labels)
        else:
            st.markdown("_No labels found._")

        display_cluster_row(cluster_data['results'])

        st.markdown("---")