The UDPServer connects animations, which talk over by the server provided unix sockets, with physical interfaces, which talk over IP/UDP. It allows for multiple physical interfaces to be collected inside of virtual interfaces, which again can be nested. The system also allows for multiple virtual interfaces to be the root interfaces, so the network can be segmented.

# Configuration files

The configuration of the interfaces can be set via a configuration file, for example:

```yaml
interfaces:
  - name: virt-1
    interface-type: virtual             # Interfaces can either by of type virtual or physical
    children:                           # Virtual interfaces must have children
      - name: phys-1                    # phys and virt as names are not required, currently primarily indicative.
        interface-type: physical
        ip: "127.0.0.1"
        port: 1337
        amount-leds: 10
        max-udp-size: 320
        max-brightness: 15
      - name: phys-2
        interface-type: physical
        ip: "127.0.0.1"
        port: 1338
        amount-leds: 10
        max-udp-size: 320
        max-brightness: 15
  - name: virt-2                        # This is the second root virtual interface.
    interface-type: virtual
    children:
      - name: phys-3
        interface-type: physical
        ip: "127.0.0.1"
        port: 1339
        amount-leds: 10
        max-udp-size: 320
        max-brightness: 15

sockets:
  dir: /run/syncstream                  # Animations and control talk via unix sockets to the server, and these sockets
                                        # need to reside somewhere.
```

Given the names of the example configuration file, the following sockets will be created:

- /run/syncstream/virt-1
- /run/syncstream/virt-2

# Control packages

Animations can talk to the server using the unix-stream socket. The messages must contain a valid magic, then the length of the message and finally the message type / command.

## Get info command (0)

The get info command, indicated by the integer 0, will collect data such as the total amount of leds in the root interface and sends it back in a yaml-compatible format.

## Send buffer command (1)
The send info command, indicated by the integer 1, will unpack the fully send framebuffer and propagate it to the virtual interface, which again propagates it further to their childs and so on. 
