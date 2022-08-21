import pandas as pd
import streamlit as st

pd.set_option('display.max_colwidth',None)

st.markdown("""#### Upload your bookmarked books here! """)
uploaded_file = st.file_uploader("")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file)

    # First phase of dataset processing
    ft = df[
        ['BranchName', 'TitleName', 'CallNumber', 'StatusDesc', 'url']]
    
    ft.columns = ["library", 'title', "number", 'avail', 'url']

    unique_bks = len(ft.title.drop_duplicates().tolist())
    unique_avail_bks = len(ft[ft.avail == 'Not on Loan'].title.drop_duplicates().tolist())

    st.markdown(f"### Summary of your NLB Favorites")
    # available_unique_bks = len(ft[ft.avail].title.drop_duplicates().tolist())
    st.markdown(f"""
        1. {unique_bks} unique books
        2. {unique_avail_bks} unique available books
    """)
    top_few = pd.DataFrame(ft[ft.avail == 'Not on Loan'].library.value_counts()).head()
    st.markdown(f""" {top_few} """)

    

    # Second phase of dataset processing
    ft.loc[ft.library == "Repository Used Book Collection", 'avail'] = "For Reference Only"
    ft = ft[ft.avail == "Not on Loan"]
    ft.avail = [i.replace("Not on Loan", "Available") for i in ft.avail]
    
    ft['title'] = [i.split(" | ")[0] for i in ft['title']]
    ft['title'] = [i.split(r"/")[0].strip() for i in ft['title']]
    ft.sort_values(['library', 'title'], inplace=True)
    final = ft[['library', 'title', 'number', 'url']]

    lib_select = st.selectbox(
        'Select specific library or All',
        tuple(final.library.drop_duplicates().tolist() + ["All", ]))

    search_text = st.text_input(label="Title Search (not case-sensitive)").lower()

    lib_col = True
    if st.checkbox("Include library column"):
        if lib_col == True:
            lib_col = False
        else:
            lib_col = True

    if lib_select != 'All':
        final = final[
            final['library'] == lib_select].drop_duplicates().sort_values('title')

    if len(search_text) > 0:
        final['title_lower'] = final['title'].str.lower()
        final = final[final.title_lower.str.contains(search_text)]
        del final['title_lower']

    def make_clickable(text, link):
        # target _blank to open new window
        # extract clickable text to display for your link
        return f'<a target="_blank" href="{link}">{text}</a>'

    # link is the column with hyperlinks
    final['title'] = [make_clickable(text, url) for text, url in zip(final['title'], final['url'])]

    del final['url']

    if lib_col:
        del final['library']

    final = final.sort_values("number").reset_index(drop=True)
    ft = final.to_html(escape=False)

    st.write("Book : {}".format(final.shape[0]))
    st.write(ft, unsafe_allow_html=True)