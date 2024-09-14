# Colmi R02 Client

A python client to connect to the Colmi R02 family of Smart Rings.

Can be used either as a command line app (via `colmi_r02_client` and `colmi_r02_util`)

Inspired by https://github.com/atc1441/ATC_RF03_Ring/


# Status

 - [x] real time heart rate and SPO2
 - [x] Step logs (still don't quite understand how the day is split up)
 - [x] Heart rate logs (periodic measurement)
 - [ ] SPO2 logs
 - [ ] "Stress" measurement
 - [ ] Sleep tracking
 - [ ] Set HR log frequency
 - [x] Set ring time

# TODO

- add more CLI functionlity
    - set hr log frequency
    - pretty print HR and steps
    - sync all data to a file or sqlite db?

# Getting started

## With the command line

If you don't know python that well, I **highly** recommend you install [pipx](https://pipx.pypa.io/stable/installation/). It's puprpose built for managing python packages intended to be used as standalone programs and it will keep your computer safe from the pitfalls of python packaging. Once install you can do

```sh
pipx install git+https://github.com/tahnok/colmi_r02_client
```

Once that is done you can look for nearby rings using

```sh
# colmi_r02_util scan
Found device(s)
                Name  | Address
--------------------------------------------
            R02_341C  |  70:CB:0D:D0:34:1C
```

Once you have your address you can use it to do things like get real time heart rate

```sh
# colmi_r02_client --address=70:CB:0D:D0:34:1C get-real-time-heart-rate
Starting reading, please wait.
[81, 81, 79, 79, 79, 79]
```

## With the library / sdk

You can use the `colmi_r02_client.client` class as a library to do your own stuff in python. See `docs/` for the documentation on that.
