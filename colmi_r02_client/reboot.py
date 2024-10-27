from colmi_r02_client.packet import make_packet

CMD_REBOOT = 8  # 0x08

REBOOT_PACKET = make_packet(CMD_REBOOT, bytearray(b"\x01"))
