import streamlit as st
import make_names
import pandas as pd
import time

from faker import Factory
import random

faker = Factory.create()
# probability of typo
prob = 0.2

def make_list_app(num_names, max_num_repeats, num_changes, num_lines):
    with open('wordlist.txt', 'w') as f:
        for i in range(num_names):
            # pick out random lines to perturb (make typo)
            name = faker.company()
            num_repeats = random.randint(1,max_num_repeats) 
            num_lines += num_repeats
            for _ in range(num_repeats):
                if random.random() < prob:
                    new_name = make_names.perturb(name)
                    num_changes +=1
                else:
                    new_name = name
                f.write(new_name + '\n')
    st.write("Num changes: %d\nNum lines: %d"%(num_changes, num_lines))

def split_sentence(sentence: str) -> list:
    words = sentence.split("\n")
    return words



options01 = ['I have a list of names', 'I need to make a list of names']

selection01 = st.selectbox("Tell us what dataset you'd like to use", options01)

if options01.index(selection01) == 1: # make a list of names
    num_names = st.text_input("How many unique names would you like in your list?", 50) # default argument 50
    num_names = int(num_names)  # convert to int
    max_num_repeats = st.text_input("Input the max number of times a you'd like a unique name to repeat.", 15) # default argument 50
    max_num_repeats = int(max_num_repeats) # convert to int
    
    num_changes = 0
    num_lines = 0
    
    if st.button("Make list!", key = 0):
        st.write("Making typo list from %d unique names with up to %d repetitions..."%(num_names, max_num_repeats))
        # time.sleep(2)
        make_list_app(num_names, max_num_repeats, num_changes, num_lines)
        
        with open("wordlist.txt", "r") as file:
            string = file.read()
            

        
        ls = split_sentence(string)
        width_fix = []
        for i in range(len(ls)):
            width_fix.append('\t\t\t\t\t\t\t\t\t')
        df = pd.DataFrame(zip(ls,width_fix), columns = ['company_names', '\t\t\t\t\t\t\t\t\t'])
        st.dataframe(df)
        
        
        
                    
        
            
  