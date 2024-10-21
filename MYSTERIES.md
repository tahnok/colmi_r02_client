Some notes on packets and behaviours I don't fully understand yet.

---

I got this one when doing a real time heart rate reading, but I don't think this usually happens

bytearray(b's\x0c\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x94'

I got another 's' packet while asking for battery level

bytearray(b's\x0c+\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xab')


This one showed up when asking for steps for a day

bytearray(b's\x0cd\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe4')

---

Set-time always includes

bytearray(b'/\xf1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 ')

and I don't know what it means
