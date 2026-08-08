import pySerialX.serialx_communication
import pySerialX.version


class SerialX:
    ERROR_PREFIX = "E|"

    def __init__(self, port, baud_rate=9600):
        self.communication = pySerialX.serialx_communication.SerialXCommunication(port, baud_rate, True)
        """self.supported_types = [
            "bool", "int", "float", "string", "char", "charstring",
            "uint8_t", "uint16_t", "uint32_t", "long", "double"
        ]"""
        self._type_map = {
            "bool": lambda x: str(x).strip().lower() in ("true", "1", "yes"),
            "int": int, "float": float, "string": str, "char": str,
            "charstring": str, "uint8_t": int, "uint16_t": int,
            "uint32_t": int, "long": int, "double": float,
        }

    def _read_response(self, command, timeout=5):
        """Invia il comando, legge la risposta, gestisce errori/timeout in un solo posto."""
        line = self.communication.send_line(command)

        if line is None:
            raise TimeoutError("Nessuna risposta da Arduino")

        line = line.strip()
        if line.startswith(self.ERROR_PREFIX):
            raise ValueError(f"Errore da Arduino: {line[len(self.ERROR_PREFIX):].strip()}")

        return line

    def isAuthActive(self):
        line = self._read_response("isAuthActive")
        return self._type_map["bool"](line)

    def auth(self, accessKey):
        line = self._read_response(f"accessKey {accessKey}")
        return self._type_map["bool"](line)

    def get_version(self) -> str:
        return pySerialX.version.__version__

    def info(self):
        return self.communication.send_line("info")

    def help(self):
        return self.communication.send_line("help")

    def get(self, tipo: str, name: str, isVirtual: bool = False):
        tipo = tipo.lower()
        if not name or not name.strip():
            raise ValueError("Nome non valido")

        cmd = f"getvirtual {tipo} {name}" if isVirtual else f"get {tipo} {name}"

        try:
            line = self._read_response(cmd)
            return self._type_map[tipo](line)
        except ValueError as e:
            raise ValueError(f"Impossibile convertire '{line}' nel tipo '{tipo}'") from e

    def set(self, tipo: str, name: str, value):
        tipo = tipo.lower()
        if not name or not name.strip():
            raise ValueError("Nome non valido")

        cmd = f"set {tipo} {name} {value}"
        try:
            line = self._read_response(cmd)
        except ValueError as e:
            raise ValueError(f"Impossibile convertire '{line}' nel tipo '{tipo}'") from e

    def run(self, name: str):
        if not name or not name.strip():
            raise ValueError("Nome non valido")
        return self._read_response(f"run {name}")

    def personalized_command(self, command: str, jit=True):
        if not command or not command.strip():
            raise ValueError("Comando non valido")
        if jit:
            return self._read_response(command)
        return self.communication.send_raw(command)

    def close(self):
        self.communication.close()