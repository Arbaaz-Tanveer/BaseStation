import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import math
import socket
import threading
from PIL import Image, ImageTk
from base_station_UI import *
from communication import WiFiHandler, RefBoxHandler

class BaseStationLogic:
    def __init__(self, ui):
        self.ui = ui
        self.robots = ui.robots
        self.opponents = ui.opponents
        self.global_world = ui.global_world
        self.connection_status = False

        # RefBox connection using RefBoxHandler
        self.refbox_handler = RefBoxHandler(
            "127.0.0.1", 28097, 
            self.handle_refbox_message, 
            self.handle_refbox_disconnect
        )
        self.refbox_messages = []  # store all messages from RefBox here

    def connect_to_robots(self):
        self.connection_status = True
        for robot in self.robots:
            if robot.connect():
                if hasattr(robot, "status_label"):
                    robot.status_label.config(text="Connected", fg="green")
                print("Connected to robot", robot.name)
            else:
                if hasattr(robot, "status_label"):
                    robot.status_label.config(text="Disconnected", fg="red")
                print("Failed to connect to robot", robot.name)

    def disconnect_from_robots(self):
        self.connection_status = False
        for robot in self.robots:
            robot.disconnect()
            if hasattr(robot, "status_label"):
                robot.status_label.config(text="Disconnected", fg="red")
        print("Disconnected from robots")

    def connect_to_refbox(self, ip="127.0.0.1", port=28097):
        if not self.refbox_handler.connected:
            self.refbox_handler.connect()
            self.ui.update_refbox_status(connected=True)

    def handle_refbox_message(self, message):
        self.ui.log_refbox_message(message)

    def handle_refbox_disconnect(self):
        self.ui.update_refbox_status(connected=False)  # Update UI to "Disconnected"
        print("RefBox disconnected.")

    def stop_refbox(self):
        self.refbox_handler.stop()
        self.ui.update_refbox_status(connected=False)

    def update_world_state(self):
        # Update global world map from robots
        self.global_world.update_from_robots(self.robots)
        # Redraw field
        self.ui.redraw_field()
        # Keep scheduling next update
        self.ui.root.after(100, self.update_world_state)

    def parse_message(self, message):
        print(message)

def main():
    root = tk.Tk()
    app = BaseStationUI(root)
    logic = BaseStationLogic(app)
    app.logic = logic
    logic.connect_to_robots()
    logic.update_world_state()
    root.mainloop()

if __name__ == "__main__":
    main()