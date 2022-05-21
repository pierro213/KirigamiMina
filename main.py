##############
## Script listens to serial port and writes contents into a file
##############
## requires pySerial to be installed
#import serial

#serial_port = 'COM9';
#baud_rate = 9600; #In arduino, Serial.begin(baud_rate)
#write_to_file_path = "output.txt";

#output_file = open(write_to_file_path, "w+");
#ser = serial.Serial(serial_port, baud_rate)
#while True:
#    line = ser.readline();
#    line = line.decode("utf-8") #ser.readline returns a binary, convert to string
#    print(line);
#    output_file.write(line);

#!/usr/bin/env python

from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import struct
import pandas as pd
import tkinter as tk


#root = tk.Tk()
#canvas1 = tk.Canvas(root, width = 300, height = 300) # create the canvas
#canvas1.pack()

#entry1 = tk.Entry (root) # create the entry box
#canvas1.create_window(150, 100, window=entry1)


#def insert_number():  # add a function/command to be called by the button (i.e., button1 below)
#    global x1  # add 'global' before the variable x1, so that you can use that variable outside of the command/function if ever needed
#    x1 = str(entry1.get())  # store the data input by the user as a variable x1
#    root.destroy()



class serialPlot:
    def __init__(self, serialPort = 'COM7', serialBaud = 38400, plotLength = 10, dataNumBytes = 4, x1 = 'kirigami'):
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.rawData = bytearray(dataNumBytes)
        self.data = collections.deque([0] * (plotLength*10), maxlen=plotLength*10)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        self.filename = x1
        self.csvData = []

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText):
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)     # the first reading will be erroneous
        self.previousTimer = currentTimer
        #timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
        value,  = struct.unpack('f', self.rawData)    # use 'h' for a 2 byte integer
        self.data.append(value)    # we get the latest data point and append it to our array
        lines.set_data(np.linspace(0, self.plotMaxLength, self.plotMaxLength*10), self.data)
        lineValueText.set_text('[' + lineLabel + '] = ' + str(round(value)) + ' Ohms ')
        self.csvData.append(self.data[-1])

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True
            print(self.rawData)

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        df = pd.DataFrame(self.csvData)
        df.to_csv('C:/Users/pierk/PycharmProjects/kirigamiRecording/' + self.filename + '.csv')


def main():
    # portName = 'COM5'     # for windows users
    portName = 'COM7'
    baudRate = 38400
    maxPlotLength = 10
    dataNumBytes = 4        # number of bytes of 1 data point
    #button1 = tk.Button(root, text='What is the name of the CSV file? ', command=insert_number, bg='green',
    #                    fg='white')  # button to call the 'insert_number' command above
    #canvas1.create_window(150, 140, window=button1)

    #root.mainloop()
    x1 = input('Name of the CSV file?')
    s = serialPlot(portName, baudRate, maxPlotLength, dataNumBytes, x1)   # initializes all required variables
    s.readSerialStart()                                               # starts background thread

    # plotting starts below
    pltInterval = 100    # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = maxPlotLength
    ymin = 400
    ymax = 550
    fig = plt.figure(figsize=(6.4,4.8))
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title('Kirigami resistivity')
    ax.set_xlabel("time (s)")
    ax.set_ylabel("Resistivity (Ohms)")

    lineLabel = 'Resistivity'
    timeText = ax.text(0.5, 0.95, '', transform=ax.transAxes)
    lines = ax.plot([], [], label=lineLabel)[0]
    lineValueText = ax.text(0.5, 0.9, '', transform=ax.transAxes)
    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(lines, lineValueText, lineLabel, timeText),
                                   interval=pltInterval)    # fargs has to be a tuple

    plt.legend(loc="upper left")
    plt.show()

    s.close()


if __name__ == '__main__':
    main()

