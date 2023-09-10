# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 02:39:19 2023

@author: edmun
"""

from __future__ import absolute_import, division, print_function
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
#from pymongo import MongoClient
import numpy as np
import tkinter as tk
from tkinter import filedialog
import datetime as dt
from datetime import date
from datetime import datetime

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout


import datetime
from pdfkivygui.dfguik import DfguiWidget
import pdfkivygui
#from pdfkivygui.pdfkivygui import Graph, BarGraph




fields = ['Device', 'Serial', 'Timestamp', 'Record Type', 'Historic Glucose', 'Scan Glucose', 'Non-numeric rapid insulin', 'Rapid insulin (units)',
          'Non-numeric food', 'Carbohydrate (grams)', 'Carbohydrate (servings)', 'Non-numeric long acting insulin', 'Long acting insulin (units)',
          'Notes', 'Strip glucose mmol/L', 'Ketone mmol/L', 'Meal insulin', 'Correction', 'User change insulin (units)']

dir(pdfkivygui)


def open_file():
    
    filetypes = (
        ('CSV files', '*.CSV'),
        ('All files', '*.*'),
    )
    
    # open-file dialog
    root = tk.Tk()
    filename = tk.filedialog.askopenfilename(
        title='Select a file...',
        filetypes = filetypes,
    )
    root.destroy()
    print(filename)
    return(filename)

def save_file():
    # save-as dialog
    
    filetypes = (
        ('CSV files', '*.CSV')
        ('Text files', '*.TXT'),
        ('All files', '*.*'),
    )
    
    root = tk.Tk()
    filename = tk.filedialog.asksaveasfilename(
        title='Save as...',
        filetypes = filetypes,
        defaultextension='.csv'
    )
    root.destroy()
    return(filename)
# filename == 'path/to/myfilename.txt' if you type 'myfilename'
# filename == 'path/to/myfilename.abc' if you type 'myfilename.abc'

def upload_data():
    global records_df
    file_path = open_file()
        
    records_whole_df = pd.read_csv(file_path, header = None, names = fields, skiprows = 2, usecols = ['Timestamp', 'Record Type', 'Historic Glucose',
                                                                                                      'Scan Glucose', 'Rapid insulin (units)', 
                                                                                                      'Long acting insulin (units)', 'Carbohydrate (grams)',
                                                                                                      'Notes'], dtype ={'Notes':'string'})
    
    #Removes the other records for this type
    records_glucose_df = records_whole_df.drop(columns = ['Scan Glucose', 'Rapid insulin (units)', 'Long acting insulin (units)', 'Carbohydrate (grams)', 'Notes'])
    records_glucose_df = records_glucose_df[records_glucose_df['Record Type'] == 0]
    
    records_glucose_scan_df = records_whole_df.drop(columns = ['Historic Glucose', 'Rapid insulin (units)', 'Long acting insulin (units)', 'Carbohydrate (grams)', 'Notes'])
    records_glucose_scan_df = records_glucose_scan_df[records_glucose_scan_df['Record Type'] == 1]
    
    records_insulin_df = records_whole_df.drop(columns = ['Historic Glucose', 'Scan Glucose', 'Carbohydrate (grams)', 'Notes'])
    records_insulin_df = records_insulin_df[records_insulin_df['Record Type'] == 4]
    
    records_carbs_df = records_whole_df.drop(columns = ['Historic Glucose', 'Scan Glucose', 'Rapid insulin (units)', 'Long acting insulin (units)', 'Notes'])
    records_carbs_df = records_carbs_df[records_carbs_df['Record Type'] == 5]
    
    records_notes_df = records_whole_df.drop(columns = ['Historic Glucose', 'Scan Glucose', 'Rapid insulin (units)', 'Long acting insulin (units)', 'Carbohydrate (grams)'])
    records_notes_df = records_notes_df[records_notes_df['Record Type'] == 6]
    #Replaces NaN values with 0
    records_insulin_df = records_insulin_df.fillna(0)
    
    #Converts the timestamp to Datetime format so we can round it to the nearest 5 minutes
    records_glucose_df['Timestamp'] = records_glucose_df['Timestamp'].apply(pd.to_datetime, dayfirst=True)
    records_glucose_df['Timestamp'] = records_glucose_df['Timestamp'].dt.round('5min')
    records_glucose_scan_df['Timestamp'] = records_glucose_scan_df['Timestamp'].apply(pd.to_datetime, dayfirst=True)
    records_glucose_scan_df['Timestamp'] = records_glucose_scan_df['Timestamp'].dt.round('5min')
    records_insulin_df['Timestamp'] = records_insulin_df['Timestamp'].apply(pd.to_datetime, dayfirst=True)
    records_insulin_df['Timestamp'] = records_insulin_df['Timestamp'].dt.round('5min')
    records_carbs_df['Timestamp'] = records_carbs_df['Timestamp'].apply(pd.to_datetime, dayfirst=True)
    records_carbs_df['Timestamp'] = records_carbs_df['Timestamp'].dt.round('5min')
    records_notes_df['Timestamp'] = records_notes_df['Timestamp'].apply(pd.to_datetime, dayfirst=True)
    records_notes_df['Timestamp'] = records_notes_df['Timestamp'].dt.round('5min')

    #We no longer need the record type. Lets get rid of it
    records_glucose_df = records_glucose_df.drop(columns = ['Record Type'])
    records_glucose_scan_df = records_glucose_scan_df.drop(columns = ['Record Type'])
    records_insulin_df = records_insulin_df.drop(columns = ['Record Type'])
    records_carbs_df = records_carbs_df.drop(columns = ['Record Type'])
    records_notes_df = records_notes_df.drop(columns = ['Record Type'])
    
    #Creates the full merged dataframe
    records_df = pd.merge(left = records_glucose_df, right = records_glucose_scan_df, left_on =['Timestamp'], right_on = ['Timestamp'], how = 'left')
    records_df = pd.merge(left = records_df, right = records_insulin_df, left_on =['Timestamp'], right_on = ['Timestamp'], how = 'left')
    records_df = pd.merge(left = records_df, right = records_carbs_df, left_on =['Timestamp'], right_on = ['Timestamp'], how = 'left')
    records_df = pd.merge(left = records_df, right = records_notes_df, left_on =['Timestamp'], right_on = ['Timestamp'], how = 'left')
    #Fill the NaN values. Though not sure if I want to do this for the glucose scans and history as well, because 0 would imply a deadly low.
    records_df['Rapid insulin (units)'] = records_df['Rapid insulin (units)'].fillna(0)
    records_df['Long acting insulin (units)'] = records_df['Long acting insulin (units)'].fillna(0)
    records_df['Carbohydrate (grams)'] = records_df['Carbohydrate (grams)'].fillna(0)
    
    #May have done something wrong with the merging, found some duplicate info so dropping them.
    records_df = records_df.drop_duplicates()
    #Makes timestamp the index, commented out for bugfixing
    #records_df = records_df.set_index('Timestamp')
    #records_df = records_df.sort_index()
    
    print(records_carbs_df)
    print(records_insulin_df)
    print(records_insulin_df.dtypes)
    print(records_df)

#Next create a way for users to input a year so they can look at that data, might want to consolidate data into daily.

meal_df = pd.DataFrame({'Meal/Food': pd.Series(dtype = 'string'), 'Carbohydrate (grams)': pd.Series(dtype = 'int')})

#Function to add new data to our meal list
def add_meal():
    global meal_df
    Food = input("Enter a name for the meal")
    Carbs = input("Enter the weight in grams of Carbohydrate in this meal")
    Carbs = int(Carbs)
    meal_data = pd.DataFrame([[Food, Carbs]], columns = ['Meal/Food', 'Carbohydrate (grams)'])
    meal_df = pd.concat([meal_df, meal_data])
    return

def add_record():
    global records_df
    Timestamp = datetime.now()
    Scan = input("Enter your bloodsugar level")
    Scan = float(Scan)
    Carbs = input("Enter the weight in grams of any Carbohydrate you have eaten")
    Carbs = int(Carbs)
    F_Insulin = input("Enter your rapid insulin dose if you have taken it for the carbohydrate")
    F_Insulin = int(F_Insulin)
    L_Insulin = input("Enter your long acting insulin dose if you have injected it")
    L_Insulin = int(L_Insulin)
    Notes = input("Any notes?")
    records_data = pd.DataFrame([[Timestamp, Scan, Scan, F_Insulin, L_Insulin, Carbs, Notes]], columns = ['Timestamp', 'Historic Glucose', 'Scan Glucose',
                                                                                           'Rapid insulin (units)', 'Long acting insulin (units)',
                                                                                           'Carbohydrate (grams)', 'Notes'])
    records_data['Rapid insulin (units)'] = records_data['Rapid insulin (units)'].fillna(0)
    records_data['Long acting insulin (units)'] = records_data['Long acting insulin (units)'].fillna(0)
    records_data['Carbohydrate (grams)'] = records_data['Carbohydrate (grams)'].fillna(0)
    records_data['Timestamp'] = records_data['Timestamp'].apply(pd.to_datetime)
    records_data['Timestamp'] = records_data['Timestamp'].dt.round('5min')
    records_df = pd.concat([records_df, records_data])
    #Reorganises the data
    #records_df = records_df.set_index('Timestamp')
    #records_df = records_df.sort_index()
    return

upload_data()


#add_record()

# Ok for the graph I will probably have to manually make different timestamp ranges to do it. So just going to use an example for now
#def month_graph():
    #global records_df
    #today = date.today()
    #graph_df = records_df.set_index('Timestamp')
    #graph_df = graph_df.sort_index()
   # graph_df = graph_df.loc[today - pd.Timedelta(days = 30): today].reset_index()
   # print(graph_df)
   # return

#Successfully gives us the average glucose for each day. Now just need to make an actual graph with this data
def test_graph_historic():
    global records_df
    graph_df = records_df.drop(columns = ['Scan Glucose','Rapid insulin (units)','Long acting insulin (units)', 'Carbohydrate (grams)', 'Notes'])
    graph_df = graph_df.set_index('Timestamp').groupby(pd.Grouper(freq='d')).mean().dropna(how='all')
    graph_df['Historic Glucose'] = graph_df['Historic Glucose'].round(1)
    
    #Below code allows us to find January 2022 values. Will have to find a way to make it easier for other months and years
    locate = (graph_df.index > '2021-12-31') & (graph_df.index < '2022-02-01')
    January_2022_df = graph_df.loc[locate]
    
    plt.figure(figsize = (40,10))
    plt.grid()
    graph = sns.lineplot(x = January_2022_df.index, y = 'Historic Glucose', data = January_2022_df)
    graph.set(xticks = January_2022_df.index.values)
    
    
    print(January_2022_df)
    return

class graph(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        box = self.ids.box
        box.add_widget(FigureCanvasKivyAgg(plt))
        
class DataFrameApp(App):
    def build(self):
        return DfguiWidget(records_df)
#class DataFrameApp(App):
    #def build(self):
        #graph_test = Graph()
        #graph_test.draw(records_df)

        #bar_test = BarGraph()
        #bar_test.x_tick_labels = test_time

        #graph_test.draw(records_df)

        #return graph_test 
       


if __name__ == '__main__':
    DataFrameApp().run()

#month_graph()
test_graph_historic()
#print(meal_df)