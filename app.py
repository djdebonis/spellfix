import streamlit as st
import make_names

options01 = ['I have a list of names', 'I need to make a list of names']

selection01 = st.selectbox("Tell us what dataset you'd like to use", options01)

if options01.index(selection01) == 1: # make a list of names
    number_unique = st.text_input("How many unique names would you like in your list?", default = 50)
    repeats = st.text_input("Input the max number of times a you'd like a unique name to repeat.")
    