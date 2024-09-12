from hypothesis import given
import hypothesis.strategies as st

from colmi_r02_client.packet import make_packet, crc


@given(command=st.integers(min_value=0, max_value=255), sub_data=st.binary(max_size=14))
def test_make_packet_works_on_valid_data(command, sub_data):
    packet = make_packet(command, sub_data)

    assert len(packet) == 16
    assert packet[-1] == crc(packet[0:15])
