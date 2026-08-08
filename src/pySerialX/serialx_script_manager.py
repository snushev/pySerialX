from pySerialX.serialx_communication import SerialXCommunication
from pySerialX.models.serialx_data import SerialXData

class SerialXScriptManager:
    def __init__(self, controller: SerialXCommunication):
        self.controller = controller

    def send(self, serialx_data: SerialXData):
        for jit_command in serialx_data.jit:
            self.controller.send_line(jit_command)
            print(f"<<< {jit_command}")
            line = self.controller.communication.read_line(timeout=0.1)
            while line:
                print(line)
                line = self.controller.communication.read_line(timeout=0.1)

    def interpreter_script(script):
        serialXData = SerialXData(scriptVersion="", commands=[])

        for line in script.splitlines():
            line = line.strip()

            if not line or line.startswith("//") or line.startswith("#!"):
                continue

            # Metadata
            if line.startswith("@"):
                if line.startswith("@v") and not serialXData.scriptVersion:
                    serialXData.scriptVersion = line[2:]
                elif not serialXData.scriptName:
                    serialXData.scriptName = line[1:]
                continue
        return serialXData
