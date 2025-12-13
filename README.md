# VICTOR 86C/86D Multimeter Parser

A Python library for parsing and decoding the serial data stream from **VICTOR 86C** and **VICTOR 86D** digital multimeters (DMM).

This library was developed through reverse engineering of the 14-byte data packets sent by the multimeter's USB/Serial interface, enabling developers to easily integrate the multimeter into Python applications for data logging, automation, and monitoring.

## 🚀 Features

* **Real-time Decoding:** Parses raw 14-byte hex packets into readable floating-point values.
* **Unit & Mode Detection:** Automatically detects measurement units (V, A, Ohm, Hz, etc.) and modes (AC, DC, HOLD, MAX/MIN).
* **Symbol Support:** Identifies special symbols like `AUTO`, `DIODE`, `BEEP`, and prefixes (`m`, `u`, `k`, `M`).
* **Bargraph Data:** Extracts the analog bargraph value (0-42).
* **Lightweight:** Pure Python implementation with no heavy dependencies.

## 📦 Installation

To install the library locally, navigate to the project directory (where `setup.py` is located) and run:

```bash
pip install .
```

## 🛠️ Usage

### Basic Usage

You can easily decode a raw packet and get the final measurement value and unit string.

```python
from victor86c_parser import Victor86cParser

# Example raw packet (14 bytes) received from serial
# Represents: 0.017 A (DC)
raw_packet = b'+0017 \\x001\\x00\\x00@\\x00'

# Create a parser instance
parser = Victor86cParser(raw_packet)

# Get the decoded value
value = parser.get_measurement_value()
unit = parser.get_unit_string()
mode = parser.get_mode()

print(f"Reading: {value} {unit} ({mode})")
# Output: Reading: 0.017 A (DC)
```

### Serial Monitor Example

Here is a simple example of how to read from the serial port and decode data in real-time using `pyserial`.

```python
import serial
from victor86c_parser import Victor86cParser

# Configure your serial port (Windows: 'COMx', Linux: '/dev/ttyUSBx')
PORT = 'COM11'
BAUD = 2400

ser = serial.Serial(PORT, BAUD, timeout=0.5)

print(f"Listening on {PORT}...")

try:
    while True:
        # Read a full line (14 bytes data + 2 bytes CR/LF)
        line = ser.readline()
        
        # Extract the 14 data bytes (ignore CR/LF)
        if len(line) >= 14:
            data_packet = line[:14]
            
            parser = Victor86cParser(data_packet)
            
            val = parser.get_measurement_value()
            unit = parser.get_unit_string()
            mode = parser.get_mode()
            
            print(f"Measured: {val} {unit} ({mode})")

except KeyboardInterrupt:
    print("Stopped.")
    ser.close()
```

## 📚 Protocol Documentation

The VICTOR 86C sends a **14-byte** packet followed by `\\r\\n` (CRLF) continuously (approx. 2-3 times/sec).

| Byte Index | Bit | Description | Example Values |
| :---: | :---: | :--- | :--- |
| **0** | `0` | Sign (+/-) | `+`, `-` |
| **1-4** | `1-4` | Numeric Digits | `0017` (ASCII) |
| **5** | `5` | Space/Separator | ` ` (Space) |
| **6** | `6` | Decimal Point | `1` (/1000), `2` (/100), `4` (/10) |
| **7** | `7` | Measurement Mode | `1` (DC), `)` (AC), `!` (AUTO), `#` (AUTO HOLD) |
| **8** | `8` | MAX/MIN Indicator | `\\x20` (MAX), `\\x10` (MIN) |
| **9** | `9` | Prefix/Symbol | `\\x10` (M), `@` (m), `\\x80` (u), `\\x01` (k) |
| **10** | `10` | Base Unit | `2` (C), `1` (F), `@` (A), `\\x80` (V), ` ` (Ohms) |
| **11** | `11` | Analog Bargraph | Integer value (0-42) |
| **12-13** | - | Terminators | `\\r\\n` |

## 🤝 Contributing

Contributions are welcome! If you have a VICTOR 86C/86D and find a symbol or mode that isn't mapped correctly, please open an issue or submit a pull request with the raw hex data and the expected display value.

## 📄 License

This project is licensed under the MIT License.
