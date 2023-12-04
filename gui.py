# from tkinter import Tk, filedialog, StringVar
import tkinter
from tkinter import filedialog, simpledialog, commondialog, dialog
from tkinter import ttk as TKK, messagebox

import matplotlib.pyplot as plt

from filters import CFC_filter
from matplotlib import pyplot

import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
import dask.array as da

from csv_tools import *


class GUI:
    """
    class for selecting and plotting csv files
    """

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('CSV Plotter')

        self.files = set()
        self.filenames = {}
        self.text_rows = {}
        self.headers = []
        self.df = pd.DataFrame()
        self.new_df = pd.DataFrame()
        # self.data = pd.DataFrame()
        self.text = da.array([])
        self.cfc = 0
        self.legend = []

        self.file_var = tkinter.StringVar(value='file selection')
        self.file_label = tkinter.Label(master=self.root, textvariable=self.file_var)
        self.file_label.grid(row=10, column=0)

        self.column_var = tkinter.StringVar(value='header selection')
        self.column_label = tkinter.Label(master=self.root, textvariable=self.column_var)
        self.column_label.grid(row=11, column=0)

        self.xaxis_var = tkinter.StringVar(value='xaxis selection')
        self.xaxis_label = tkinter.Label(master=self.root, textvariable=self.xaxis_var)
        self.xaxis_label.grid(row=12, column=0)

        self.yaxis_var = tkinter.StringVar(value='yaxis selection')
        self.yaxis_label = tkinter.Label(master=self.root, textvariable=self.yaxis_var)
        self.yaxis_label.grid(row=13, column=0)

        self.browse_button = tkinter.Button(text="Browse", command=lambda: self.browse_fn(), width=25, height=1)
        self.browse_button.grid(row=0, column=0)

        self.plot_button = tkinter.Button(text="Plot Selected", command=lambda: self.plot_fn(), width=25, height=1)
        self.plot_button.grid(row=1, column=1)

        self.open_button = tkinter.Button(text="Open Selected", command=lambda: self.open_fn(), width=25, height=1)
        self.open_button.grid(row=1, column=0)

        self.filter_var = tkinter.StringVar(value=f'Select Filter ({self.cfc if self.cfc != 0 else "no filter"})')
        self.filter_button = tkinter.Button(textvariable=self.filter_var, command=lambda: self.filter_fn(), width=25, height=1)
        self.filter_button.grid(row=2, column=0)

        self.browse_button = tkinter.Button(text="Clear", command=lambda: self.clear_fn(), width=25, height=1)
        self.browse_button.grid(row=0, column=1)

        self.file_dropdown = TKK.Combobox(state='readonly', values=list(self.filenames.keys()), width=27, height=10)
        self.file_dropdown.grid(row=10, column=1, columnspan=10)

        self.header_dropdown = TKK.Combobox(state='readonly', values=[], width=27, height=10)
        self.header_dropdown.bind("<<ComboboxSelected>>", self.header_fn)
        self.header_dropdown.grid(row=11, column=1, columnspan=10)

        self.xaxis_dropdown = TKK.Combobox(state='readonly', values=[], width=27, height=10)
        self.xaxis_dropdown.bind("<<ComboboxSelected>>", self.xaxis_fn)
        self.xaxis_dropdown.grid(row=12, column=1, columnspan=10)

        self.yaxis_dropdown = TKK.Combobox(state='readonly', values=[], width=27, height=10)
        self.yaxis_dropdown.bind("<<ComboboxSelected>>", self.yaxis_fn)
        self.yaxis_dropdown.grid(row=13, column=1, columnspan=10)

        # self.shift_time_var1 = tkinter.StringVar(value=f'Select Starting Time ({self.cfc if self.cfc != 0 else "no start time selected"})')
        # self.shift_time_button1 = tkinter.Button(textvariable=self.shift_time_var1, command= lambda: self.)


    def browse_fn(self):
        """
        browse and select files
        :return:
        """
        self.files = {*self.files, *filedialog.askopenfilenames(filetypes=[('CSV', '.csv')])}
        self.update_filenames()

    def plot_fn(self):

        xkey = self.xaxis_dropdown.get()
        ykey = self.yaxis_dropdown.get()

        if not plt.fignum_exists(1):
            self.legend.clear()


        try:
            xdata = self.df[xkey]
            ydata = self.df[ykey]

            if self.cfc != 0:
                ydata = CFC_filter(1/10000, ydata, self.cfc)

            plt.figure(1)
            plt.plot(xdata, ydata)
            plt.xlabel('Time')
            self.legend.append(f"{ykey} {self.cfc if self.cfc > 0 else ''}")
            plt.legend(self.legend)
            plt.show()
        except KeyError:
            tkinter.messagebox.showerror('KeyError', 'please select valid x and y data series')

    def clear_fn(self):
        """
        reset gui and clear all stored data
        :return:
        """
        self.files.clear()
        self.filenames.clear()
        self.text_rows.clear()
        self.headers.clear()
        self.df = pd.DataFrame()
        self.new_df = pd.DataFrame()
        self.df = pd.DataFrame()
        self.text = np.array([])
        self.cfc = 0

        plt.close()

        self.update_filenames()
        self.update_headers()

        self.file_dropdown.set('')
        self.header_dropdown.set('')
        self.xaxis_dropdown.set('')
        self.yaxis_dropdown.set('')

    def open_fn(self):
        """
        open selected file
        :return:
        """
        key = self.file_dropdown.get()
        self.header_dropdown.set('')
        self.xaxis_dropdown.set('')
        self.yaxis_dropdown.set('')
        try:
            self.df, self.text = open_csv(self.filenames[key])
            self.text_rows = {' '.join([str(i) for i in row]): [str(i) for i in row] for row in self.text}
            self.update_headers()
            # print('file opened')
            print(self.text)
            # print(self.data)
        except KeyError:
            tkinter.messagebox.showerror('KeyError', 'please select valid filename')

    def filter_fn(self):
        """
        CFC filter
        :return:
        """
        self.cfc = simpledialog.askinteger('CFC filtering', 'enter CFC filter type (0 is unfiltered)', minvalue=0, maxvalue=1000)
        self.filter_var.set(f'Select Filter ({"CFC " if self.cfc != 0 else ""}{self.cfc if self.cfc != 0 else "no filter"})')
        print(self.cfc)

    def header_fn(self, event: tkinter.Event):
        """
        update columns of opened dataframe
        :param event: dropdown menu selection change
        :return:
        """
        self.xaxis_dropdown.set('')
        self.yaxis_dropdown.set('')
        print(type(event))
        self.headers = self.text_rows[self.header_dropdown.get()]
        self.df.columns = self.headers
        self.xaxis_dropdown['values'] = self.headers
        self.yaxis_dropdown['values'] = self.headers
        print(self.df)

    def xaxis_fn(self, event: tkinter.Event):
        pass

    def yaxis_fn(self, event: tkinter.Event):
        pass

    # def x_axis_start_shift(self)
    def update_filenames(self):
        """
        update filenames dictionary from files set
        :return:
        """
        self.filenames = {file.split('/')[-1][:-4]: file for file in self.files if file[-4:] == '.csv'}
        self.file_dropdown['values'] = list(self.filenames.keys())
        print(self.filenames)

    def update_headers(self):
        """
        update headers dropdown menu
        :return:
        """
        self.header_dropdown['values'] = list(self.text_rows.keys())

    def main(self) -> None:
        """
        main loop
        :return:
        """
        tkinter.mainloop()




if __name__ == '__main__':
    gui = GUI()
    gui.main()
