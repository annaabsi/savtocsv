import base64
import os
import stat
import time

import pyreadstat
import streamlit as st

import random
import shutil
import pathlib


def randomWord(length=5):
    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"

    return "".join(random.choice((consonants, vowels)[i % 2]) for i in range(length))


def get_table_download_link_csv(df, filename_download):
    # csv = df.to_csv(index=False)
    csv = df.to_csv().encode()
    # b64 = base64.b64encode(csv.encode()).decode()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename_download}.csv" target="_blank">Download csv file</a>'
    return href


def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split(".")[0]
    format = base.split(".")[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move("%s.%s" % (name, format), destination)


def run():

    shutil.rmtree("./temporal", ignore_errors=True)

    st.title(".sav TO .csv")
    st.text("Please, upload just one file")
    fileStatsObj = os.stat("main.py")
    modificationTime = time.ctime(fileStatsObj[stat.ST_MTIME])
    last_update = "Last Modified Time : " + modificationTime
    st.text(last_update)

    uploadedfile = st.file_uploader("Select your .sav file", type=["sav", "zip"])

    if uploadedfile is not None:

        file_details = {
            "FileName": uploadedfile.name,
            "FileType": uploadedfile.type,
            "FileSize": uploadedfile.size,
        }
        st.write(file_details)

        session_id = randomWord()
        tempDir = f"temporal/session_{session_id}/"
        os.makedirs(tempDir)

        if file_details["FileType"] == "application/x-spss-sav":

            # save local
            with open(tempDir + os.path.join(uploadedfile.name), "wb") as f:
                f.write(uploadedfile.getbuffer())
            st.success("File correctly updated")

            df, meta = pyreadstat.read_sav(tempDir + os.path.join(uploadedfile.name))
            st.success("Converted, creating download link")

            st.markdown(
                get_table_download_link_csv(
                    df, filename_download=uploadedfile.name[:-4]
                ),
                unsafe_allow_html=True,
            )

        if file_details["FileType"] == "application/zip":

            # save local
            with open(tempDir + os.path.join(uploadedfile.name), "wb") as f:
                f.write(uploadedfile.getbuffer())
            st.success("File correctly updated")

            shutil.unpack_archive(
                tempDir + os.path.join(uploadedfile.name), tempDir + "unzip"
            )
            os.makedirs(tempDir + "new_zip")

            filelist = []
            for root, dirs, files in os.walk(tempDir + "unzip"):
                for file in files:
                    # append the file name to the list
                    filelist.append(os.path.join(root, file))

            for file in filelist:
                if ".sav" in file:
                    st.write(file)
                    df, meta = pyreadstat.read_sav(file)
                    df.to_csv(file[:-4] + ".csv", index=False)
                    os.remove(file)

            make_archive(
                tempDir + "unzip/" + uploadedfile.name[:-4],
                tempDir + "new_zip/" + uploadedfile.name,
            )

            with open(tempDir + "new_zip/" + uploadedfile.name, "rb") as fp:
                btn = st.download_button(
                    label="Download ZIP",
                    data=fp,
                    file_name=f"{uploadedfile.name}",
                    mime="application/zip",
                )


if __name__ == "__main__":
    run()
