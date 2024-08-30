from colmi_r02_client.set_time import byte_to_bcd

import pytest

@pytest.mark.parametrize("normal, bcd", [(0, 0), (10, 0b00010000), (99, 0b10011001)])
def test_byte_to_bcd(normal, bcd):
    assert bcd == byte_to_bcd(normal)

@pytest.mark.parametrize("bad", [-1, 100, 1000])
def test_byte_to_bcd_bad(bad):
    with pytest.raises(AssertionError):
        byte_to_bcd(bad)
