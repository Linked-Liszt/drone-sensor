import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import matplotlib.patches as mpatches
import socket
import multiprocessing 

#HOST = "192.168.1.98"
#PORT = 8000


HOST = "127.0.0.1"
PORT = 80

NUM_POINTS = 20

CO2_ATM = [400]*NUM_POINTS #define atmospheric gas levels
CO_ATM = [0]*NUM_POINTS

CO2_1 = [600]*NUM_POINTS #placeholder levels for co2
CO2_2 = [1000]*NUM_POINTS

CO_CATCONV = [100]*NUM_POINTS #co for car w/ catalytic converter
CO_INJ = [1000]*NUM_POINTS #co for car w/ fuel injector


#need to add co2 levels for estimated people in room

#Global Vars For Thread Communication:
co_g = 0.0
co2_g = 0.0
connection_g = True

def openNewConnection(server_socket):
    while True:
        try:
            server_socket.listen(5) #server_socket defined in main below
            print("Server Listening")
            server_socket.settimeout(10)
            (client_socket, address) = server_socket.accept()
            print("Connection found!")
            return client_socket
        except socket.error:
            print("Connection Not Found. Refreshing.")


def getData(proc_conn):
    co = 0.0
    co2 = 0.0
    connection = False
    proc_conn.send({"co":co, "co2":co2, "conn":connection})
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    print("Socket Bound Sucessfully")
    client_socket = openNewConnection(server_socket)
    while True:
        try:
            skt_raw = client_socket.recv(1024)
            if not skt_raw:
                raise Exception("socket disconnect")
            
            skt_str = skt_raw.decode("utf-8")
            co = float(skt_str.split("\t")[0].strip())
            co2 = float(skt_str.split("\t")[1].strip())
            connection = True

        except ValueError:
            connection=False
            print("Packet Messed Up: Unable to Convert!")

        except (socket.error, Exception):
            connection=False
            print("Socket error or disconnect!")
            client_socket.close()
            client_socket = openNewConnection(server_socket)
        
        proc_conn.send({"co":co, "co2":co2, "conn":connection})

def logToFile(co, co2, timestamp):
    with open("sensorData.log", "a+") as log_file:
        log_file.write("Timestamp: {0},\t CO: {1:.2f},\t CO2: {2:.2f} \n".format(str(timestamp), co, co2))

def drawChart(i, co_list, co2_list, times, proc_conn):
    global co_g
    global co2_g
    global connection_g
    # Get Data
    timestamp = dt.datetime.now().strftime('%H:%M:%S')
    while proc_conn.poll():
        data = proc_conn.recv()
        co_g = data["co"]
        co2_g = data["co2"]
        connection_g = data["conn"] #Can use this to signal disconnect on graph

    logToFile(co_g, co2_g, timestamp)

    # Add to lists
    times.append(timestamp)
    co_list.append(co_g)
    co2_list.append(co2_g)

    # Limit x and y lists to NUM_POINTS items
    co_list = co_list[-NUM_POINTS:]
    co2_list = co2_list[-NUM_POINTS:]
    times = times[-NUM_POINTS:]


    # Update plots
    co_plot.clear()
    co_live = co_plot.plot(times, co_list, label="CO Live", color="blue")
    co_atm_line = co_plot.plot(CO_ATM, label="Atm CO", color="green") #line for atm CO
    co_cat_line = co_plot.plot(CO_CATCONV,label="Cat Conv",color="yellow")
    co_inj_line = co_plot.plot(CO_INJ,label="Fuel Injector",color="red")
    #CO Legend
    co_plot.legend(handles=[co_inj_line[0],co_cat_line[0],co_atm_line[0],co_live[0]], loc=2) #legend for atmospheric level CO


    co2_plot.clear()
    co2_live = co2_plot.plot(times, co2_list, label="Live Co2", color="blue")
    co2_atm_line = co2_plot.plot(CO2_ATM, label="Atm Co2", color="green") #line for atm co2
    co2_line1 = co2_plot.plot(CO2_1,label="Co2 600", color="yellow")
    co2_line2 = co2_plot.plot(CO2_2,label="Co2 1000", color = "red")

    #CO Formatting
    co_plot.set_title("CO Readings")
    co_plot.set_ylabel("PPM")

    #CO2 Formatting
    co2_plot.set_title("CO2 Readings")
    co2_plot.set_ylabel("PPM")
    co2_plot.set_xlabel("Time Stamp")
    co2_plot.tick_params(axis='x', rotation=45)
    #Legend
    co2_plot.legend(handles=[co2_line2[0],co2_line1[0],co2_atm_line[0],co2_live[0]], loc=2) #legend for CO2_2
        #Add new lines to legend in handles, use same syntax



if __name__ == "__main__":
    # Create figure for plotting
    fig, (co_plot, co2_plot) = plt.subplots(2, 1, sharex=True)
    co_list_g = []
    co2_list_g = []
    times_g = []

    # Set up data collection worker
    pipe_receive, pipe_send = multiprocessing.Pipe(duplex=False)
    data_proc = multiprocessing.Process(target=getData, args=[pipe_send])
    data_proc.start()

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, drawChart, fargs=(co_list_g, co2_list_g, times_g, pipe_receive), interval=1000)
    plt.show()
