Source: internal-faq/port_forwarding
Title: How to set up port forwarding

1. Give the target device a fixed IP using Address Reservation (Advanced > Network > DHCP Server).
2. Go to Advanced > NAT Forwarding > Virtual Servers and click Add.
3. Enter a service name, the external port, the internal IP of the device, and the internal port.
4. Choose the protocol (TCP, UDP, or All) and save.
5. Test using an online port-check tool. If it fails, check that the device firewall allows the port and that your provider does not use CGNAT.
