import base64
import os
import stat
import time

import pyreadstat
import streamlit as st


def get_table_download_link_csv(df, filename_download):
    # csv = df.to_csv(index=False)
    csv = df.to_csv().encode()
    # b64 = base64.b64encode(csv.encode()).decode()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename_download}.csv" target="_blank">Download csv file</a>'
    return href


def run():

    st.title(".sav TO .csv")
    st.text("Please, upload just one file")
    fileStatsObj = os.stat("main.py")
    modificationTime = time.ctime(fileStatsObj[stat.ST_MTIME])
    last_update = "Last Modified Time : " + modificationTime
    st.text(last_update)

    uploadedfile = st.file_uploader("Select your .sav file", type=["sav"])
    if uploadedfile is not None:

        file_details = {
            "FileName": uploadedfile.name,
            "FileType": uploadedfile.type,
            "FileSize": uploadedfile.size,
        }
        st.write(file_details)

        # save local
        with open(os.path.join(uploadedfile.name), "wb") as f:
            f.write(uploadedfile.getbuffer())
        st.success("File correctly updated")
        st.success("Processing...")

        df, meta = pyreadstat.read_sav(os.path.join(uploadedfile.name))
        # df.to_csv(os.path.join("tempDir", uploadedfile.name[:-3]+".csv"))
        st.success("Converted, creating download link")

        st.markdown(
            get_table_download_link_csv(
                df, filename_download=uploadedfile.name[:-4]
            ),
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    run()
