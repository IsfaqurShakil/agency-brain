import streamlit as st

from answer import answer
from check import check_caption
from search import brands

st.set_page_config(page_title="Agency Brain", page_icon="🧠")
st.title("🧠 Agency Brain")
st.caption("Ask about a brand's rules and past campaigns, or check a caption against its brand rules.")

brand = st.selectbox("Brand", brands())

tab_ask, tab_check = st.tabs(["Ask", "Check"])

with tab_ask:
    question = st.text_input("Your question")
    if st.button("Get answer"):
        if question.strip():
            with st.spinner("Searching documents..."):
                try:
                    st.write(answer(question, brand))
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
        else:
            st.warning("Please type a question first.")

with tab_check:
    caption = st.text_area("Paste your caption")
    if st.button("Check caption"):
        if caption.strip():
            with st.spinner("Checking brand rules..."):
                try:
                    st.write(check_caption(caption, brand))
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
        else:
            st.warning("Please paste a caption first.")