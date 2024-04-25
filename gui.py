import os
import time
import typing
from tkinter import (filedialog, simpledialog, commondialog, dialog, messagebox, colorchooser, Tk, Button,
                     Toplevel, Label, BooleanVar, StringVar, Scale, Event, mainloop)
from tkinter import ttk as TTK
from utils import (catch, check_file, check_ext, trim_series, process_series, enumerator,
                   trim_arrays, filter_arrays)
from HIC15 import hic15, hic_ais
from Cmax import chest_AIS3
from Nij import neck_AIS
from lasso.dyna import Binout
from femur import femur_ais2
from math import cos, sin, tan, acos, asin, atan, atan2, pi, e, inf, log
from BrIC import bric, bric_mps_ais, bric_csdm_ais
from damage3 import calc_damage, dmg_ais, dy_dt

import matplotlib.pyplot as plt

from filters import CFC_filter

import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
import dask.array as da

from csv_tools import open_csv
from binout_tools import get_binout, read_binout


class GUI:
    """
    class for selecting and plotting csv files
    """

    def __init__(self):
        self.root = Tk()
        self.root.title('CSV Plotter')
        # self.root.iconbitmap()
        self.files = []  # set()
        self.filenames = {}
        self.text_rows = {}
        self.headers = []
        self.data: pd.DataFrame | Binout | None = None
        self.ext = ''
        self.series = {}
        self.text = np.array([])
        self.cfc = 0
        self.trim = (-inf, inf)
        self.legend = []
        self.xlabel = ''
        self.ylabel = ''
        self.title = ''

        ##############
        #  COLUMN 0  #
        ##############

        self.filter_var = StringVar(value=f'Select Filter '
                                          f'({self.cfc if self.cfc != 0 else "no filter"})')
        self.filter_button = Button(textvariable=self.filter_var,
                                    command=lambda: self.filter_fn(),
                                    width=25,
                                    height=1)
        self.filter_button.grid(row=0, column=0)

        self.trim_var = StringVar(value=f'Trim Data')
        self.trim_button = Button(textvariable=self.trim_var,
                                  command=lambda: self.trim_popup(),
                                  width=25,
                                  height=1)
        self.trim_button.grid(row=1, column=0)

        self.xscale_var = StringVar(value=f'X Scale')
        self.xscale_button = Button(textvariable=self.xscale_var,
                                    command=lambda: self.xscale_fn(),
                                    width=25,
                                    height=1)
        self.xscale_button.grid(row=2, column=0)

        self.yscale_var = StringVar(value=f'Y Scale')
        self.yscale_button = Button(textvariable=self.yscale_var,
                                    command=lambda: self.yscale_fn(),
                                    width=25,
                                    height=1)
        self.yscale_button.grid(row=3, column=0)

        self.xoff_var = StringVar(value=f'X Offset')
        self.xoff_button = Button(textvariable=self.xoff_var,
                                  command=lambda: self.xoff_fn(),
                                  width=25,
                                  height=1)
        self.xoff_button.grid(row=4, column=0)

        self.yoff_var = StringVar(value=f'Y Offset')
        self.yoff_button = Button(textvariable=self.yoff_var,
                                  command=lambda: self.yoff_fn(),
                                  width=25,
                                  height=1)
        self.yoff_button.grid(row=5, column=0)

        self.color_var = StringVar(value="Set Color")
        self.color_button = Button(textvariable=self.color_var,
                                   command=lambda: self.color_fn(),
                                   width=25,
                                   height=1)
        self.color_button.grid(row=6, column=0)

        self.style_dropdown = TTK.Combobox(state='readonly',
                                           values=['None', '-', '--', '-.', ':'],
                                           width=27,
                                           height=10)
        self.style_dropdown.bind("<<ComboboxSelected>>", self.style_fn)
        self.style_dropdown.set('-')
        self.style_dropdown.grid(row=7, column=0, columnspan=1)

        self.marker_dropdown = TTK.Combobox(state='readonly',
                                            values=['None', '.', ',', 'o', 'v', '^', '<', '>',
                                                    '1', '2', '3', '4', '8', 's', 'p', 'P', '*',
                                                    'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_'],
                                            width=27,
                                            height=10)
        self.marker_dropdown.bind("<<ComboboxSelected>>", self.marker_fn)
        self.marker_dropdown.set('None')
        self.marker_dropdown.grid(row=8, column=0, columnspan=1)

        self.file_var = StringVar(value='file selection')
        self.file_label = Label(master=self.root, textvariable=self.file_var)
        self.file_label.grid(row=10, column=0)

        self.column_var = StringVar(value='header selection')
        self.column_label = Label(master=self.root, textvariable=self.column_var)
        self.column_label.grid(row=11, column=0)

        self.xaxis_var = StringVar(value='x axis selection')
        self.xaxis_label = Label(master=self.root, textvariable=self.xaxis_var)
        self.xaxis_label.grid(row=12, column=0)

        self.yaxis_var = StringVar(value='y axis selection')
        self.yaxis_label = Label(master=self.root, textvariable=self.yaxis_var)
        self.yaxis_label.grid(row=13, column=0)

        self.series_var = StringVar(value='series selection')
        self.series_label = Label(master=self.root, textvariable=self.series_var)
        self.series_label.grid(row=14, column=0)

        ##############
        #  COLUMN 1  #
        ##############

        self.browse_button = Button(text="Browse Files",
                                    command=lambda: self.browse_fn(),
                                    width=25,
                                    height=1)
        self.browse_button.grid(row=0, column=1)

        self.open_button = Button(text="Open Selected File",
                                  command=lambda: self.open_fn(),
                                  width=25,
                                  height=1)
        self.open_button.grid(row=1, column=1)

        self.clear_button = Button(text="Reset All",
                                   command=lambda: self.clear_fn(),
                                   width=25,
                                   height=1)
        self.clear_button.grid(row=2, column=1)

        self.del_button = Button(text="Delete Selected Series",
                                 command=lambda: self.del_series(),
                                 width=25,
                                 height=1)
        self.del_button.grid(row=3, column=1)

        self.add_button = Button(text="Add To Data Series",
                                 command=lambda: self.addseries_fn(),
                                 width=25,
                                 height=1)
        self.add_button.grid(row=4, column=1)

        self.changeseries_button = Button(text='Change Series Name',
                                          command=lambda: self.changeseries_fn(),
                                          width=25,
                                          height=1)
        self.changeseries_button.grid(row=5, column=1)

        self.xlabel_var = StringVar(value='X Label')
        self.xlabel_button = Button(textvariable=self.xlabel_var,
                                    command=lambda: self.xlabel_fn(),
                                    width=25,
                                    height=1)
        self.xlabel_button.grid(row=6, column=1)

        self.ylabel_var = StringVar(value='Y Label')
        self.ylabel_button = Button(textvariable=self.ylabel_var,
                                    command=lambda: self.ylabel_fn(),
                                    width=25,
                                    height=1)
        self.ylabel_button.grid(row=7, column=1)

        self.title_var = StringVar(value='Title')
        self.title_button = Button(textvariable=self.title_var,
                                   command=lambda: self.title_fn(),
                                   width=25,
                                   height=1)
        self.title_button.grid(row=8, column=1)

        self.plot_button = Button(text="Plot Selected",
                                  command=lambda: self.plot_popup(),
                                  width=25,
                                  height=1)
        self.plot_button.grid(row=9, column=1)

        self.file_dropdown = TTK.Combobox(state='readonly',
                                          values=list(self.filenames.keys()),
                                          width=27,
                                          height=10)
        self.file_dropdown.bind("<<ComboboxSelected>>", self.file_fn)
        self.file_dropdown.grid(row=10, column=1, columnspan=1)

        self.header_dropdown = TTK.Combobox(state='readonly',
                                            values=[],
                                            width=27,
                                            height=10)
        self.header_dropdown.bind("<<ComboboxSelected>>", self.header_fn)
        self.header_dropdown.grid(row=11, column=1, columnspan=1)

        self.xaxis_dropdown = TTK.Combobox(state='readonly',
                                           values=[],
                                           width=27,
                                           height=10)
        self.xaxis_dropdown.bind("<<ComboboxSelected>>", self.xaxis_fn)
        self.xaxis_dropdown.grid(row=12, column=1, columnspan=1)

        self.yaxis_dropdown = TTK.Combobox(state='readonly',
                                           values=[],
                                           width=27,
                                           height=10)
        self.yaxis_dropdown.bind("<<ComboboxSelected>>", self.yaxis_fn)
        self.yaxis_dropdown.grid(row=13, column=1, columnspan=1)

        self.series_dropdown = TTK.Combobox(state='readonly',
                                            values=[],
                                            width=27,
                                            height=10)
        self.series_dropdown.bind("<<ComboboxSelected>>", self.series_fn)
        self.series_dropdown.grid(row=14, column=1, columnspan=1)

        ##############
        #  COLUMN 2  #
        ##############

        self.hic15_button = Button(text="HIC15",
                                   command=lambda: self.hic15_fn(),
                                   width=25,
                                   height=1)
        self.hic15_button.grid(row=0, column=2)

        self.bric_button = Button(text="BrIC15",
                                  command=lambda: self.bric_fn(),
                                  width=25,
                                  height=1)
        self.bric_button.grid(row=1, column=2)

        self.bric_button = Button(text="DAMAGE",
                                  command=lambda: self.damage_fn(),
                                  width=25,
                                  height=1)
        self.bric_button.grid(row=2, column=2)

        self.nij_button = Button(text="Nij",
                                 command=lambda: self.nij_fn(),
                                 width=25,
                                 height=1)
        self.nij_button.grid(row=3, column=2)

        self.cmax_button = Button(text="Cmax",
                                  command=lambda: self.cmax_fn(),
                                  width=25,
                                  height=1)
        self.cmax_button.grid(row=4, column=2)

        self.cmax_button = Button(text="Femur",
                                  command=lambda: self.femur_fn(),
                                  width=25,
                                  height=1)
        self.cmax_button.grid(row=5, column=2)

        self.resultant_button = Button(text="Calculate Resultant",
                                       command=lambda: self.resultant_popup(),
                                       width=25,
                                       height=1)
        self.resultant_button.grid(row=6, column=2)

    def switch(self,
               func1: typing.Callable,
               func2: typing.Callable,
               args1: tuple = tuple(),
               args2: tuple = tuple(),
               kwargs1: dict = {},
               kwargs2: dict = {}):
        """
        switches behavior based on data type
        :param func1:
        :param func2:
        :param args1:
        :param args2:
        :param kwargs1:
        :param kwargs2:
        :return:
        """
        if type(self.data) is pd.DataFrame:
            return func1(*args1, **kwargs1)
        elif type(self.data) is Binout:
            return func2(*args2, **kwargs2)
        return

    def get_binout_ydata(self, key: str):
        if id_ := self.yaxis_dropdown.get():
            index = list(self.data.read(self.header_dropdown.get(), 'ids')).index(int(id_))  # NOQA
            return self.data.read(self.header_dropdown.get(), key)[:, index]
        else:
            return self.data.read(self.header_dropdown.get(), key)

    @catch
    def resultant_popup(self):
        if self.xaxis_dropdown.get():
            cfc = simpledialog.askinteger('set CFC filter',
                                          f'enter CFC filter type (0 is unfiltered)\n',
                                          minvalue=0,
                                          maxvalue=1000,
                                          initialvalue=self.cfc)

            def select_all():
                keys = [k for k in checkboxes if checkboxes[k]['bool'].get()]
                xkey = self.xaxis_dropdown.get()
                xdata: pd.Series = self.switch(lambda: self.data[xkey],
                                               lambda: pd.Series(self.data.read(self.header_dropdown.get(), 'time')))
                ydata = np.zeros_like(xdata)
                for key in keys:
                    array = self.switch(lambda k: self.data[k].to_numpy(),
                                        lambda k: self.get_binout_ydata(k),
                                        args1=(key,),
                                        args2=(key,))
                    if cfc != 0:
                        array = CFC_filter(1 / 10000, array, cfc)
                    ydata += array ** 2
                    # array += self.data[key].to_numpy() ** 2
                # if cfc != 0:
                #     ydata = CFC_filter(1 / 10000, np.sqrt(array), cfc)
                # else:
                #     ydata = np.sqrt(array)
                ser = pd.Series(np.sqrt(ydata))
                self.series['resultant'] = {'xdata': xdata,
                                            'ydata': ser,
                                            'cfc': str(cfc),
                                            'xscale': 1,
                                            'yscale': 1,
                                            'xoffset': 0,
                                            'yoffset': 0,
                                            'trim': (max(xdata.min(), self.trim[0]),
                                                     min(xdata.max(), self.trim[1])),
                                            'color': '#000000',
                                            'style': '-',
                                            'marker': 'None',
                                            'width': 2
                                            }
                self.series_dropdown['values'] = list(self.series.keys())
                self.series_dropdown.set('resultant')
                self.series_fn(None)
                win.destroy()

            win = Toplevel()
            win.wm_title("RESULTANT")
            # win.geometry('200x300')

            l = Label(win, text="select all data series to be used in calculating resultant")
            l.grid(row=0, column=0)
            checkboxes = {}

            value_set = self.switch(lambda: self.yaxis_dropdown['values'],
                                    lambda: self.xaxis_dropdown['values'])

            for i, value in enumerate(value_set):
                x = (i + 3) % 10
                y = (i + 3) // 10
                checkboxes[value] = {'bool': BooleanVar()}
                checkboxes[value]['checkbox'] = TTK.Checkbutton(win, text=value, variable=checkboxes[value]['bool'])
                checkboxes[value]['checkbox'].grid(row=x, column=y)

            b = TTK.Button(win, text="Okay", command=select_all)
            b.grid(row=1, column=0)
            b2 = TTK.Button(win, text="Check",
                            command=lambda: print([f"{k}: {checkboxes[k]['bool'].get()}" for k in checkboxes]))
            b2.grid(row=2, column=0)
        else:
            messagebox.showerror('Doofus Elert', 'select x axis data')

    @catch
    def plot_popup(self):
        def select_all():
            keys = [k for k in checkboxes if checkboxes[k]['bool'].get()]
            win.destroy()
            self.plot(keys)

        win = Toplevel()
        win.wm_title("SELECT SERIES")
        # win.geometry('200x300')

        l = Label(win, text="select all data series to plot")
        l.grid(row=0, column=0)
        checkboxes = {}

        for i, value in enumerate(self.series_dropdown['values']):
            x = (i + 2) % 10
            y = (i + 2) // 10
            checkboxes[value] = {'bool': BooleanVar()}
            checkboxes[value]['checkbox'] = TTK.Checkbutton(win, text=value, variable=checkboxes[value]['bool'])
            checkboxes[value]['checkbox'].grid(row=x, column=y)

        b = TTK.Button(win, text="Plot", command=select_all)
        b.grid(row=1, column=0)
        # print('plot called now')

    # @catch
    def trim_popup(self):

        def set_lower():
            value = simpledialog.askfloat('Set Lower Limit',
                                          'enter lower limit',
                                          minvalue=minimum,
                                          maxvalue=slider_max.get(),
                                          initialvalue=slider_min.get())
            if value is not None:
                slider_min.set(value)

        def set_upper():
            value = simpledialog.askfloat('Set Upper Limit',
                                          'enter upper limit',
                                          minvalue=slider_min.get(),
                                          maxvalue=maximum,
                                          initialvalue=slider_max.get())

            if value is not None:
                slider_max.set(value)

        def set_trim():
            self.trim = (slider_min.get(), slider_max.get())
            min_var.set(f"default min: {self.trim[0]}")
            max_var.set(f"default max: {self.trim[1]}")

        def reset_trim():
            self.trim = (-inf, inf)
            min_var.set(f"default min: {self.trim[0]}")
            max_var.set(f"default max: {self.trim[1]}")

        def set_lims():
            self.series[skey]['trim'] = (slider_min.get(), slider_max.get())
            win.destroy()

        skey = self.series_dropdown.get()
        minimum = self.series[skey]['xdata'].min()
        maximum = self.series[skey]['xdata'].max()
        # math

        win = Toplevel()
        win.wm_title("TRIM")
        # win.geometry('200x300')

        l_min = Label(win, text="MIN")
        l_min.grid(row=0, column=0)

        l_max = Label(win, text="MAX")
        l_max.grid(row=0, column=1)

        slider_min = Scale(win,
                           from_=minimum,
                           to=maximum,
                           digits=4,
                           resolution=0.001,
                           length=300,
                           command=lambda x: slider_max.configure(from_=x))
        slider_min.grid(row=1, column=0)
        slider_min.set(self.series[skey]['trim'][0])

        slider_max = Scale(win,
                           from_=minimum,
                           to=maximum,
                           digits=4,
                           resolution=0.001,
                           length=300,
                           command=lambda x: slider_min.configure(to=x))
        slider_max.grid(row=1, column=1)
        slider_max.set(self.series[skey]['trim'][1])

        min_var = StringVar(value=f"default min: {self.trim[0]}")
        min_default = Label(win, textvariable=min_var)
        min_default.grid(row=2, column=0)

        max_var = StringVar(value=f"default max: {self.trim[1]}")
        max_default = Label(win, textvariable=max_var)
        max_default.grid(row=2, column=1)

        b1 = TTK.Button(win, text="Set Min", command=set_lower, width=20)
        b1.grid(row=3, column=0)

        b2 = TTK.Button(win, text="Set Max", command=set_upper, width=20)
        b2.grid(row=3, column=1)

        b3 = TTK.Button(win, text="Set Default", command=set_trim, width=20)
        b3.grid(row=4, column=0)

        b4 = TTK.Button(win, text="Reset Default", command=reset_trim, width=20)
        b4.grid(row=4, column=1)

        b5 = TTK.Button(win, text="Set Current", command=set_lims, width=20)
        b5.grid(row=5, column=0, rowspan=5)

    def browse_fn(self):
        """
        browse and select files
        :return:
        """
        self.files = [*self.files,
                      *[file for file in filedialog.askopenfilenames(filetypes=[('CSV', '.csv'), ('binout', '*')])
                        if check_file(file) and file not in self.files]]
        self.update_filenames()

    @catch
    def color_fn(self):
        """
        pick plot color for selected series
        :return:
        """
        skey = self.series_dropdown.get()
        color = colorchooser.askcolor(initialcolor=self.series[skey]['color'])
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
            self.data, self.text = open_csv(self.filenames[key])

            self.column_var.set("header selection")
            self.xaxis_var.set("x axis selection")
            self.yaxis_var.set("y axis selection")
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
    @catch
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
                             'trim': (max(self.data[xkey].min(), self.trim[0]),
                                      min(self.data[xkey].max(), self.trim[1])),
                             'color': '#000000',
                             'style': '-',
                             'marker': 'None',
                             'width': 2
                             }

    @catch
    def addbinout_fn(self):
        """
        add binout to data series
        :return:
        """

        datax, datay = read_binout(self.data, (key1 := self.header_dropdown.get(),
                                               key2 := self.xaxis_dropdown.get(),
                                               key3 := self.yaxis_dropdown.get()))

        if datax is not None:
            self.series[f"{key2} {key3}"] = {'xdata': pd.Series(datax),
                                             'ydata': pd.Series(datay),
                                             'cfc': self.cfc,
                                             'xscale': 1,
                                             'yscale': 1,
                                             'xoffset': 0,
                                             'yoffset': 0,
                                             'trim': (max(datax.min(), self.trim[0]),
                                                      min(datax.max(), self.trim[1])),
                                             'color': '#000000',
                                             'style': '-',
                                             'marker': 'None',
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
        # time.sleep(0.1)
        upper_lim = simpledialog.askfloat('Set Data Limits',
                                          'enter data upper limit',
                                          minvalue=self.series[skey]['xdata'].min(),
                                          maxvalue=self.series[skey]['xdata'].max(),
                                          initialvalue=self.series[skey]['trim'][1])
        if upper_lim is not None and lower_lim is not None:
            self.series[skey]['trim'] = (lower_lim, upper_lim)
            print((lower_lim, upper_lim))

    @catch
    def plot(self, selected_series):
        """
        plot all current data series
        :return:
        """

        if not plt.fignum_exists(1):
            self.legend.clear()
        plt.figure(1)

        for key in selected_series:
            xdata, ydata = process_series(self.series[key])

            plt.plot(xdata,
                     ydata,
                     color=self.series[key]['color'],
                     linestyle=self.series[key]['style'],
                     marker=self.series[key]['marker'])
            self.legend.append(f"{key}")

        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend(self.legend)
        plt.title(self.title)
        plt.show()

    @catch
    def hic15_fn(self):
        """
        calculate HIC15 AIS2+ injury risk
        :return:
        """

        t = self.data['Display Name'].to_numpy()
        x_acc = self.data['Head Acceleration X'].to_numpy()
        y_acc = self.data['Head Acceleration Y'].to_numpy()
        z_acc = self.data['Head Acceleration Z'].to_numpy()

        t, x_acc, y_acc, z_acc = trim_arrays(x_acc, y_acc, z_acc, xdata=t, lim=self.trim)
        x_acc, y_acc, z_acc = filter_arrays(x_acc, y_acc, z_acc, cfc=1000)

        hic, hic_t = hic15(t, x_acc, y_acc, z_acc)

        # print(f"filtered: {hic}")

        # hic, hic_t = hic15(self.data['Display Name'].to_numpy(),
        #                    self.data['Head Acceleration X'].to_numpy(),
        #                    self.data['Head Acceleration Y'].to_numpy(),
        #                    self.data['Head Acceleration Z'].to_numpy())
        #
        # print(f"unfiltered: {hic}")

        ais2, ais3 = hic_ais(hic)
        messagebox.showinfo('HIC15', f'HIC15: {hic:0.1f}'
                                     f'\nHIC Time: {hic_t:0.3f}'
                                     f'\nAIS 2 Risk: {100 * ais2:0.2f}%'
                                     f'\nAIS 3+ Risk: {100 * ais3:0.2f}%')

    @catch
    def bric_fn(self):
        """
        calculate HIC15 AIS2+ injury risk
        :return:
        """
        dtr = pi / 180
        t = self.data['Display Name'].to_numpy()
        wx = self.data['Head Angular Velocity X'].to_numpy() * dtr
        wy = self.data['Head Angular Velocity Y'].to_numpy() * dtr
        wz = self.data['Head Angular Velocity Z'].to_numpy() * dtr

        t, wx, wy, wz = trim_arrays(wx, wy, wz, xdata=t, lim=self.trim)
        wx, wy, wz = filter_arrays(wx, wy, wz, cfc=1000)

        bric_score = bric(wx, wy, wz)

        # bric_score = bric(self.data['Head Angular Velocity X'].to_numpy() * dtr,
        #                   self.data['Head Angular Velocity Y'].to_numpy() * dtr,
        #                   self.data['Head Angular Velocity Z'].to_numpy() * dtr)

        # csdm_ais1, csdm_ais2, csdm_ais3, csdm_ais4, csdm_ais5p = bric_csdm_ais(bric_score)
        mps_ais1p, mps_ais2p, mps_ais3p, mps_ais4p, mps_ais5p = bric_mps_ais(bric_score)

        messagebox.showinfo('BrIC', f'BrIC: {bric_score: 0.3f}'
                                    f'\n'
                                    f'\n MPS'
                                    f'\n AIS 1+ Risk: {100 * mps_ais1p:0.2f}%'
                                    f'\n AIS 2+ Risk: {100 * mps_ais2p:0.2f}%'
                                    f'\n AIS 3+ Risk: {100 * mps_ais3p:0.2f}%'
                                    f'\n AIS 4+ Risk: {100 * mps_ais4p:0.2f}%'
                                    f'\n AIS 5+ Risk: {100 * mps_ais5p:0.2f}%'
                            )

    @catch
    def damage_fn(self):
        """
        calculate HIC15 AIS2+ injury risk
        :return:
        """
        dtr = pi / 180
        t = self.data['Display Name'].to_numpy()
        wx = self.data['Head Angular Velocity X'].to_numpy() * dtr
        wy = self.data['Head Angular Velocity Y'].to_numpy() * dtr
        wz = self.data['Head Angular Velocity Z'].to_numpy() * dtr

        t, wx, wy, wz = trim_arrays(wx, wy, wz, xdata=t, lim=self.trim)
        wx, wy, wz = filter_arrays(wx, wy, wz, cfc=1000)

        ax = dy_dt(wx, t)
        ay = dy_dt(wy, t)
        az = dy_dt(wz, t)

        dmg_score = calc_damage(ax, ay, az, t[1:])
        ais1, ais2, ais4 = dmg_ais(dmg_score)

        plt.figure(1)

        plt.plot(t[1:],
                 ax,
                 color='#ffab0f')  # (255, 171, 15)
        plt.plot(t[1:],
                 ay,
                 color='#cd0532')
        plt.plot(t[1:],
                 az,
                 color='#0080ff')
        plt.xlabel('Time (s)')
        plt.ylabel('Angular Acceleration (rads/s/s)')
        plt.legend(['Ax', 'Ay', 'Az'])
        plt.title('Damage Components')
        plt.show()

        messagebox.showinfo('DAMAGE', f'Damage: {dmg_score: 0.3f}'
                                      f'\n'
                                      f'\n AIS 1+ Risk: {100 * ais1:0.2f}%'
                                      f'\n AIS 2+ Risk: {100 * ais2:0.2f}%'
                                      f'\n AIS 4+ Risk: {100 * ais4:0.2f}%'
                            )

    @catch
    def cmax_fn(self):
        """
        calculate chest AIS3+ injury risk based on Cmax
        :return:
        """
        t = self.data['Display Name'].to_numpy()
        c = self.data['DS_78051-317_EY5223'].to_numpy()
        t, c = trim_arrays(c, xdata=t, lim=self.trim)
        c: np.ndarray = CFC_filter(1 / 10000, c, cfc=180)
        # cmax = self.data['DS_78051-317_EY5223'].to_numpy().__abs__().max()
        cmax = c.__abs__().max()
        ais3 = chest_AIS3(cmax)
        messagebox.showinfo('Cmax', f'Cmax: {cmax:0.1f}'
                                    f'\nAIS3+ Risk: {100 * ais3:0.2f}%')

    @catch
    def nij_fn(self):
        """
        calculate neck injury risk based on Nij
        :return:
        """
        t = self.data['Display Name'].to_numpy()
        fz = self.data['Neck Upper Force Z'].to_numpy()
        my = self.data['Neck Upper Moment Y'].to_numpy()

        t, fz, my = trim_arrays(fz, my, xdata=t, lim=self.trim)
        fz = CFC_filter(1 / 10000, fz, 1000)
        my = CFC_filter(1 / 10000, my, 600)

        my_fn = lambda x: x / 310 if x > 0 else -x / 125
        fz_norm = (fz / 4500).__abs__()
        my_norm = np.array([my_fn(m) for m in my])
        # fz_norm = abs(self.data['Neck Upper Force Z'].to_numpy() / 4500)
        # my_norm = np.array([my_fn(my) for my in self.data['Neck Upper Moment Y'].to_numpy()])
        nij = fz_norm + my_norm
        nij_max = max(nij)

        plt.figure(1)

        plt.plot(t,
                 fz_norm,
                 color='#ffab0f')  # (255, 171, 15)
        plt.plot(t,
                 my_norm,
                 color='#cd0532')
        plt.plot(t,
                 nij,
                 color='#0080ff')

        plt.xlabel('Time (s)')
        plt.ylabel('Nij score')
        plt.legend(['Force Z', 'Moment Y', 'Nij'])
        plt.title('Nij Components')
        plt.show()

        ais2, ais3, ais3_old = neck_AIS(nij_max)
        messagebox.showinfo('Nij', f'Nij: {nij_max:0.2f}\n'
                                   f'AIS2 Risk: {100 * ais2:0.2f}%\n'
                                   f'AIS3+ Risk: {100 * ais3:0.2f}%\n'
                                   f'OLD AIS3+ Risk: {100 * ais3_old:0.2f}%\n')

    @catch
    def femur_fn(self):
        """
        calculate femur injury risk
        :return:
        """
        # risk_r, force_r = femur_ais2(self.data['Femur Right Force X'],
        #                              self.data['Femur Right Force Y'],
        #                              self.data['Femur Right Force Z'])

        t = self.data['Display Name'].to_numpy()
        # fx = self.data['Femur Left Force X'].to_numpy()
        # fy = self.data['Femur Left Force Y'].to_numpy()
        fz = self.data['Femur Left Force Z'].to_numpy()

        t, fz = trim_arrays(fz, xdata=t, lim=self.trim)
        fz = CFC_filter(1 / 10000, fz, cfc=600)

        risk_l, force_l = femur_ais2(fz)
        # risk_l, force_l = femur_ais2(self.data['Femur Left Force X'],
        #                              self.data['Femur Left Force Y'],
        #                              self.data['Femur Left Force Z'])

        messagebox.showinfo('Femur Injury Risk',
                            f'Left Femur\n'
                            f'Force: {force_l:0.3f} kN\n'
                            f'AIS2+ Risk: {100 * risk_l:0.2f}%\n')

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
        self.series.clear()
        self.text = np.array([])
        self.cfc = 0

        plt.close()

        self.update_filenames()
        self.update_headers()

        self.file_dropdown.set('')
        self.header_dropdown.set('')
        self.xaxis_dropdown.set('')
        self.yaxis_dropdown.set('')
        self.series_dropdown.set('')
        self.header_dropdown['values'] = []
        self.xaxis_dropdown['values'] = []
        self.yaxis_dropdown['values'] = []
        self.series_dropdown['values'] = []
        self.series_fn(None)

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
        self.series_dropdown.set('')
        self.series_fn(None)

    def filter_fn(self):
        """
        CFC filter
        :return:
        """
        series = self.series_dropdown.get()
        if series and type(self.series[series]["cfc"]) is str:
            messagebox.showerror("FILTERING ERROR",
                                 "data has already been filtered and combined")
            return

        cfc = simpledialog.askinteger('CFC filtering',
                                      f'enter CFC filter type (0 is unfiltered)\n'
                                      f'{"series filter: " + str(self.series[series]["cfc"]) if series else ""}\n'
                                      f'{"UNCHANGEABLE" if series and type(self.series[series]["cfc"]) is str else ""}',
                                      minvalue=0,
                                      maxvalue=1000,
                                      initialvalue=self.cfc)
        if cfc is not None:
            self.cfc = cfc
            self.filter_var.set(
                f'Select Filter ({"CFC " if self.cfc != 0 else ""}'
                f'{self.cfc if self.cfc != 0 else "no filter"})'
            )
            if series and type(self.series[series]["cfc"]) is int:
                self.series[series]['cfc'] = cfc
            print(self.cfc)
        # else:
        #     messagebox.showerror('Series Filter Cannot Be Changed',
        #                          'please contact developer for further explanation')

    def file_fn(self, event: Event | None):
        """
        execute on file dropdown selection
        :param event:
        :return:
        """
        print(self.filenames[self.file_dropdown.get()])

    def header_fn(self, event: Event | None):
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

    def xaxis_fn(self, event: Event):
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

    def yaxis_fn(self, event: Event):
        pass

    def series_fn(self, event: Event | None):
        key = self.series_dropdown.get()
        if key:
            self.cfc = int(self.series[key]['cfc'])
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

    def style_fn(self, event: Event | None):
        key = self.series_dropdown.get()
        style = self.style_dropdown.get()
        if key:
            self.series[key]['style'] = style
        # else:
        #     self.cfc = 0
        # self.update_buttons()

    def marker_fn(self, event: Event | None):
        key = self.series_dropdown.get()
        marker = self.marker_dropdown.get()
        if key:
            self.series[key]['marker'] = marker
        # else:
        #     self.cfc = 0
        # self.update_buttons()

    def update_filenames(self):
        """
        update filenames dictionary from files set
        :return:
        """

        @enumerator
        def get_filename(file_path):
            return os.path.splitext(os.path.basename(file_path))[0]

        self.filenames = {get_filename(file): file
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
        if key:
            self.style_dropdown.set(self.series[key]['style'])
            self.marker_dropdown.set(self.series[key]['marker'])

    def main(self) -> None:
        """
        main loop
        :return:
        """
        mainloop()

    def changeseries_fn(self):
        key = self.series_dropdown.get()
        name = simpledialog.askstring('Series Name',
                                      'enter series name',
                                      initialvalue=key)
        if name:
            self.series[name] = self.series[key]
            self.series.__delitem__(key)
            self.series_dropdown['values'] = list(self.series.keys())
            self.series_dropdown.set(name)

    def xlabel_fn(self):
        name = simpledialog.askstring('X',
                                      'enter x axis label',
                                      initialvalue=self.xlabel)
        if name:
            self.xlabel = name
            self.xlabel_var.set(f'X Label {self.xlabel}')

    def ylabel_fn(self):
        name = simpledialog.askstring('Y',
                                      'enter y axis label',
                                      initialvalue=self.ylabel)
        if name:
            self.ylabel = name
            self.ylabel_var.set(f'Y Label {self.ylabel}')

    def title_fn(self):
        name = simpledialog.askstring('TITLE',
                                      'enter graph title',
                                      initialvalue=self.title)
        if name:
            self.title = name
            self.title_var.set(f'Title: {self.title}')

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
