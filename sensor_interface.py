import time
import threading
from tkinter import *
from tkinter.messagebox import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from read_sensors import TMP117, SHTC3, AzureIoTHub
import sensor_config as sc

class sensorGUI(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.tmp117 = None
        self.shtc3 = None
        self.stop_online = None
        self.azureuploader = None
        self.connstatus = StringVar()
        self.connstatus.set('Not Connect.')
        self.temperature = StringVar()
        self.humidity = StringVar()
        self.temp_unit = 'C'
        
        self.pack(expand = YES, fill = BOTH)
        self.master.title('Sensor Reader')
        self.master.geometry("500x320+300+200")
        self.master.resizable(False, False)

        self.frame1 = Frame(self)
        self.frame1.pack(side = 'top', padx = 5, pady = 5, fill = BOTH)
        self.connectButton = Button(self.frame1, text = 'Connect', width = 15)
        self.connectButton.bind("<Enter>", self.rolloverEnter)
        self.connectButton.bind("<Leave>", self.rolloverLeave)
        self.connectButton.bind("<ButtonRelease>", self.conn2device)
        self.connectButton.pack(side = 'left', anchor = 'nw', padx = 20, pady = 5)
        self.Labelconnstatus = Label(self.frame1, textvariable = self.connstatus, background = 'white', width = 150, highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.Labelconnstatus.pack(side = 'left', anchor = 'ne', padx = 20, pady = 10)

        self.frame2 = Frame(self)
        self.frame2.pack(side = 'top', padx = 5, pady = 5, fill = BOTH)
        self.Labelunit = Label(self.frame2, text = "Choose temperature unit:")
        self.Labelunit.pack(side = 'left', anchor = 'sw', padx = 20, pady = 20)
        unitSelections = ["Celsius", "Fahrenheit"]
        self.chosenUnit = StringVar()
        self.chosenUnit.set(unitSelections[0])
        for style in unitSelections:
            aButton = Radiobutton(self.frame2, text = style, variable = self.chosenUnit, value = style, command = self.changeUnit)
            aButton.pack(side = 'left', anchor = 'se', padx = 5, pady = 20)
        self.frame21 = Frame(self)
        self.frame21.pack(side = 'top', padx = 5, pady = 0, fill = BOTH)
        self.getTempButton = Button(self.frame21, text = 'Temperature', width = 15)
        self.getTempButton.bind("<Enter>", self.rolloverEnter)
        self.getTempButton.bind("<Leave>", self.rolloverLeave)
        self.getTempButton.bind("<ButtonRelease>", self.getTemp)
        self.getTempButton.pack(side = 'left', anchor = 'nw', padx = 20, pady = 5)
        self.Labeltemp = Label(self.frame21, textvariable = self.temperature, background = 'white', width = 150, highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.Labeltemp.pack(side = 'left', anchor = 'ne', padx = 20, pady = 10)
        self.frame22 = Frame(self)
        self.frame22.pack(side = 'top', padx = 5, pady = 0, fill = BOTH)
        self.getHumdButton = Button(self.frame22, text = 'Humidity', width = 15)
        self.getHumdButton.bind("<Enter>", self.rolloverEnter)
        self.getHumdButton.bind("<Leave>", self.rolloverLeave)
        self.getHumdButton.bind("<ButtonRelease>", self.getHumd)
        self.getHumdButton.pack(side = 'left', anchor = 'nw', padx = 20, pady = 5)
        self.Labeltemp = Label(self.frame22, textvariable = self.humidity, background = 'white', width = 150, highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.Labeltemp.pack(side = 'left', anchor = 'ne', padx = 20, pady = 10)

        self.frame3 = Frame(self)
        self.frame3.pack(side = 'top', padx = 5, pady = 5, fill = BOTH)
        self.showTempButton = Button(self.frame3, text = 'T-Curve', width = 15)
        self.showTempButton.bind("<Enter>", self.rolloverEnter)
        self.showTempButton.bind("<Leave>", self.rolloverLeave)
        self.showTempButton.bind("<ButtonRelease>", self.showCurve)
        self.showTempButton.pack(side = 'left', anchor = 'nw', padx = 20, pady = 5)        
        self.showHumdButton = Button(self.frame3, text = 'H-Curve', width = 15)
        self.showHumdButton.bind("<Enter>", self.rolloverEnter)
        self.showHumdButton.bind("<Leave>", self.rolloverLeave)
        self.showHumdButton.bind("<ButtonRelease>", self.showCurve)
        self.showHumdButton.pack(side = 'left', anchor = 'se', padx = 20, pady = 5)

        self.frame4 = Frame(self)
        self.frame4.pack(side = 'top', padx = 5, pady = 5, fill = BOTH)        
        self.showOnlineButton = Button(self.frame4, text = 'ShowOnline', width = 15)
        self.showOnlineButton.bind("<Enter>", self.rolloverEnter)
        self.showOnlineButton.bind("<Leave>", self.rolloverLeave)
        self.showOnlineButton.bind("<ButtonRelease>", self.showOnline)
        self.showOnlineButton.pack(side = 'left', anchor = 'se', padx = 20, pady = 5)
        self.stopOnlineButton = Button(self.frame4, text = 'StopOnline', width = 15)
        self.stopOnlineButton.bind("<Enter>", self.rolloverEnter)
        self.stopOnlineButton.bind("<Leave>", self.rolloverLeave)
        self.stopOnlineButton.bind("<ButtonRelease>", self.stopOnline)
        self.stopOnlineButton.pack(side = 'left', anchor = 'se', padx = 20, pady = 5)
        
    def rolloverEnter(self, event):
        event.widget.config(relief = GROOVE)

    def rolloverLeave(self, event):
        event.widget.config(relief = RAISED)

    def conn2device(self, event):
        try:
            self.tmp117 = TMP117()
            self.shtc3 = SHTC3()
            self.tmp117.set_time_lag(0b011, 0b01)  #set to 500ms
            if not self.shtc3.dev_reg():
                showwarning(title = "Warning", message = 'Fail to register the humidity sensor!')
        except:
            showwarning(title = "Warning", message = 'Fail to connect sensors!')
        self.connstatus.set('Sensors Connected.')

    def getTemp(self, event):
        if self.tmp117 == None or self.shtc3 == None:
            showwarning(title = "Warning", message = 'Please connect first!')
        else:        
            if self.temp_unit == 'C':
                self.temperature.set(self.tmp117.read_temp_c())
            if self.temp_unit == 'F':
                self.temperature.set(self.tmp117.read_temp_f())
            if self.tmp117.most_acc_limit():
                showwarning(title = "Warning", message = 'The temperature exceeds the threshold!')
            
    def getHumd(self, event):
        if self.tmp117 == None or self.shtc3 == None:
            showwarning(title = "Warning", message = 'Please connect first!')
        else:
            self.humidity.set(self.shtc3.read_data()[1])

    def changeUnit(self):
        if self.chosenUnit.get() == "Celsius":
            desiredUnit = "C"
        elif self.chosenUnit.get() == "Fahrenheit":
            desiredUnit = "F"
        self.temp_unit = desiredUnit        

    def showCurve(self, event):
        if self.tmp117 == None or self.shtc3 == None:
            showwarning(title = "Warning", message = 'Please connect first!')
        else:
            if event.widget.cget('text') == 'T-Curve':
                #canvas_curve('t', self.tmp117).mainloop()
                self.draw_curve_new('t')
            elif event.widget.cget('text') == 'H-Curve':
                #canvas_curve('h', self.shtc3).mainloop()
                self.draw_curve_new('h')

##    def draw_curve(self, data_type):
##        ax=[]
##        ay=[]
##        if data_type == 't':
##            subtitle_name = 'Temperature Real-Time Data'
##        if data_type == 'h':
##            subtitle_name = 'Humidity Real-Time Data'            
##        plt.ion()
##        plt.rcParams['figure.figsize'] = (200, 100)
##        plt.rcParams['lines.linewidth'] = 1
##        while True:
##            plt.clf()
##            plt.suptitle(subtitle_name)
##            ax.append(str(int(time.time())))
##            if data_type == 't':
##                ay.append(self.tmp117.read_temp_c())
##            if data_type == 'h':
##                ay.append(self.shtc3.read_data()[1])
##            agraphic=plt.subplot(2,1,1)
##            agraphic.set_xlabel('Timestamp')
##            if data_type == 't':
##                agraphic.set_ylabel('Temperature')
##            if data_type == 'h':
##                agraphic.set_ylabel('Humidity')
##            plt.plot(ax,ay,'g-')
##            plt.pause(1)
##        plt.ioff()
##        plt.close()

    def draw_curve_new(self, data_type):
        if self.tmp117 == None or self.shtc3 == None:
            showwarning(title = "Warning", message = 'Please connect first!')
        else:
            self.x, self.y = [], []
            fig, ax = plt.subplots()
            ax.grid()
            self.line, = ax.plot(self.x, self.y, color='k')
            self.line.set_solid_capstyle = 'round'
            self.line.set_solid_joinstyle = 'round'
            if data_type == 't':
                self.y.append(self.tmp117.read_temp_c())
                fig.suptitle('Temperature real-time data')
                ax.set(xlabel = 'Timestamp', ylabel = 'Temperature C')
            if data_type == 'h':
                self.y.append(self.shtc3.read_data()[1])
                fig.suptitle('Humidity real-time data')
                ax.set(xlabel = 'Timestamp', ylabel = 'Humidity')
            self.x.append(int(time.time()))
            ani = FuncAnimation(fig, self.updateCurve, fargs = [data_type, ax], frames = np.linspace(1,1000,1000), interval = 1000, blit = True)
            plt.show()

    def updateCurve(self, n, data_type, ax):
        self.x.append(int(time.time()))
        if data_type == 't':
            self.y.append(self.tmp117.read_temp_c())
            ax.set_ylim(min(self.y) - sc.TEMP_SHOW_SCALE, max(self.y) + sc.TEMP_SHOW_SCALE)
        if data_type == 'h':
            self.y.append(self.shtc3.read_data()[1])
            ax.set_ylim(min(self.y) - sc.HUMD_SHOW_SCALE, max(self.y) + sc.HUMD_SHOW_SCALE)
        if len(self.x) > sc.MAX_SHOWDATA_NUMBER:
            self.x.pop(0)
            self.y.pop(0)
        #print('[x]:',self.x,'\n[y]:',self.y)
        if self.x[0] == self.x[-1]:
            ax.set_xlim(self.x[0] - 1, self.x[-1], auto = True)
        else:
            ax.set_xlim(self.x[0], self.x[-1], auto = True)
        self.line.set_data(self.x, self.y)
        return self.line,

    def showOnline(self, event):
        if self.tmp117 == None or self.shtc3 == None:
            showwarning(title = "Warning", message = 'Please connect first!')
        else:        
            self.stop_online = True
            self.azure_iothub_client = AzureIoTHub()
            if askokcancel(title = 'Yes / No', message = 'Do you want to start upload data to Azure IoT Hub?'):
                showinfo('Notice', 'Please visit: https://iot-hub-data-visualization.azurewebsites.net')
                self.stop_online = False
                self.azureuploader = threading.Thread(target = self.dataUpload)
                self.azureuploader.start()

    def dataUpload(self):
        while not self.stop_online:
            temperature = self.tmp117.read_temp_c()
            humidity = self.shtc3.read_data()[1]
            #print('Temperature: ' + str(temperature) + ' | Humidity: ' + str(humidity) + ' | Time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            self.azure_iothub_client.iothub_client_telemetry_run(temperature, humidity)
            time.sleep(1)
                
    def stopOnline(self, event):
        self.stop_online = True
        self.azureuploader.join()
        showinfo('', 'Stopping upload data.')

def main():
    sensorGUI().mainloop()

if __name__ == "__main__":
    main()
