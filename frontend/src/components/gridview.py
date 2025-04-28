import streamlit as st

import io
import base64

from PIL import Image

from shared.utils.constants import ESPACENET_URL

def encode_image(image):

    image = Image.open(image)
    image = image.resize((224, 224))
    
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'<img src="data:image/png;base64,{img_str}" width="224" height="224"/>'

def patent_link(patent, title):
    return f'<a href="{ESPACENET_URL}+{patent}" target="_blank" style="color: rgb(46, 154, 255); text-decoration: underline;" title="{title.title()}">{patent}</a>'

def render_keywords_pills(keywords):
    if not keywords:
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

    html = "".join([f'<span class="pill">{keyword}</span>' for keyword in keywords])
    html += "<br/>"
    st.markdown(html, unsafe_allow_html=True)

def display_similarity_score(score):
    score_percent = int(score * 100)
    progress_html = f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
            <div style="flex-grow: 1; background-color: #e0e0e0; border-radius: 5px; height: 10px; position: relative;">
                <div style="width: {score_percent}%; background-color: #4CAF50; height: 100%; border-radius: 5px;"></div>
            </div>
            <div style="min-width: 40px; text-align: right; font-size: 0.85rem; color: gray;">
                {score_percent}%
            </div>
        </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def display_row(results, grid_size):

    grid_cols = st.columns(grid_size)

    for col, result in enumerate(results):
        with grid_cols[col]:
            
            image = Image.open(result['image'])
            st.image(image=image, use_container_width=True)
            display_similarity_score(result['score'])

            html = f"""
            <div style="flex: 0 0 auto; text-align: center;">
                <span style="text-align: center;">{patent_link(result['patent'], result['metadata']['title.txt'])}</span>
            </div>"""

            st.markdown(html, unsafe_allow_html=True)

            st.markdown('---')

def display_cluster_row(results):

    html = """
    <div style="display: flex; overflow-x: auto; gap: 16px; padding-bottom: 8px;">
    """

    for result in results:
        img_html = encode_image(image=result['image'])

        html += f"""
        <div style="flex: 0 0 auto; text-align: center;">
            {img_html}<br>
            <span style="text-align: center;">{patent_link(result['patent'], result['metadata']['title.txt'])}</span>
        </div>
        """

    html += "</div>"

    st.html(html)

def render(results, top_k=None, per_row=6):
    
    grid_size = per_row

    top_k_results = results[:top_k] if top_k else results

    batched_results = [
        top_k_results[i:i+grid_size] for i in range(0, len(top_k_results), grid_size)
    ]

    for batch in batched_results:
        display_row(batch, grid_size)

def render_cluster(clustered_results, w_desc=False):

    if w_desc:
        st.markdown("""
            <div style='font-size: 0.9rem; color: gray; padding: 0.5em 0;'>
            ⚠️ <strong>Disclaimer:</strong> The titles and descriptions below are generated using a Large Vision-language Model (LVLM). They may not be fully accurate or reliable. We assume no liability for their use.
            </div>
        """, unsafe_allow_html=True)

    for id, (_, cluster_data) in enumerate(clustered_results.items(), start=1):

        title = cluster_data.get("title", "")
        st.markdown(
            f"### Cluster - {title if 'title' in cluster_data else id}"
        )

        if 'description' in cluster_data:
            st.write(cluster_data.get("description", ""))

        terms = cluster_data.get("terms", [])

        if terms:
            render_keywords_pills(terms)
        else:
            st.markdown("_No keywords found._")

        display_cluster_row(cluster_data['results'])

        st.markdown("---")