import pySerialX.core.arduino_controller
from pySerialX.serialx_jit_interpreter import SerialXInterpreter

class SerialXCommunication:
    """Management the comunication with Arduino with JIT Interpreter and type checking"""

    ERROR_PREFIX = "E|"

    def _read_all_lines(self, timeout=1) -> str:
        """Read all lines from the Arduino until a timeout occurs and return them as a single string."""
        lines = []
        while True:
            line = self.communication.read_line(timeout=timeout)
            if not line:
                break
                
            # Controlla se la riga inizia con il prefisso di errore
            if line.startswith(self.ERROR_PREFIX):
                # Puoi sollevare un'eccezione personalizzata o standard
                raise RuntimeError(f"Errore ricevuto da Arduino: {line}")
                
            lines.append(line)
        return "\n".join(lines)

    def __init__(self, port, baud_rate=9600, jit=True):
        """Initialize the SerialXCommunication with the specified serial port and baud rate."""
        try:
            self.communication = pySerialX.core.arduino_controller.ArduinoController(port, baud_rate)
            print(f"Connected to {port} at {baud_rate} baud")
        except Exception as e:
            print(f"Error during connection to {port}: {e}")
            raise

        self.jit = jit

        # Request device info to get supported types and other details
        self.communication.send_line("i")
        self.info = SerialXInterpreter.decode_info(self._read_all_lines())
        self._print_info(self.info)
        self.type_supported = {
            t.code for t in self.info.type_supported.values() if t.enabled
        }

    def send_line(self, line):
        """Send a command line to the Arduino and handle the response."""
        if self.jit:
            jit_command = SerialXInterpreter.encode(line)
            if not jit_command:
                print("Comando non riconosciuto o errore nella traduzione JIT")
                return None
            line = jit_command

        if not line:
            return None

        # Check type support dor set/get commands
        if len(line) >= 2 and line[0] in ("s", "g") and line[1] not in self.type_supported:
            raise TypeError(f"Type not supported by device: {line[1]}")

        self.communication.send_line(line)

        if line[0] == "h":
            result = SerialXInterpreter.decode_help(self._read_all_lines())
            self._print_help(result, use_values=False)
            return result

        elif line[0] == "i" and not line.startswith("is"): # Exclude "is" for "isAuthActive"
            self.info = SerialXInterpreter.decode_info(self._read_all_lines())
            self._print_info(self.info)
            return self.info

        else:
            data = self.communication.read_line(timeout=1)
            if data is None:
                raise TimeoutError("Timeout: Nessuna risposta da Arduino")
            elif data.startswith(self.ERROR_PREFIX):
                raise RuntimeError(f"Errore da Arduino: {data[len(self.ERROR_PREFIX):].strip()}")
            print(f"Arduino <<< {data}")
            return data

    def _print_help(self, result, use_values=False):
        print(
            "Available Commands:",
            "\nset <type> <name> <value>",
            "\nget <type> <name>",
            "\nrun <name_script>"
        )

        print("\nVariables available:")
        if use_values:
            print("Name       | Type  | Value     | CanSet ")
            print("-----------|-------|-----------|--------")
        else:
            print("Name       | Type  | CanSet ")
            print("-----------|-------|--------")

        for v in result["variables"]:
            if v.get("unrecognized"):
                print(f"Line not recognized: {v['raw']}")
                continue
            if use_values:
                print(f"{v['name']:10} | {v['type']:5} | {v['value']:9} | {v['can_set']}")
            else:
                print(f"{v['name']:10} | {v['type']:5} | {v['can_set']}")

        print("\nFunzioni disponibili:")
        print("Name")
        print("-----------")
        for f in result["functions"]:
            print(f)

    def _print_info(self, info):
        print(f"\nDevice: {info.device_name}")
        print(f"Software: {info.software_name}")
        print(f"SerialX v{info.serialx_version} | JIT v{info.serialx_jit_version}")
        print("\nSupported Types: " + "".join(f"{t.code}" for t in info.type_supported.values() if t.enabled))
        for name, t in info.type_supported.items():
            if t.enabled:
                print(f"  {name} ({t.code})")

    def close(self):
        self.communication.chiudi()