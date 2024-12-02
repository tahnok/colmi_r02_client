# Colmi R02 Client

Open source python client to read your data from the Colmi R02 family of Smart Rings. 100% open source, 100% offline.

[Source code on GitHub](https://github.com/tahnok/colmi_r02_client)

## What is the Colmi R02?

<img src="https://cdn.tahnok.ca/u/banner_colmi_r02.png" alt="picture of the colmi r02 smart ring in shiny black. The electronics can be seen through the epoxy inside the ring" width="100%"/>

It's a cheap (as in $20) "smart ring" / fitness wearable that includes the following sensors:

 - Accelerometer
    - step tracking
    - sleep tracking
    - gestures (maybe...?)
 - Heart Rate (HR)
 - Blood Oxygen (SPO2)

I found out about the ring from atc1441 and his work on [ATC_RF03](https://github.com/atc1441/ATC_RF03_Ring/) and the 
[Hackaday coverage](https://hackaday.com/2024/06/16/new-part-day-a-hackable-smart-ring/)

Got questions or ideas?

 - [Send me an email](mailto:tahnok+colmir02@gmail.com) 
 - [open an issue](https://github.com/tahnok/colmi_r02_client/issues/new)
 - [join the discord](https://discord.gg/K4wvDqDZvn)

Are you hiring? [Send me an email](mailto:tahnok+colmir02@gmail.com)

## Compatibility

The following rings are fully compatible:

 - Colmi R02
 - Colmi R06
 - Colmi R10

The rule of thumb is that if the listing suggests you use the QRing app, the ring is compatible with this client.

## How to buy

You can get it on [here on AliExpress](https://www.aliexpress.com/item/1005006631448993.html). If that link is dead try searching for "COLMI R02", I got mine from "Colmi official store". It cost me $CAD 22 shipped.

## Reverse engineering status

 - [x] Real time heart rate and SPO2
 - [x] Step logs (still don't quite understand how the day is split up)
 - [x] Heart rate logs (aka periodic measurement)
 - [x] Set ring time
 - [x] Set HR log frequency
 - [ ] SPO2 logs
 - [ ] Sleep tracking
 - [ ] "Stress" measurement

## Planned Feature

 - add more CLI functionality
 - pretty print HR and steps
 - sync all data to a file or SQLite db
 - simple web interface

## Getting started

### Using the command line

If you don't know python that well, I **highly** recommend you install [pipx](https://pipx.pypa.io/stable/installation/). It's purpose built for managing python packages intended to be used as standalone programs and it will keep your computer safe from the pitfalls of python packaging. Once installed you can do

```sh
pipx install git+https://github.com/tahnok/colmi_r02_client
```

Once that is done you can look for nearby rings using

```sh
colmi_r02_util scan
```

```
Found device(s)
                Name  | Address
--------------------------------------------
            R02_341C  |  70:CB:0D:D0:34:1C
```

Once you have your address you can use it to do things like get real time heart rate

```sh
colmi_r02_client --address=70:CB:0D:D0:34:1C get-real-time heart-rate
```

```
Starting reading, please wait.
[81, 81, 79, 79, 79, 79]
```

You can also sync the data from your ring to sqlite

```sh
colmi_r02_client --address=3A:08:6A:6F:EB:EC sync
```

```
Writing to /home/wes/src/colmi_r02_client/ring_data.sqlite
Syncing from 2024-12-01 01:43:04.723232+00:00 to 2024-12-01 02:03:20.150315+00:00
Done
```

The database schema is available [here](https://github.com/tahnok/colmi_r02_client/blob/main/tests/database_schema.sql)

The most up to date and comprehensive help for the command line can be found running

```sh
colmi_r02_client --help
```

```
Usage: colmi_r02_client [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --record / --no-record  Write all received packets to a file
  --address TEXT          Bluetooth address
  --name TEXT             Bluetooth name of the device, slower but will work
                          on macOS
  --help                  Show this message and exit.

Commands:
  get-heart-rate-log           Get heart rate for given date
  get-heart-rate-log-settings  Get heart rate log settings
  get-real-time-heart-rate     Get real time heart rate.
  get-steps                    Get step data
  info                         Get device info and battery level
  raw                          Send the ring a raw command
  reboot                       Reboot the ring
  set-heart-rate-log-settings  Get heart rate log settings
  set-time                     Set the time on the ring, required if you...
  sync                         Sync all data from the ring to a sqlite...
```

### With the library / SDK

You can use the `colmi_r02_client.client` class as a library to do your own stuff in python. I've tried to write a lot of docstrings, which are visible on [the docs site](https://tahnok.github.io/colmi_r02_client/)

## Communication Protocol Details

I've kept a lab notebook style stream of consciousness notes on https://notes.tahnok.ca/, starting with [2024-07-07 Smart Ring Hacking](https://notes.tahnok.ca/blog/2024-07-07+Smart+Ring+Hacking) and eventually getting put under one folder. That's the best source for all the raw stuff.

At a high level though, you can talk to and read from the ring using BLE. There's no binding or security keys required to get started. (that's kind of bad, but the range on the ring is really tiny and I'm not too worried about someone getting my steps or heart rate information. Up to you).

The ring has a BLE GATT service with the UUID `6E40FFF0-B5A3-F393-E0A9-E50E24DCCA9E`. It has two important characteristics:

 1. RX: `6E400002-B5A3-F393-E0A9-E50E24DCCA9E`, which you write to
 2. TX: `6E400003-B5A3-F393-E0A9-E50E24DCCA9E`, which you can "subscribe" to and is where the ring responds to packets you have sent.

This closely resembles the [Nordic UART Service](https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/libraries/bluetooth_services/services/nus.html) and UART/Serial communications in general.

### Packet structure

The ring communicates in 16 byte packets for both sending and receiving. The first byte of the packet is always a command/tag/type. For example, the packet you send to ask for the battery level starts with `0x03` and the response packet also starts with `0x03`.

The last byte of the packet is always a checksum/crc. This value is calculated by summing up the other 15 bytes in the packet and taking the result modulo 255. See `colmi_r02_client.packet.checksum`

The middle 14 bytes are the "subdata" or payload data. Some requests (like `colmi_r02_client.set_time.set_time_packet`) include additional data. Almost all responses use the subdata to return the data you asked for.

Some requests result in multiple responses that you have to consider together to get the data. `colmi_r02_client.steps.SportDetailParser` is an example of this behaviour.

If you want to know the actual packet structure for a given feature's request or response, take a look at the source code for that feature. I've tried to make it pretty easy to follow even if you don't know python very well. There are also some tests that you can refer to for validated request/response pairs and human readable interpretations of that data.

Got questions or ideas? [Send me an email](mailto:tahnok+colmir02@gmail.com) or [open an issue](https://github.com/tahnok/colmi_r02_client/issues/new)

## Other links

 - https://github.com/Puxtril/colmi-docs
 - gadgetbridge (open source android client for many smart devices) support [PR](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/3896)
