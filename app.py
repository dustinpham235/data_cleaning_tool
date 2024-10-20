import streamlit as st
import json
import pandas as pd
import base64
from streamlit_javascript import st_javascript


def load_json(file):
    content = file.getvalue().decode("utf-8")
    return json.loads(content)


def save_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def trim_phone(phone):
    return phone.strip() if isinstance(phone, str) else phone

st.set_page_config(page_title="JSON Editor", layout="wide")
st.title("JSON Editor")

# File upload
uploaded_file = st.file_uploader("Choose a JSON file", type="json")

if uploaded_file is not None:
    # Store the original filename in session state
    if 'original_filename' not in st.session_state:
        st.session_state.original_filename = uploaded_file.name.rsplit('.', 1)[0]

    # Load JSON data
    data = load_json(uploaded_file)

    # Convert JSON to DataFrame
    if "df" not in st.session_state:
        st.session_state.df = pd.json_normalize(data)

    # Remove status columns and add a delete column
    display_columns = [
        # "delete",
        "name",
        "address",
        "post_url",
        "average_price_per_person",
        "open_time",
        "description",
        "phone",
    ]
    edit_df = st.session_state.df[display_columns].copy()
    # edit_df["delete"] = False

    # Select and reorder columns
    edit_df = st.session_state.df[display_columns]

    # Edit DataFrame
    edited_df = st.data_editor(
        edit_df,
        hide_index=True,
        column_config={
            "delete": st.column_config.CheckboxColumn("Delete"),
            "post_url": st.column_config.LinkColumn("Post URL"),
        },
        use_container_width=True,
        key="data_editor",
        num_rows="dynamic",
    )

    # Store edited_df in session state
    st.session_state.edited_df = edited_df

    # Prepare for Download button with on_change callback
    def update_dataframe():
        for index, row in st.session_state.edited_df.iterrows():
            st.session_state.df.loc[index, display_columns] = row
        st.session_state.changes_prepared = True

    st.button("Save changes", on_click=update_dataframe, key="prepare_download")

    # Show success message if changes are prepared
    if st.session_state.get('changes_prepared', False):
        st.success("Changes saved. You can now download the updated JSON.")

    # Convert DataFrame back to JSON
    output = st.session_state.df.to_dict(orient="records")

    # Replace NaN with None (which will be converted to null in JSON)
    def replace_nan_with_none(obj):
        if isinstance(obj, dict):
            return {k: replace_nan_with_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_nan_with_none(v) for v in obj]
        elif pd.isna(obj):
            return None
        else:
            return obj

    output = replace_nan_with_none(output)

    # Prepare JSON data for download
    json_data = save_json(output)

    # Download section
    st.divider()
    original_filename = st.session_state.get('original_filename', 'data')
    filename = st.text_input(
        "Enter filename for download (without .json)",
        value=f"{original_filename}_clean"
    )
    st.download_button(
        label="Download JSON",
        data=json_data,
        file_name=f"{filename}.json",
        mime="application/json",
        disabled=not st.session_state.get('changes_prepared', False)
    )
    st.info("Check Download của browser nhé, k có thông báo đâu")
