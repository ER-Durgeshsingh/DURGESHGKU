import streamlit as st
from supabase import create_client


SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://ultqgjwinmwowkcwxmpo.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_koh7aLEpmgwXKSL_MclJyA_oR2quZrA")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
