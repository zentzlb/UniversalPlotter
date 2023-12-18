# from tkinter import Tk, filedialog, StringVar
import tkinter
from tkinter import filedialog, simpledialog, commondialog, dialog
from tkinter import ttk as TKK, messagebox
from utils import catch
from HIC import hic15, Hic15, hicAIS2
from Cmax import chest_AIS3
from Nij import neck_AIS

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

        self.browse_button = tkinter.Button(text="Browse",
                                            command=lambda: self.browse_fn(),
                                            width=25,
                                            height=1)
        self.browse_button.grid(row=0, column=0)

        self.plot_button = tkinter.Button(text="Plot Selected",
                                          command=lambda: self.plot_fn(),
                                          width=25,
                                          height=1)
        self.plot_button.grid(row=1, column=1)

        self.open_button = tkinter.Button(text="Open Selected",
                                          command=lambda: self.open_fn(),
                                          width=25,
                                          height=1)
        self.open_button.grid(row=1, column=0)

        self.filter_var = tkinter.StringVar(value=f'Select Filter '
                                                  f'({self.cfc if self.cfc != 0 else "no filter"})')
        self.filter_button = tkinter.Button(textvariable=self.filter_var,
                                            command=lambda: self.filter_fn(),
                                            width=25,
                                            height=1)
        self.filter_button.grid(row=2, column=0)

        self.browse_button = tkinter.Button(text="Clear",
                                            command=lambda: self.clear_fn(),
                                            width=25,
                                            height=1)
        self.browse_button.grid(row=0, column=1)

        self.hic15_button = tkinter.Button(text="HIC15",
                                           command=lambda: self.hic15_fn(),
                                           width=25,
                                           height=1)
        self.hic15_button.grid(row=0, column=2)

        self.nij_button = tkinter.Button(text="Nij",
                                         command=lambda: self.nij_fn(),
                                         width=25,
                                         height=1)
        self.nij_button.grid(row=1, column=2)

        self.cmax_button = tkinter.Button(text="Cmax",
                                          command=lambda: self.cmax_fn(),
                                          width=25,
                                          height=1)
        self.cmax_button.grid(row=2, column=2)

        self.file_dropdown = TKK.Combobox(state='readonly',
                                          values=list(self.filenames.keys()),
                                          width=27,
                                          height=10)
        self.file_dropdown.grid(row=10, column=1, columnspan=1)

        self.header_dropdown = TKK.Combobox(state='readonly',
                                            values=[],
                                            width=27,
                                            height=10)
        self.header_dropdown.bind("<<ComboboxSelected>>", self.header_fn)
        self.header_dropdown.grid(row=11, column=1, columnspan=1)

        self.xaxis_dropdown = TKK.Combobox(state='readonly',
                                           values=[],
                                           width=27,
                                           height=10)
        self.xaxis_dropdown.bind("<<ComboboxSelected>>", self.xaxis_fn)
        self.xaxis_dropdown.grid(row=12, column=1, columnspan=1)

        self.yaxis_dropdown = TKK.Combobox(state='readonly',
                                           values=[],
                                           width=27,
                                           height=10)
        self.yaxis_dropdown.bind("<<ComboboxSelected>>", self.yaxis_fn)
        self.yaxis_dropdown.grid(row=13, column=1, columnspan=1)

        # self.shift_time_var1 = tkinter.StringVar(value=f'Select Starting Time ({self.cfc if self.cfc != 0 else "no start time selected"})')
        # self.shift_time_button1 = tkinter.Button(textvariable=self.shift_time_var1, command= lambda: self.)

    def browse_fn(self):
        """
        browse and select files
        :return:
        """
        self.files = {*self.files, *filedialog.askopenfilenames(filetypes=[('CSV', '.csv')])}
        self.update_filenames()

    @catch
    def plot_fn(self):

        xkey = self.xaxis_dropdown.get()
        ykey = self.yaxis_dropdown.get()

        if not plt.fignum_exists(1):
            self.legend.clear()

        xdata = self.df[xkey]
        ydata = self.df[ykey]

        if self.cfc != 0:
            ydata = CFC_filter(1 / 10000, ydata, self.cfc)

        plt.figure(1)
        plt.plot(xdata, ydata)
        plt.xlabel('Time')
        self.legend.append(
            f"{self.file_dropdown.get()} {ykey} {'CFC ' if self.cfc > 0 else ''}"
            f"{self.cfc if self.cfc > 0 else ''}")
        plt.legend(self.legend)
        plt.show()

    @catch
    def hic15_fn(self):
        """
        calculate HIC15 AIS2+ injury risk
        :return:
        """
        hic, hic_t = Hic15(self.df['Display Name'].to_numpy(),
                           self.df['Head Acceleration X'].to_numpy(),
                           self.df['Head Acceleration Y'].to_numpy(),
                           self.df['Head Acceleration Z'].to_numpy())

        ais2 = hicAIS2(hic)
        messagebox.showinfo('HIC15', f'HIC15: {hic:0.1f}'
                                     f'\nAIS2+ Risk: {100 * ais2:0.2f}%')

    @catch
    def cmax_fn(self):
        """
        calculate chest AIS3+ injury risk based on Cmax
        :return:
        """
        cmax = self.df['DS_78051-317_EY5223'].to_numpy().__abs__().max()
        ais3 = chest_AIS3(cmax)
        messagebox.showinfo('Cmax', f'Cmax: {cmax:0.1f}'
                                    f'\nAIS3+ Risk: {100 * ais3:0.2f}%')

    @catch
    def nij_fn(self):
        """
        calculate neck injury risk based on Nij
        :return:
        """
        my_fn = lambda x: x / 310 if x > 0 else x / 125
        fz_norm = self.df['Neck Upper Force Z'].to_numpy() / 4500
        my_norm = np.array([my_fn(my) for my in self.df['Neck Upper Moment Y'].to_numpy()])
        nij = max(fz_norm + my_norm)
        ais2, ais3, ais4, ais5 = neck_AIS(nij)
        messagebox.showinfo('Nij', f'Nij: {nij:0.1f}\n'
                                   f'AIS2+ Risk: {100 * ais2:0.2f}%\n'
                                   f'AIS3+ Risk: {100 * ais3:0.2f}%\n'
                                   f'AIS4+ Risk: {100 * ais4:0.2f}%\n'
                                   f'AIS5+ Risk: {100 * ais5:0.2f}%\n')

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

    @catch
    def open_fn(self):
        """
        open selected file
        :return:
        """
        key = self.file_dropdown.get()
        self.header_dropdown.set('')
        self.xaxis_dropdown.set('')
        self.yaxis_dropdown.set('')
        self.df, self.text = open_csv(self.filenames[key])
        if self.text.ndim > 1:
            self.text_rows = {' '.join([str(i) for i in row]):
                                  [str(i) for i in row] for row in self.text}
        else:
            text = ' '.join(self.text)
            self.text_rows = {text: list(self.text)}
            self.header_dropdown.set(text)
            self.header_fn(None)
        self.update_headers()
        # print('file opened')
        print(self.text)
        # print(self.data)

    def filter_fn(self):
        """
        CFC filter
        :return:
        """
        cfc = simpledialog.askinteger('CFC filtering',
                                      'enter CFC filter type (0 is unfiltered)',
                                      minvalue=0,
                                      maxvalue=1000)
        if cfc is not None:
            self.cfc = cfc
            self.filter_var.set(
                f'Select Filter ({"CFC " if self.cfc != 0 else ""}'
                f'{self.cfc if self.cfc != 0 else "no filter"})'
            )
            print(self.cfc)

    def header_fn(self, event: tkinter.Event | None):
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
