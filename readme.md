SyncStream allows you to easily configure multiple LED-interfaces. Originally started for digitally addressable
LED strips, reachable as UDP interfaces.

## Server infrastructure

The server cluster works with animations, the interfacing udpserver, and obviously the controllers that translate
the UDP packages to the LED strips. The last systems open a UDP port to the network, to which the udpserver
connects to. The configuration for this interface is held on the system running the udpserver, and should match
the what the physical interface hosts.

Then the udpserver reads out this configuration. The configuration can hold multiple physical interfaces, and for
each interface animations are able to send seperate animations. It is also possible to collect multiple interfaces
(not limited to physical interfaces) into a virtual interface, and send data to this virtual interface. An animation
now only sees that virtual interface as the interface it can write to.

In the case multiple root-level interfaces are configured, the udpserver starts a socket for each of them. This
allows multiple animations to be ran on multiple sets of LED strips
