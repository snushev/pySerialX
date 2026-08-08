import queue
import threading
import time

import serial

class ArduinoController:

    def __init__(self, port, baud_rate=9600, on_error=None):
        """Initialize the ArduinoController with the specified serial port and baud rate."""
        self.arduino = serial.Serial(port, baud_rate, timeout=1)
        self.messages = queue.Queue()
        self.on_error = on_error
        self._stop_thread = False
        self.thread = threading.Thread(target=self._read_serial, daemon=True)
        self.thread.start()

    def _read_serial(self):
        """Read lines from the Arduino in a separate thread and put them in a queue."""
        while not self._stop_thread:
            try:
                if self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8', errors='ignore').rstrip()
                    if line:
                        self.messages.put(line)
            except Exception as e:
                if self.on_error:
                    self.on_error(e)
                break
            time.sleep(0.01)

    def read_line(self, timeout=0):
        """Return a line if available, otherwise None"""
        try:
            return self.messages.get(timeout=timeout)
        except queue.Empty:
            return None

    def send_line(self, cmd):
        """Send a command to the Arduino."""
        self.arduino.write((cmd + '\n').encode('utf-8'))
        time.sleep(0.05)

    def close(self):
        """Stop the reading thread and close the serial connection."""
        self._stop_thread = True
        self.thread.join(timeout=1)
        self.arduino.close()