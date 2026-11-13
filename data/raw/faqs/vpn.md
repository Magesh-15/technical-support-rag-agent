Source: internal-faq/vpn
Title: How to set up a VPN on the router

Some routers include a VPN server (OpenVPN or PPTP) so you can reach your home network from outside.
1. Log in to the admin page (tplinkwifi.net or 192.168.0.1).
2. Open Advanced > VPN Server and choose OpenVPN or PPTP VPN.
3. Enable the server, generate a certificate for OpenVPN, then export the configuration file.
4. Install the OpenVPN client on your phone or laptop and import the file.
5. Connect. If it fails, check that your provider gives you a public IP (not CGNAT) and use Dynamic DNS if your IP changes.
Models without a VPN menu do not support running a VPN. Check the product page for your model.
