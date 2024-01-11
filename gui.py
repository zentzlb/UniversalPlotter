# from tkinter import Tk, filedialog, StringVar
import os
import tkinter
import tkinter.simpledialog
from tkinter import filedialog, simpledialog, commondialog, dialog, colorchooser
from tkinter import ttk as TKK, messagebox
from utils import catch, check_file, check_ext, trim_series, process_series
from HIC15 import hic15, hic_ais
from Cmax import chest_AIS3
from Nij import neck_AIS
from lasso.dyna import Binout
from math import cos, sin, tan, acos, asin, atan, atan2, pi, e

from test2 import SimpleChoiceBox

import matplotlib.pyplot as plt

from filters import CFC_filter
from matplotlib import pyplot

import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
import dask.array as da

from csv_tools import *
from binout_tools import get_binout


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
        self.data: pd.DataFrame | Binout = pd.DataFrame()
        # self.binout = Binout
        self.ext = ''
        self.series = {}
        # self.data = pd.DataFrame()
        self.text = da.array([])
        self.cfc = 0
        self.legend = []
        self.xlabel = ''
        self.ylabel = ''

        self.file_var = tkinter.StringVar(value='file selection')
        self.file_label = tkinter.Label(master=self.root, textvariable=self.file_var)
        self.file_label.grid(row=10, column=0)

        self.column_var = tkinter.StringVar(value='header selection')
        self.column_label = tkinter.Label(master=self.root, textvariable=self.column_var)
        self.column_label.grid(row=11, column=0)

        self.xaxis_var = tkinter.StringVar(value='x axis selection')
        self.xaxis_label = tkinter.Label(master=self.root, textvariable=self.xaxis_var)
        self.xaxis_label.grid(row=12, column=0)

        self.yaxis_var = tkinter.StringVar(value='y axis selection')
        self.yaxis_label = tkinter.Label(master=self.root, textvariable=self.yaxis_var)
        self.yaxis_label.grid(row=13, column=0)

        self.series_var = tkinter.StringVar(value='series selection')
        self.series_label = tkinter.Label(master=self.root, textvariable=self.series_var)
        self.series_label.grid(row=14, column=0)

        self.browse_button = tkinter.Button(text="Browse Files",
                                            command=lambda: self.browse_fn(),
                                            width=25,
                                            height=1)
        self.browse_button.grid(row=0, column=0)

        self.open_button = tkinter.Button(text="Open Selected File",
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

        self.trim_var = tkinter.StringVar(value=f'Trim Data')
        self.trim_button = tkinter.Button(textvariable=self.trim_var,
                                          command=lambda: self.trim_fn(),
                                          width=25,
                                          height=1)
        self.trim_button.grid(row=3, column=0)

        self.xscale_var = tkinter.StringVar(value=f'X Scale')
        self.xscale_button = tkinter.Button(textvariable=self.xscale_var,
                                            command=lambda: self.xscale_fn(),
                                            width=25,
                                            height=1)
        self.xscale_button.grid(row=4, column=0)

        self.yscale_var = tkinter.StringVar(value=f'Y Scale')
        self.yscale_button = tkinter.Button(textvariable=self.yscale_var,
                                            command=lambda: self.yscale_fn(),
                                            width=25,
                                            height=1)
        self.yscale_button.grid(row=5, column=0)

        self.xoff_var = tkinter.StringVar(value=f'X Offset')
        self.xoff_button = tkinter.Button(textvariable=self.xoff_var,
                                          command=lambda: self.xoff_fn(),
                                          width=25,
                                          height=1)
        self.xoff_button.grid(row=6, column=0)

        self.yoff_var = tkinter.StringVar(value=f'Y Offset')
        self.yoff_button = tkinter.Button(textvariable=self.yoff_var,
                                          command=lambda: self.yoff_fn(),
                                          width=25,
                                          height=1)
        self.yoff_button.grid(row=7, column=0)

        self.add_button = tkinter.Button(text="Add To Data Series",
                                         command=lambda: self.addseries_fn(),
                                         width=25,
                                         height=1)
        self.add_button.grid(row=2, column=1)

        self.changeseries_button = tkinter.Button(text='Change Series Name',
                                                  command=lambda: self.changeseries_fn(),
                                                  width=25,
                                                  height=1)
        self.changeseries_button.grid(row=3, column=1)

        self.color_var = tkinter.StringVar(value="Set Color")
        self.color_button = tkinter.Button(textvariable=self.color_var,
                                           command=lambda: self.color_fn(),
                                           width=25,
                                           height=1)
        self.color_button.grid(row=4, column=1)

        self.xlabel_var = tkinter.StringVar(value='X Label')
        self.xlabel_button = tkinter.Button(textvariable=self.xlabel_var,
                                            command=lambda: self.xlabel_fn(),
                                            width=25,
                                            height=1)
        self.xlabel_button.grid(row=5, column=1)

        self.ylabel_var = tkinter.StringVar(value='Y Label')
        self.ylabel_button = tkinter.Button(textvariable=self.ylabel_var,
                                            command=lambda: self.ylabel_fn(),
                                            width=25,
                                            height=1)
        self.ylabel_button.grid(row=6, column=1)

        self.plot_button = tkinter.Button(text="Plot Selected",
                                          command=lambda: self.plot_fn(),
                                          width=25,
                                          height=1)
        self.plot_button.grid(row=9, column=1)

        self.clear_button = tkinter.Button(text="Clear",
                                           command=lambda: self.clear_fn(),
                                           width=25,
                                           height=1)
        self.clear_button.grid(row=0, column=1)

        self.del_button = tkinter.Button(text="Delete Series",
                                         command=lambda: self.del_series(),
                                         width=25,
                                         height=1)
        self.del_button.grid(row=1, column=1)

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

        self.series_dropdown = TKK.Combobox(state='readonly',
                                            values=[],
                                            width=27,
                                            height=10)
        self.series_dropdown.bind("<<ComboboxSelected>>", self.series_fn)
        self.series_dropdown.grid(row=14, column=1, columnspan=1)

        # self.shift_time_var1 = tkinter.StringVar(value=f'Select Starting Time ({self.cfc if self.cfc != 0 else "no start time selected"})')
        # self.shift_time_button1 = tkinter.Button(textvariable=self.shift_time_var1, command= lambda: self.)

    def browse_fn(self):
        """
        browse and select files
        :return:
        """
        self.files = {*self.files,
                      *{file for file in filedialog.askopenfilenames(filetypes=[('CSV', '.csv'), ('binout', '*')])
                        if check_file(file)}}
        self.update_filenames()

    def color_fn(self):
        """
        pick plot color for selected series
        :return:
        """
        skey = self.series_dropdown.get()
        icolor = self.series[skey]['color']
        color = colorchooser.askcolor(initialcolor=icolor)
        if color[0]:
            print(color)
            self.series[skey]['color'] = color[1]
            self.color_var.set(f"Change Color ({self.series[self.series_dropdown.get()]['color']})")

    @catch
    def open_fn(self):
        """
        open selected file
        :return:
        """
        key = self.file_dropdown.get()
        self.ext = check_ext(self.filenames[key])
        self.header_dropdown.set('')
        self.xaxis_dropdown.set('')
        self.yaxis_dropdown.set('')
        self.header_dropdown['values'] = []
        self.xaxis_dropdown['values'] = []
        self.yaxis_dropdown['values'] = []
        if self.ext == '.csv':
            self.column_var.set("header selection")
            self.xaxis_var.set("x axis selection")
            self.yaxis_var.set("y axis selection")

            self.data, self.text = open_csv(self.filenames[key])
            # self.binout = Binout
            if self.text.ndim > 1:
                self.text_rows = {' '.join([str(i) for i in row]):
                                      [str(i) for i in row] for row in self.text}
            else:
                text = ' '.join(self.text)
                self.text_rows = {text: list(self.text)}
                self.header_dropdown.set(text)
                self.header_fn(None)
            self.update_headers()
            print(self.text)
        else:
            self.data = get_binout(self.filenames[key])
            self.header_dropdown['values'] = self.data.read()
            self.column_var.set("data selection")
            self.xaxis_var.set("y axis selection")
            self.yaxis_var.set("id selection")

    # def

    def addseries_fn(self):
        """
        add data to saved series
        :return:
        """
        if self.ext == '.csv':
            self.addcsv_fn()
            self.series_dropdown['values'] = list(self.series.keys())
            self.series_dropdown.set(self.yaxis_dropdown.get())
        else:
            self.addbinout_fn()
            self.series_dropdown['values'] = list(self.series.keys())
            self.series_dropdown.set(f"{self.xaxis_dropdown.get()} {self.yaxis_dropdown.get()}")
        self.series_fn(None)

    def addcsv_fn(self):
        """
        add csv to data series
        :return:
        """
        xkey = self.xaxis_dropdown.get()
        ykey = self.yaxis_dropdown.get()

        self.series[ykey] = {'xdata': self.data[xkey],
                             'ydata': self.data[ykey],
                             'cfc': self.cfc,
                             'xscale': 1,
                             'yscale': 1,
                             'xoffset': 0,
                             'yoffset': 0,
                             'trim': (self.data[xkey].min(), self.data[xkey].max()),
                             'color': '#000000',
                             'style': '-',
                             'width': 2
                             }

    def addbinout_fn(self):
        """
        add binout to data series
        :return:
        """
        key1 = self.header_dropdown.get()
        key2 = self.xaxis_dropdown.get()
        key3 = self.yaxis_dropdown.get()

        if key3:
            index = list(self.data.read(key1, 'ids')).index(int(key3))
        else:
            index = 0

        if key1 and key2:
            options1 = [key1, 'time']
            options2 = [key1, key2]

            self.series[f"{key2} {key3}"] = {'xdata': pd.Series(self.data.read(*options1)),
                                             'ydata': pd.Series(self.data.read(*options2)[:, index]),
                                             'cfc': self.cfc,
                                             'xscale': 1,
                                             'yscale': 1,
                                             'xoffset': 0,
                                             'yoffset': 0,
                                             'trim': (self.data.read(*options1).min(), self.data.read(*options1).max()),
                                             'color': '#000000',
                                             'style': '-',
                                             'width': 2
                                             }

    @catch
    def trim_fn(self):
        """
        trim selected series
        :return:
        """
        skey = self.series_dropdown.get()
        lower_lim = simpledialog.askfloat('Set Data Limits',
                                          'enter data lower limit',
                                          minvalue=self.series[skey]['xdata'].min(),
                                          maxvalue=self.series[skey]['xdata'].max(),
                                          initialvalue=self.series[skey]['trim'][0])
        upper_lim = simpledialog.askfloat('Set Data Limits',
                                          'enter data upper limit',
                                          minvalue=self.series[skey]['xdata'].min(),
                                          maxvalue=self.series[skey]['xdata'].max(),
                                          initialvalue=self.series[skey]['trim'][1])
        if upper_lim is not None and lower_lim is not None:
            self.series[skey]['trim'] = (lower_lim, upper_lim)
            print((lower_lim, upper_lim))

    @catch
    def plot_fn(self):
        """
        plot all current data series
        :return:
        """

        if not plt.fignum_exists(1):
            self.legend.clear()
        plt.figure(1)

        for key in self.series:
            xdata, ydata = process_series(self.series[key])

            plt.plot(xdata, ydata, color=self.series[key]['color'])
            self.legend.append(f"{key}")

        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend(self.legend)
        plt.show()

    @catch
    def hic15_fn(self):
        """
        calculate HIC15 AIS2+ injury risk
        :return:
        """
        hic, hic_t = hic15(self.data['Display Name'].to_numpy(),
                           self.data['Head Acceleration X'].to_numpy(),
                           self.data['Head Acceleration Y'].to_numpy(),
                           self.data['Head Acceleration Z'].to_numpy())

        ais2, ais3 = hic_ais(hic)
        messagebox.showinfo('HIC15', f'HIC15: {hic:0.1f}'
                                     f'\nAIS2+ Risk: {100 * ais2:0.2f}%'
                                     f'\nAIS2+ Risk: {100 * ais3:0.2f}%')

    @catch
    def cmax_fn(self):
        """
        calculate chest AIS3+ injury risk based on Cmax
        :return:
        """
        cmax = self.data['DS_78051-317_EY5223'].to_numpy().__abs__().max()
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
        fz_norm = self.data['Neck Upper Force Z'].to_numpy() / 4500
        my_norm = np.array([my_fn(my) for my in self.data['Neck Upper Moment Y'].to_numpy()])
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
        self.data = pd.DataFrame()
        # self.binout = Binout
        self.series = {}
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
    def del_series(self):
        """
        delete selected series
        :return:
        """
        # skey = self.series_dropdown.get()
        # if skey:
        self.series.__delitem__(self.series_dropdown.get())
        self.series_dropdown['values'] = list(self.series.keys())
        self.series_dropdown.set('')  # self.series_dropdown['values'][0]
        self.series_fn(None)

    def filter_fn(self):
        """
        CFC filter
        :return:
        """
        cfc = simpledialog.askinteger('CFC filtering',
                                      'enter CFC filter type (0 is unfiltered)',
                                      minvalue=0,
                                      maxvalue=1000,
                                      initialvalue=self.cfc)
        if cfc is not None:
            self.cfc = cfc
            self.filter_var.set(
                f'Select Filter ({"CFC " if self.cfc != 0 else ""}'
                f'{self.cfc if self.cfc != 0 else "no filter"})'
            )
            if self.series_dropdown.get():
                self.series[self.series_dropdown.get()]['cfc'] = cfc
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
        if type(self.data) is pd.DataFrame:
            self.headers = self.text_rows[self.header_dropdown.get()]
            self.data.columns = self.headers
            self.xaxis_dropdown['values'] = self.headers
            self.yaxis_dropdown['values'] = self.headers
            print(self.data)
        elif type(self.data) is Binout:
            xdrop = list(self.data.read(self.header_dropdown.get()))
            xdrop.sort()
            self.xaxis_dropdown['values'] = xdrop
            self.yaxis_dropdown['values'] = []

    def xaxis_fn(self, event: tkinter.Event):
        if type(self.data) is Binout:
            options = (self.header_dropdown.get(), self.xaxis_dropdown.get())
            if len(self.data.read(*options).shape) > 1:
                options = (self.header_dropdown.get(), 'ids')
                ids = self.data.read(*options)
                self.yaxis_dropdown['values'] = list(ids)
                self.yaxis_dropdown.set(ids[0])
            else:
                self.yaxis_dropdown['values'] = []
                self.yaxis_dropdown.set('')

    def yaxis_fn(self, event: tkinter.Event):
        pass

    def series_fn(self, event: tkinter.Event | None):
        key = self.series_dropdown.get()
        if key:
            self.cfc = self.series[key]['cfc']
        else:
            self.cfc = 0
        self.update_buttons()
        # self.filter_var.set(
        #     f'Select Filter ({"CFC " if self.cfc != 0 else ""}'
        #     f'{self.cfc if self.cfc != 0 else "no filter"})'
        # )
        # self.color_var.set(f"Change Color ({self.series[self.series_dropdown.get()]['color']})")
        # print(self.column_var.get())

    # def x_axis_start_shift(self)
    def update_filenames(self):
        """
        update filenames dictionary from files set
        :return:
        """
        self.filenames = {os.path.splitext(os.path.basename(file))[0]: file
                          for file in self.files if check_file(file)}
        self.file_dropdown['values'] = list(self.filenames.keys())
        print(self.filenames)

    def update_headers(self):
        """
        update headers dropdown menu
        :return:
        """
        if type(self.data) is pd.DataFrame:
            self.header_dropdown['values'] = list(self.text_rows.keys())
        elif type(self.data) is Binout:
            self.header_dropdown['values'] = self.data.read()

    def update_buttons(self):
        key = self.series_dropdown.get()
        self.xscale_var.set(f'X Scale{": " + str(round(self.series[key]["xscale"], 3)) if key else ""}')
        self.yscale_var.set(f'Y Scale{": " + str(round(self.series[key]["yscale"], 3)) if key else ""}')
        self.xoff_var.set(f'X Offset{": " + str(round(self.series[key]["xoffset"], 3)) if key else ""}')
        self.yoff_var.set(f'Y Offset{": " + str(round(self.series[key]["yoffset"], 3)) if key else ""}')
        self.xlabel_var.set(f'X Label {self.xlabel}')
        self.ylabel_var.set(f'Y Label {self.ylabel}')
        self.color_var.set(f'Change Color {self.series[key]["color"] if key else ""}')
        self.filter_var.set(
            f'Select Filter ({"CFC " if self.cfc != 0 else ""}'
            f'{self.cfc if self.cfc != 0 else "no filter"})'
        )

    def main(self) -> None:
        """
        main loop
        :return:
        """
        tkinter.mainloop()

    def changeseries_fn(self):
        key = self.series_dropdown.get()
        name = tkinter.simpledialog.askstring('Series Name',
                                              'enter series name',
                                              initialvalue=key)
        if name:
            self.series[name] = self.series[key]
            self.series.__delitem__(key)
            self.series_dropdown['values'] = list(self.series.keys())
            self.series_dropdown.set(name)

    def xlabel_fn(self):
        name = tkinter.simpledialog.askstring('X',
                                              'enter x axis label',
                                              initialvalue=self.xlabel)
        if name:
            self.xlabel = name
            self.xlabel_var.set(f'X Label {self.xlabel}')

    def ylabel_fn(self):
        name = tkinter.simpledialog.askstring('Y',
                                              'enter y axis label',
                                              initialvalue=self.ylabel)
        if name:
            self.ylabel = name
            self.ylabel_var.set(f'Y Label {self.ylabel}')

    @catch
    def xscale_fn(self):
        key = self.series_dropdown.get()
        if key:
            xscale = simpledialog.askstring('Set X Scale',
                                            f'enter x scaling factor or mathematical expression \n'
                                            f'(cos, sin, tan, acos, asin, atan, atan2, pi, e)',
                                            initialvalue=self.series[key]['xscale'])

            if xscale:
                self.series[key]['xscale'] = eval(xscale)
                self.xscale_var.set(f'X Scale: {self.series[key]["xscale"]:0.3f}')

    @catch
    def yscale_fn(self):
        key = self.series_dropdown.get()
        if key:
            yscale = simpledialog.askstring('Set Y Scale',
                                            f'enter y scaling factor or mathematical expression \n'
                                            f'(cos, sin, tan, acos, asin, atan, atan2, pi, e)',
                                            initialvalue=self.series[key]['yscale'])

            if yscale:
                self.series[key]['yscale'] = eval(yscale)
                self.yscale_var.set(f'Y Scale: {self.series[key]["yscale"]:0.3f}')

    @catch
    def xoff_fn(self):
        key = self.series_dropdown.get()
        if key:
            xoff = simpledialog.askstring('Set X Offset',
                                          f'enter x offset or mathematical expression \n'
                                          f'(cos, sin, tan, acos, asin, atan, atan2, pi, e)',
                                          initialvalue=self.series[key]['xoffset'])

            if xoff:
                self.series[key]['xoffset'] = eval(xoff)
                self.xoff_var.set(f'X Offset: {self.series[key]["xoffset"]:0.3f}')

    @catch
    def yoff_fn(self):
        key = self.series_dropdown.get()
        if key:
            yoff = simpledialog.askstring('Set Y Offset',
                                          f'enter y offset or mathematical expression \n'
                                          f'(cos, sin, tan, acos, asin, atan, atan2, pi, e)',
                                          initialvalue=self.series[key]['yoffset'])

            if yoff:
                self.series[key]['yoffset'] = eval(yoff)
                self.yoff_var.set(f'Y Offset: {self.series[key]["yoffset"]:0.3f}')


if __name__ == '__main__':
    gui = GUI()
    gui.main()
