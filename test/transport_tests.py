from unittest.mock import Mock, patch
from transport import SerialReader

def test_serial_initialization():
    with patch("transport.serial.Serial") as mock_serial:
        transport = SerialReader(port = "COM7", 
                                baudrate = 115200,
                                bytesize = "8",
                                parity = "PARITY_NONE",
                                stopbits = "STOPBITS_ONE",
                                timeout = 0.1)

        mock_serial.assert_called_once_with(
            "COM7",
            115200,
            8,
            'N',
            1,
            0.1
        )

def test_read_once():
    with patch("transport.serial.Serial") as mock_serial:
        mock_serial.return_value.read.return_value = b"\x01\x02\x03"

        transport = SerialReader("COM7")
        transport._read_once()

        assert transport.get_bytes() == b"\x01\x02\x03"

def test_read_twice():
    with patch("transport.serial.Serial") as mock_serial:
        mock_serial.return_value.read.return_value = b"\x01\x02\x03"

        transport = SerialReader("COM7")
        transport._read_once()

        mock_serial.return_value.read.return_value = b"\x01\x02\x02\x02\x03"

        transport._read_once()

        assert transport.get_bytes() == b"\x01\x02\x03"
        assert transport.get_bytes() == b"\x01\x02\x02\x02\x03"

def test_read_once_no_data():
    with patch("transport.serial.Serial") as mock_serial:
        mock_serial.return_value.read.return_value = b""

        transport = SerialReader("COM7")
        transport._read_once()

        assert transport._queue.empty()
