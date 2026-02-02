

def _show_timestamps(epstein_files):
    for doc in epstein_files.doj_files:
        doc.warn(f"timestamp: {doc.timestamp}")


def _verify_filenames(epstein_files):
    doc_filenames = set([doc.file_path.name for doc in epstein_files.all_documents()])

    for file_path in epstein_files.all_files:
        if file_path.name not in doc_filenames:
            print(f"'{file_path}' is not in list of {len(doc_filenames)} Document obj filenames!")
