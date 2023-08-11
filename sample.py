import streamlit as st
from st_oauth import st_oauth


st.markdown("## This (and above) is always seen")
id = st_oauth("oauth", 'Click to login via OAuth')
st.markdown("## This (and below) is only seen after authentication")