import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from PIL import Image


file_prefix = "./"


@st.cache_data(persist=True)
def getImageAsBase64(file):
  with open(file, "rb") as f:
    data = f.read()
  return base64.b64encode(data).decode()


@st.cache_data(persist=True)
def load_data():
    data = pd.read_csv(file_prefix + 'Assignment - Preprocessed Dataset.csv')
    data['Date']=pd.to_datetime(data['Date'],errors='coerce')
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
    data['Key Phrases'] = data['Key Phrases'].astype(str)
    return data


def date_range():
    st.markdown("#### Select the date range:-")
    start = st.date_input("Start Date:- (Please select on or after 2024-04-01)",pd.to_datetime("2024-04-01",format="%Y-%m-%d"))
    end = st.date_input("End Date:- (Please select on or before 2024-05-06)",pd.to_datetime("2024-05-06",format="%Y-%m-%d"))
    return start,end;


def plot_word_cloud(df, title, col):
    msg = df['Key Phrases'].tolist()
    msg = ' '.join(msg)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    text = WordCloud(width = 750, height = 600, colormap = 'Reds', margin = 0,
                    max_words = 500, min_word_length = 4, background_color = "black").generate(msg)

    fig = plt.figure()
    plt.title(title, fontsize=15)
    plt.axis('off')
    plt.imshow(text,interpolation='bilinear')
    col.pyplot()


def create_word_count_df(substract_df):
  msg = substract_df['Key Phrases'].tolist()
  all_msgs = []
  for MSG in msg:
    temp = MSG.split(' ')
    all_msgs += temp

  msg = ','.join(all_msgs)
  counts = dict()
  words = msg.split(',')
  for word in words:
    if word in counts:
      counts[word] += 1
    else:
      counts[word] = 1

  words = list(counts.items())
  dff = pd.DataFrame(words, columns=["word", "count"])
  dff.sort_values(by = ['count'], ascending=False, inplace = True)
  return dff[0:20]


def plot_bar_graph(substract_df, title, col):

  dff = create_word_count_df(substract_df)

  x, y = dff['word'].tolist(), dff['count'].tolist()
  plt.rcParams['font.size'] = 12
  fig = plt.figure()
  plt.title(title, fontsize=16)
  plt.bar(x, y)
  plt.xticks(rotation=45, ha='right')

  for i in range(len(x)):
    plt.text(i, y[i], y[i], ha = 'center')

  col.pyplot()


def plot_pie_chart(df, sub_title, col):
  sentiment = df['Sentiment'].value_counts().index
  count = df['Sentiment'].value_counts().tolist()

  fig = plt.figure()
  plt.rcParams['font.size'] = 12

  plt.pie(count, labels=sentiment, autopct='%1.2f%%')
  plt.title(f"Pie chart for sentiments\n{sub_title}", fontsize=13)
  col.pyplot()

  plt.bar(sentiment, count)
  plt.title(f'Bar chart for sentiments\n{sub_title}', fontsize=17)
  plt.xlabel('Sentiments', fontsize=16)
  plt.ylabel('Count', fontsize=16)
  for i in range(len(sentiment)):
    plt.text(i, count[i], count[i], ha = 'center', fontsize=15)
  col.pyplot()


def callback1():
    st.session_state.button1 = True
def callback2():
    st.session_state.button2 = True


st.set_page_config(page_title="AdFactors PR Assignment",page_icon="📝",layout="wide",initial_sidebar_state="expanded")
st.write("""<h1 style='text-align: center; font-size: 13mm; color: #FF0000;'>AdFactors PR Assignment</h1>
<p style='text-align: center; font-size: 4mm'><b>Created by :- M.H.M. HISHAM <font size="2">( BSc. (Hons) in Data Science )</font></br>
<font size="3">Faculty of Science</br>University of Peradeniya</font></b></p>
<h6 style='text-align: center;'></h6>""", unsafe_allow_html=True)

with open(file_prefix + "style.css") as f:
  st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

img = getImageAsBase64(file_prefix + "img.jpeg")
st.markdown(f"""
  <style>
    [data-testid="stAppViewContainer"]{{
      background-image: url("data: image/png;base64,{img}");
      background-size: cover;
    }}
  </style>""",unsafe_allow_html=True)
  
data = load_data()
if 'button1' not in st.session_state:
  st.session_state.button1 = False
if 'button2' not in st.session_state:
  st.session_state.button2 = False

st.header("Filter by:-")
filter_by = st.selectbox("",["","Date", "Source"])

if filter_by == 'Date':
  start,end = date_range()
  extract = st.button('Extract data', on_click=callback1)
  if extract or st.session_state.button1:
    df = data.loc[data["Date"].between(str(start), str(end))]
    st.markdown("#### Filterd Data Frame")
    st.dataframe(df)

    col1, col2, col3 = st.columns(3)
    word_cloud = col1.checkbox("Draw a wordcloud for key phrases")
    bar_chart = col2.checkbox("Most frequently used 20 words in bar chart")
    pie_chart = col3. checkbox("Sentiment pie chart")

    if word_cloud:
      plot_word_cloud(df, f"Word Cloud \n({start}) - ({end})\nKey Phrases", col1)
    if bar_chart:
      plot_bar_graph(df, f"Most frequently used 20 Key Phrases\n({start}) - ({end})", col2)
    if pie_chart:
      plot_pie_chart(df, f"({start}) - ({end})", col3)
  

elif filter_by == 'Source':
  sources = data['Source'].value_counts().index
  source = []

  for temp_source in sources:
    temp_words = data.loc[data['Source']==temp_source]['Key Phrases'].value_counts().tolist()
    words_length = len(temp_words)
    if words_length != 0:
      source.append(temp_source)

  st.markdown("### Select the source:-")
  selected_source = st.selectbox("", [""]+source)
  extract = st.button('Extract data', on_click=callback2)

  if extract or st.session_state.button2:
    if selected_source != "":
      df = data.loc[data['Source']==selected_source]
      st.markdown("#### Filterd Data Frame")
      st.dataframe(df)

      col1, col2, col3 = st.columns(3)
      word_cloud = col1.checkbox("Draw a wordcloud for key phrases")
      bar_chart = col2.checkbox("Most frequently used 20 words in bar chart")
      pie_chart = col3. checkbox("Sentiment pie chart")

      if word_cloud:
        plot_word_cloud(df, f"Word Cloud\nSource:- {selected_source}\nKey Phrases", col1)
      if bar_chart:
        plot_bar_graph(df, f"Most frequently used 20 Key Phrases\nSource:- {selected_source}", col2)
      if pie_chart:
        plot_pie_chart(df, f"Source:- {selected_source}", col3)
      





















