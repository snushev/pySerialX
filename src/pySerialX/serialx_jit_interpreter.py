"""JIT Interpreter for SerialX communication with Arduino.
This module provides a Just-In-Time (JIT) interpreter for translating SerialX commands into SerialX_JIT commands.
This module include two decoders for help and info commands, which are used to decode the output of the Arduino device."""

from dataclasses import dataclass, field


@dataclass
class TypeInfo:
    code: str
    enabled: bool = False


@dataclass
class InfoData:
    device_name: str
    software_name: str
    serialx_version: str
    serialx_jit_version: str
    type_supported: dict[str, "TypeInfo"]


class SerialXInterpreter:
    JIT_COMMAND_CODES = {
        "accessKey": "akey",
        "help": "h",
        "info": "i",
        "get": "g",
        "set": "s",
        "run": "r",
    }

    JIT_TYPE_CODES = {
        "bool": "b",
        "int": "i",
        "float": "f",
        "string": "s",
        "char": "c",
        "charstring": "C",
        "uint8_t": "u",
        "uint16_t": "w",
        "uint32_t": "d",
        "long": "l",
        "double": "D",
    }

    # JIT Interpretation
    @staticmethod
    def encode(cmd: str) -> str | None:
        """Traduce un comando utente in comando JIT."""
        parts = cmd.split()
        if not parts:
            return None
        base = parts[0]
        if base == "accessKey":
            return f"{SerialXInterpreter.JIT_COMMAND_CODES['accessKey']} {parts[1]}"
        elif base in ("help", "info"):
            return SerialXInterpreter.JIT_COMMAND_CODES[base]
        elif base == "set":
            return SerialXInterpreter._encode_set(parts)
        elif base == "get":
            return SerialXInterpreter._encode_get(parts)
        elif base == "getvirtual":
            return SerialXInterpreter._encode_get(parts, virtual=True)
        elif base == "run":
            return (
                f"{SerialXInterpreter.JIT_COMMAND_CODES['run']} {' '.join(parts[1:])}"
            )
        elif base in SerialXInterpreter.JIT_COMMAND_CODES:
            return SerialXInterpreter.JIT_COMMAND_CODES[base]
        return cmd

    @staticmethod
    def _encode_set(parts: list[str]) -> str | None:
        if len(parts) < 4:
            print("Comando set incompleto: set <type> <name> <value>")
            return None

        tipo = parts[1]
        name = parts[2]
        valore = parts[3] if len(parts) == 4 else " ".join(str(x) for x in parts[3:])

        type_code = SerialXInterpreter.JIT_TYPE_CODES.get(tipo)
        if not type_code:
            print(f"Tipo non valido: {tipo}")
            return None

        try:
            if tipo == "bool":
                if isinstance(valore, bool):
                    valore = 1 if valore else 0
                else:
                    v = str(valore).strip().lower()
                    if v in ("true", "1"):
                        valore = 1
                    elif v in ("false", "0"):
                        valore = 0
                    else:
                        raise ValueError("Bool deve essere true/false o 0/1")
        except ValueError as e:
            print(f"Valore non valido per {name}: {valore} ({e})")
            return None

        return (
            f"{SerialXInterpreter.JIT_COMMAND_CODES['set']}{type_code} {name} {valore}"
        )

    @staticmethod
    def _encode_get(parts: list[str], virtual: bool = False) -> str | None:
        if len(parts) < 3:
            print("Comando get incompleto: get <type> <name>")
            return None

        tipo = parts[1]
        name = " ".join(parts[2:])

        type_code = SerialXInterpreter.JIT_TYPE_CODES.get(tipo)
        if not type_code:
            print(f"Tipo non valido: {tipo}")
            return None

        if virtual:
            return f"g{type_code}v{name}"
        return f"{SerialXInterpreter.JIT_COMMAND_CODES['get']}{type_code} {name}"

    @staticmethod
    def decode_info(text: str) -> InfoData:
        """
        text: stringa multiriga con la risposta completa al comando 'info'.
        Legge le righe di risposta al comando 'info' e le struttura.
        Formato atteso (da confermare col firmware):
            <deviceName>
            <softwareName>
            SerialX v<versione>
            JIT v<versione>
            <stringa tipi supportati, es. "bsifDLc">
        """
        serialx_version = ""
        jit_version = ""
        device_name = ""
        software_name = ""
        supported_str = ""

        lines = iter(text.splitlines())
        line = next(lines, None)

        if line and line.startswith("Device:"):
            device_name = line[7:].strip()
            line = next(lines, None)

        if line and line.startswith("Software:"):
            software_name = line[9:].strip()
            line = next(lines, None)

        if line and line.startswith("SerialX Version:"):
            serialx_version = line[16:].strip()
            line = next(lines, None)

        if line and line.startswith("JIT Version:"):
            jit_version = line[12:].strip()
            line = next(lines, None)

        if line:
            supported_str = line.strip()

        types = {
            name: TypeInfo(code)
            for name, code in SerialXInterpreter.JIT_TYPE_CODES.items()
        }
        for t in types.values():
            t.enabled = t.code in supported_str

        return InfoData(
            device_name=device_name,
            software_name=software_name,
            serialx_version=serialx_version,
            serialx_jit_version=jit_version,
            type_supported=types,
        )

    @staticmethod
    def decode_help(text: str):
        """
        text: stringa multiriga con la risposta completa al comando 'help'.
        Legge le righe di risposta al comando 'help' e le struttura.
        """
        variabili = []
        funzioni = []

        for line in text.splitlines():
            if not line:
                continue

            if line.startswith("E:"):
                raise ValueError(f"Errore da Arduino: {line[2:].strip()}")

            if len(line) < 3:
                continue

            # Funzione
            if line.startswith("r"):
                funzioni.append(line[2:].strip())
                continue

            # Variabile
            tipo = line[0]
            flag = line[1]
            parts = line[2:].split()

            if tipo not in SerialXInterpreter.JIT_TYPE_CODES.values() or len(parts) < 1:
                variabili.append({"raw": line, "unrecognized": True})
                continue

            tipo_nome = next(
                name
                for name, code in SerialXInterpreter.JIT_TYPE_CODES.items()
                if code == tipo
            )
            # name, value = parts[0], parts[1]
            name = parts[0]

            variabili.append(
                {
                    "name": name,
                    "type": tipo_nome,
                    # "value": value,
                    "can_set": flag == "x",
                    "unrecognized": False,
                }
            )

        return {"variables": variabili, "functions": funzioni}


"""
            # JIT Interpretation
                @staticmethod
                def encode(cmd: str) -> str | None:
                    parts = cmd.split()
                    if not parts:
                        return None
                    base = parts[0]
                    jit_command = None
            
                    # --- ACCESS KEY ---
                    if base == "accessKey":
                        akey = parts[1]
                        jit_command = f"{self.JIT_COMMAND_CODES['accessKey']} {akey}"
            
                    # --- HELP / INFO ---
                    elif base in ("help", "info"):
                        jit_command = self.JIT_COMMAND_CODES[base]
            
                    # --- SET ---
                    elif base == "set":
                        tipo = parts[1]
                        name = parts[2]
                        valore = " ".join(parts[3:])
            
                        type_code = self.JIT_TYPE_CODES.get(tipo)
                        if not type_code:
                            print(f"Tipo non valido: {tipo}")
                            return None
            
                        try:
                            # conversione valori
                            if tipo == "bool":
                                v = valore.lower()
                                if v == "true":
                                    valore = 1
                                elif v == "false":
                                    valore = 0
                                elif v in ("1", "0"):
                                    valore = int(v)
                                else:
                                    raise ValueError("Bool deve essere true/false o 0/1")
            
                            jit_command = f"{self.JIT_COMMAND_CODES['set']}{type_code} {name} {valore}"
            
                        except ValueError as e:
                            print(f"Valore non valido per {name}: {valore} ({e})")
                            return None
            
                    # --- GET ---
                    elif base == "get":
                        tipo = parts[1]
                        name = " ".join(parts[2:])
            
                        type_code = self.JIT_TYPE_CODES.get(tipo)
                        if not type_code:
                            print(f"Tipo non valido: {tipo}")
                            return None
            
                        jit_command = f"{self.JIT_COMMAND_CODES['get']}{type_code} {name}"
            
                    # --- GET VIRTUAL ---
                    elif base == "getvirtual":
                        tipo = parts[1]
                        name = " ".join(parts[2:])
            
                        type_code = self.JIT_TYPE_CODES.get(tipo)
                        if not type_code:
                            print(f"Tipo non valido: {tipo}")
                            return None
            
                        jit_command = f"g{type_code}v{name}"
            
                    # --- RUN ---
                    elif base == "run":
                        name = " ".join(parts[1:])
                        jit_command = f"{self.JIT_COMMAND_CODES['run']} {name}"
            
                    # --- FALLBACK ---
                    elif base in self.JIT_COMMAND_CODES:
                        jit_command = self.JIT_COMMAND_CODES[base]
            
                    else:
                        jit_command = cmd
            
                    if jit_command:
                        print("JIT Command:", jit_command)
            
                    return jit_command
                    """

