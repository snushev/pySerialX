import conftest # Non use (only for tests for import the libraries)
import sys, os
from dotenv import load_dotenv
from pySerialX.serialx_python_integration import SerialX

# IN CONFTEST
load_dotenv()

# Seleziona la porta e il baudrate in base all'OS
if sys.platform.startswith("win"):
    port = os.getenv("WINDOWS_SERIAL_PORT", "COM3")
    baud = int(os.getenv("WINDOWS_SERIAL_BAUD", 9600))
elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
    port = os.getenv("LINUX_SERIAL_PORT", "/dev/ttyACM0")
    baud = int(os.getenv("LINUX_SERIAL_BAUD", 9600))
else:
    raise OSError(f"Sistema operativo non supportato: {sys.platform}")

print(f"Uso della porta: {port} con baudrate: {baud}")


# Create SerialX instance
SerialXInstance = SerialX(port)

print("=== SERIALX TEST START ===")

# Auth
print("Checking authentication...")
if SerialXInstance.isAuthActive():
    SerialXInstance.auth("secure")
    print("AUTH OK")
else:
    print("AUTH NOT REQUIRED")

# =========================
# READ FUNCTION
# =========================

def read_all_values():
    values = {}

    values["led_state"]   = SerialXInstance.get("bool", "led_state")
    print("BOOL OK")

    values["temperature"] = SerialXInstance.get("int", "temperature")
    print("INT OK")

    values["humidity"]    = SerialXInstance.get("float", "humidity")
    print("FLOAT OK")

    values["text"]        = SerialXInstance.get("string", "text")
    print("STRING OK")

    values["char_var"]    = SerialXInstance.get("char", "char_var")
    print("CHAR OK")

    values["char_array"]  = SerialXInstance.get("charstring", "char_array")
    print("CHARSTRING OK")

    values["byte_var"]    = SerialXInstance.get("uint8_t", "byte_var")
    print("UINT8_t OK")

    values["word_var"]    = SerialXInstance.get("uint16_t", "word_var")
    print("UINT16_t OK")

    values["dword_var"]   = SerialXInstance.get("uint32_t", "dword_var")
    print("UINT32_t OK")

    values["long_var"]    = SerialXInstance.get("long", "long_var")
    print("LONG OK")

    values["double_var"]  = SerialXInstance.get("double", "double_var")
    print("DOUBLE OK")

    return values


def print_values(title, values):
    print(f"\n=== {title} ===")
    for k, v in values.items():
        print(f"{k:<15}: {v}")


# =========================
# INITIAL GET
# =========================

print("\n--- INITIAL READ ---")
initial_values = read_all_values()
print_values("INITIAL VALUES", initial_values)

# =========================
# SET TESTS
# =========================

print("\n--- EXECUTING SETS ---")

expected_values = {}

SerialXInstance.set("bool", "led_state", 1)
expected_values["led_state"] = 1
print("SET BOOL OK")

SerialXInstance.set("int", "temperature", 30)
expected_values["temperature"] = 30
print("SET INT OK")

SerialXInstance.set("float", "humidity", 55.5)
expected_values["humidity"] = 55.5
print("SET FLOAT OK")

SerialXInstance.set("string", "text", "SerialX_Test")
expected_values["text"] = "SerialX_Test"
print("SET STRING OK")

SerialXInstance.set("char", "char_var", "Z")
expected_values["char_var"] = "Z"
print("SET CHAR OK")

SerialXInstance.set("charstring", "char_array", "TEST_ARRAY")
expected_values["char_array"] = "TEST_ARRAY"
print("SET CHARARRAY OK")

SerialXInstance.set("uint8_t", "byte_var", 200)
expected_values["byte_var"] = 200
print("SET UINT8 OK")

SerialXInstance.set("uint16_t", "word_var", 60000)
expected_values["word_var"] = 60000
print("SET UINT16 OK")

SerialXInstance.set("uint32_t", "dword_var", 4000000000)
expected_values["dword_var"] = 4000000000
print("SET UINT32 OK")

SerialXInstance.set("long", "long_var", -123456)
expected_values["long_var"] = -123456
print("SET LONG OK")

SerialXInstance.set("double", "double_var", 1234.56)
expected_values["double_var"] = 1234.56
print("SET DOUBLE OK")

# =========================
# FINAL GET
# =========================

print("\n--- FINAL READ ---")
final_values = read_all_values()
print_values("FINAL VALUES", final_values)

# =========================
# VIRTUAL VARIABLE
# =========================

virtual_var_value = SerialXInstance.personalized_command("givsensor_read")
print("gvi sensor_read : " + str(virtual_var_value))

# =========================
# VERIFICATION
# =========================

print("\n=== VERIFICATION ===")

all_ok = True

for var, expected in expected_values.items():

    received = final_values.get(var)

    if isinstance(expected, float):
        ok = abs(float(received) - expected) < 0.001
    else:
        ok = str(received) == str(expected)

    if ok:
        print(f"[OK]   {var:<12} expected={expected} received={received}")
    else:
        print(f"[FAIL] {var:<12} expected={expected} received={received}")
        all_ok = False

# =========================
# RESULT
# =========================

print("\n=== RESULT ===")

if all_ok:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")

print("=== SERIALX TEST END ===")