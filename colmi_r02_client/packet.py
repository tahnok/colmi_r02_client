def make_packet(command: int, sub_data: bytearray | None = None) -> bytearray:
    """
    Make a well formed packet from a command key and optional sub data.

    That means ensuring it's 16 bytes long and the last byte is a valid CRC.

    command must be between 0 and 255 (inclusive)
    sub_data must have a len between 0 and 14
    """
    assert 0 <= command <= 255
    packet = bytearray(16)
    packet[0] = command

    if sub_data:
        assert len(sub_data) <= 14
        for i in range(len(sub_data)):
            packet[i + 1] = sub_data[i]

    packet[-1] = crc(packet)

    return packet


def crc(packet: bytearray) -> int:
    return sum(packet) & 255
