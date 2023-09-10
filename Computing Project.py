# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas
import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty, NumericProperty
from kivy.lang import Builder
#from kivy.uix.anchorlayout import AnchorLayout
#from kivymd.app import MDApp
#from kivy.lang.builder import Builder
#from kivymd.uix.datatables import MDDataTable
#from kivy.metrics import dp

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#from pymongo import MongoClient
import numpy as np
import tkinter as tk
from tkinter import filedialog
import datetime as dt
from datetime import date
from datetime import datetime

def get_data_table(dataframe):
    column_data = list(dataframe.columns)
    row_data = dataframe.to_records(index=False)
    return column_data, row_data

fields = ['Device', 'Serial', 'Timestamp', 'Record Type', 'Historic Glucose', 'Scan Glucose', 'Non-numeric rapid insulin', 'Rapid insulin (units)',
          'Non-numeric food', 'Carbohydrate (grams)', 'Carbohydrate (servings)', 'Non-numeric long acting insulin', 'Long acting insulin (units)',
          'Notes', 'Strip glucose mmol/L', 'Ketone mmol/L', 'Meal insulin', 'Correction', 'User change insulin (units)']


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
    
def records_convert():
    records_dict = records_df.to_dict('dict')

    
upload_data()

#class MyGrid(GridLayout):
    #def __init__(self, **kwargs):
       # super(MyGrid, self).__init__(**kwargs)


#class main_screen(Screen):
    
   # r1 = RelativeLayout(size = (300, 300))
    
   # def record_pressed(instance):
      #  print('Pressed')
   #     Manager.current = 'screen1'
    
   # records = Button(text = 'Records',size_hint = (.25, .1),)
    
   # records.bind(on_press = record_pressed)
                     
   # reports = Button(text = 'Reports',size_hint = (.25, .1),
   #                  pos_hint = {'x':.25})
    
   # food = Button(text = 'Food and Meals',size_hint = (.25, .1),
    #                 pos_hint = {'x':.50})
    
    #options = Button(text = 'Options',size_hint = (.25, .1),
    #                 pos_hint = {'x':.75})
    
    #r1.add_widget(records)
    #r1.add_widget(reports)
    #r1.add_widget(food)
   # r1.add_widget(options)
    

#class screen_1(Screen):
   # r1 = RelativeLayout(size = (300, 300))
    #reports = Button(text = 'Reports',size_hint = (.25, .1),
     #                pos_hint = {'x':.25})
    #r1.add_widget(reports)
    
class MainScreen(Screen):
    pass


#class AppGUI(GridLayout):
    #def __init__(self, **kwargs):
        #super().__init__(**kwargs)
        #self.rv.data = [{'label_1': str(x['number']), 'label_2': str(x['name']), 'label_3': str(x['size']), 'checkbox_1': x['in_stock']} for x in records_df]

class ReportScreen(Screen):
    pass

class RecordScreen(Screen):
    class
    def __init__(self, records_df, **kwargs):
        super().__init__(**kwargs)
        self.cols = len(records_df.columns) # number of columns
        self.rows = len(records_df.index) + 1 # number of rows
        for i, col_name in enumerate(df.columns):
            self.add_widget(Label(text=col_name))
        for i, row in df.iterrows():
            for j, val in enumerate(row):
                self.add_widget(Label(text=str(val))) 
    
    #def display_record(self):
        
        #layout = AnchorLayout()
        
       # container = my_root.ids.container
        #print(container)
       # column_data, row_data = get_data_table(records_df)
        #column_data = [(x, dp(60)) for x in column_data]
        
        #table = MDDataTable(
            column_data = column_data, row_data = row_data, use_pagination = True)
       # layout.add_widget(table)
        #return layout
    

class MealScreen(Screen):
    pass

class OptionScreen(Screen):
    pass

#class Show(Screen):
    #def fill(self, dt):
        
        

class WindowManager(ScreenManager):
    pass
    #main_screen = ObjectProperty(None)
   # screen_1 = ObjectProperty(None)
   
#class FloatLayoutKivy(FloatLayout):
   # pass
   
kv = Builder.load_file('My.kv')



class MyApp(App):
    def build(self):
        return kv
        
   #     r1 = RelativeLayout(size = (300, 300))
        
 #       def record_pressed(instance):
     #      print('Pressed')
        
   #     records = Button(text = 'Records',size_hint = (.25, .1),)
        
    #    records.bind(on_press = record_pressed)
                         
    #    reports = Button(text = 'Reports',size_hint = (.25, .1),
    #                     pos_hint = {'x':.25})
        
    #   food = Button(text = 'Food and Meals',size_hint = (.25, .1),
    #                    pos_hint = {'x':.50})
        
     #   options = Button(text = 'Options',size_hint = (.25, .1),
     #                    pos_hint = {'x':.75})
        
     #   r1.add_widget(records)
     #   r1.add_widget(reports)
     #   r1.add_widget(food)
     #   r1.add_widget(options)
        
    #    return r1
       
      # m = Manager(transition = NoTransition())
       #return m
        
        
      #  r1 = RelativeLayout(size = (300, 300))
        
     #   records = Button(text = 'Records',size_hint = (.25, .1),)
        
     #   records.bind(on_press = record_pressed)
                         
      #  reports = Button(text = 'Reports',size_hint = (.25, .1),
      #                   pos_hint = {'x':.25})
        
       # food = Button(text = 'Food and Meals',size_hint = (.25, .1),
       #                  pos_hint = {'x':.50})
        
       # options = Button(text = 'Options',size_hint = (.25, .1),
       #                  pos_hint = {'x':.75})
        
       # r1.add_widget(records)
        #r1.add_widget(reports)
        #r1.add_widget(food)
        #r1.add_widget(options)
        
       # def record_pressed(self, instance):
        #    print('Pressed')
        
        #return r1
       
        
        #return Label(text = " This is a test")

    
if __name__ == "__main__":
    MyApp().run()
    