"""Creates the 27 FAQ documents in data/raw/faqs/.  Run:  python make_faqs.py
Menu names vary slightly between router models, so the steps are written generically."""
import os

LOGIN = "log in to the admin page (tplinkwifi.net or 192.168.0.1)"

FAQS = {
"reset_router": ("How to reset the router to factory settings",
"""Use a factory reset when you forgot the admin password or the router is misconfigured.
1. Keep the router powered on.
2. Find the small RESET button (a pinhole) on the back panel.
3. Press and hold it with a pin or paperclip for 8-10 seconds until all LEDs blink and turn off.
4. Release the button and wait 2 minutes for the router to reboot.
5. Connect to the default Wi-Fi name printed on the router label and log in at 192.168.0.1 or tplinkwifi.net.
Warning: a reset erases all custom settings, including Wi-Fi name, password, and port forwarding rules."""),
"wifi_keeps_disconnecting": ("Wi-Fi keeps disconnecting",
"""Common causes are interference, outdated firmware, or a weak signal.
1. Restart the router: unplug power for 30 seconds, then plug it back in.
2. Move the router to a central, open location away from microwaves, cordless phones, and thick walls.
3. Change the Wi-Fi channel: log in to the admin page, go to Wireless settings, and choose channel 1, 6, or 11 for 2.4 GHz.
4. Update the router firmware (see the firmware update guide).
5. Forget the Wi-Fi network on your device and reconnect.
6. If only one device disconnects, update that device's Wi-Fi driver.
If the problem continues, contact support."""),
"forgot_wifi_password": ("Forgot the Wi-Fi password",
"""Option 1: Check the label on the bottom or back of the router. It shows the default Wi-Fi name and password (PIN or Wireless Password).
Option 2: If the password was changed, connect a computer to the router with an Ethernet cable, log in to the admin page (192.168.0.1 or tplinkwifi.net), and open Wireless settings to view or change the password.
Option 3: If you also forgot the admin password, factory reset the router and use the default password from the label."""),
"forgot_admin_password": ("Forgot the router admin (login) password",
"""The admin password is different from the Wi-Fi password.
1. Try the default credentials on the router label, or admin / admin on older models.
2. Some models let you create the admin password on first login. If you set one and forgot it, there is no recovery option.
3. The only fix is a factory reset using the RESET button (hold 8-10 seconds). All settings will be erased."""),
"led_indicators": ("What do the router LED lights mean",
"""Power LED: solid on means powered; off means no power.
Internet LED: solid white or green means connected to the internet; solid orange or red means the router has no internet connection; off means no WAN cable detected.
Wireless LED (2.4 GHz / 5 GHz): solid on means the Wi-Fi band is active; off means it is disabled.
Blinking LED: data is being transferred, or the router is starting up.
If the Internet LED is orange or red: check the cable from the modem, restart both modem and router, and confirm the internet service is active."""),
"no_internet_access": ("Connected to Wi-Fi but no internet access",
"""1. Check the Internet LED on the router. If it is orange or red, the router cannot reach the internet.
2. Power-cycle: turn off the modem and router, wait 30 seconds, turn on the modem first, wait 2 minutes, then turn on the router.
3. Check that the cable from the modem is firmly plugged into the router's WAN (Internet) port.
4. Log in to the admin page and check the Internet connection type (Dynamic IP, PPPoE, Static IP). PPPoE needs the username and password from your internet provider.
5. Try connecting a device directly to the modem. If it also has no internet, contact your internet provider."""),
"slow_wifi_speed": ("Slow Wi-Fi speed",
"""1. Test your speed near the router, then in the problem room, to see whether it is a signal issue.
2. Use the 5 GHz band for faster speeds at close range. The 2.4 GHz band has longer range but is slower.
3. Disconnect devices you are not using.
4. Change the Wi-Fi channel to reduce interference from neighbors.
5. Update the router firmware.
6. Restart the router regularly.
7. If the speed is slow on wired connections too, the issue is likely with your internet provider."""),
"firmware_update": ("How to update the router firmware",
"""1. Log in to the admin page (192.168.0.1 or tplinkwifi.net).
2. Go to Advanced > System > Firmware Update.
3. Click Check for Updates if the router is online, then click Update.
4. For a manual update, download the firmware file for your exact model and hardware version from the manufacturer's website, then use Local Upgrade to select the file.
Warning: do not power off the router during the update. It takes about 3-5 minutes and the router will reboot."""),
"change_wifi_name_password": ("How to change the Wi-Fi name and password",
"""1. Log in to the admin page (192.168.0.1 or tplinkwifi.net).
2. Go to Wireless settings (Basic > Wireless or Advanced > Wireless).
3. Enter a new Network Name (SSID) and a new Password. Use WPA2 or WPA3 security with a password of at least 12 characters.
4. Click Save. All devices will disconnect and must reconnect with the new password."""),
"port_forwarding": ("How to set up port forwarding",
"""1. Give the target device a fixed IP using Address Reservation (Advanced > Network > DHCP Server).
2. Go to Advanced > NAT Forwarding > Virtual Servers and click Add.
3. Enter a service name, the external port, the internal IP of the device, and the internal port.
4. Choose the protocol (TCP, UDP, or All) and save.
5. Test using an online port-check tool. If it fails, check that the device firewall allows the port and that your provider does not use CGNAT."""),
"cannot_access_admin_page": ("Cannot open the router admin page",
"""1. Confirm your device is connected to the router (Wi-Fi or Ethernet).
2. Type the address in the browser address bar, not a search bar: tplinkwifi.net or 192.168.0.1 (some models use 192.168.1.1).
3. Clear the browser cache or try another browser or a private window.
4. Disable any VPN or proxy.
5. Set your computer to obtain an IP address automatically.
6. If it still fails, factory reset the router and try again."""),
"guest_network": ("How to set up a guest network",
"""1. Log in to the admin page.
2. Go to Basic > Guest Network.
3. Turn on the guest network for 2.4 GHz and/or 5 GHz.
4. Set a name and password for the guest network.
5. Leave 'Allow guests to see each other' and 'Allow guests to access my local network' disabled for better security.
6. Click Save. Visitors can then use the internet without knowing your main Wi-Fi password."""),
# ---------------- 15 new documents ----------------
"parental_controls": ("How to set up parental controls",
f"""Parental controls limit when and where your children can go online.
1. {LOGIN.capitalize()}.
2. Open Parental Controls (Basic or Advanced menu).
3. Click Add and choose your child's device from the list of connected devices.
4. Set the allowed internet time (for example 8 AM to 9 PM) and a daily limit.
5. Add website keywords or categories to block, such as adult content or social media.
6. Click Save. Time limits only work when the router clock is set correctly (System > Time Settings)."""),
"qos": ("How to set up QoS (prioritize devices)",
f"""QoS (Quality of Service) gives important devices more bandwidth, for example a work laptop during video calls.
1. {LOGIN.capitalize()}.
2. Open Advanced > QoS (or Game Accelerator / Device Priority on some models).
3. Turn QoS on and enter your real internet speed (run a speed test first).
4. Choose the device and set its priority to High, or pick a category such as Gaming or Streaming.
5. Click Save. Other devices may become slower when the line is busy."""),
"vpn": ("How to set up a VPN on the router",
f"""Some routers include a VPN server (OpenVPN or PPTP) so you can reach your home network from outside.
1. {LOGIN.capitalize()}.
2. Open Advanced > VPN Server and choose OpenVPN or PPTP VPN.
3. Enable the server, generate a certificate for OpenVPN, then export the configuration file.
4. Install the OpenVPN client on your phone or laptop and import the file.
5. Connect. If it fails, check that your provider gives you a public IP (not CGNAT) and use Dynamic DNS if your IP changes.
Models without a VPN menu do not support running a VPN. Check the product page for your model."""),
"ipv6": ("How to enable IPv6",
f"""1. {LOGIN.capitalize()}.
2. Open Advanced > IPv6.
3. Turn IPv6 on and choose the connection type your provider uses: Dynamic IP (SLAAC/DHCPv6), Static IP, PPPoE, or 6to4 Tunnel. If you are not sure, try Dynamic IP first.
4. Click Save, then test at an IPv6 test website.
If IPv6 does not work, ask your internet provider whether your plan supports IPv6."""),
"wps": ("How to use WPS to connect a device",
"""WPS lets you connect a device without typing the Wi-Fi password.
1. Press the WPS button on the router once (usually on the side or back).
2. Within 2 minutes, press the WPS button on the device or choose WPS in its Wi-Fi settings.
3. Wait until the WPS LED stops blinking. The device is now connected.
For better security, many people turn WPS off: log in to the admin page, open Wireless > WPS, and disable it. The WPS PIN method is less secure than the button."""),
"dns_settings": ("How to change DNS settings",
f"""Changing DNS can fix websites that will not load and may speed up browsing.
1. {LOGIN.capitalize()}.
2. Go to Advanced > Network > Internet.
3. Turn off 'Get automatically from ISP' for DNS, or choose Use the Following DNS Addresses.
4. Enter a primary DNS such as 8.8.8.8 (Google) and a secondary such as 8.8.4.4, or use 1.1.1.1 (Cloudflare).
5. Click Save and restart your devices. You can also set DNS on a single device in its network settings."""),
"bridge_ap_mode": ("How to use the router as an access point (bridge mode)",
f"""Use Access Point mode to turn a second router into a Wi-Fi extender that is connected by cable to your main router.
1. Connect your computer to the second router and {LOGIN}.
2. Open Operation Mode and select Access Point. The router reboots.
3. Connect an Ethernet cable from a LAN port of the main router to the Internet/WAN port of the second router.
4. Set the Wi-Fi name and password. Use the same name and password as the main router for easy roaming, but a different channel.
5. DHCP is turned off in this mode, so the main router assigns the IP addresses."""),
"mac_filtering": ("How to block a device with MAC filtering",
f"""You can block unknown devices from your network with Wireless MAC Filtering or Access Control.
1. Find the device's MAC address in its Wi-Fi settings, or in the router's client list.
2. {LOGIN.capitalize()}.
3. Open Security > Access Control (or Wireless > MAC Filtering).
4. Choose Blacklist to block listed devices, or Whitelist to allow only listed devices.
5. Add the MAC address and click Save.
Tip: if you see a device you do not know, also change your Wi-Fi password."""),
"static_ip_dhcp": ("How to reserve an IP address for a device (DHCP reservation)",
f"""Address Reservation always gives the same IP address to a device such as a printer, camera, or game server.
1. {LOGIN.capitalize()}.
2. Open Advanced > Network > DHCP Server.
3. In Address Reservation click Add.
4. Select the device from the list (or enter its MAC address) and type the IP address you want, for example 192.168.0.50.
5. Save and reconnect the device. Choose an address outside the normal DHCP range if possible."""),
"band_steering": ("2.4 GHz vs 5 GHz: which band should I use",
"""2.4 GHz: longer range and better through walls, but slower and more crowded with interference from microwaves, Bluetooth, and neighbors. Best for smart-home devices and far rooms.
5 GHz: faster and less crowded, but shorter range and weaker through walls. Best for streaming, gaming, and video calls when you are in the same room or nearby.
Tip: give the two bands different names (for example Home-2G and Home-5G) so you can choose, or use Smart Connect to let the router pick the best band automatically."""),
"router_overheating": ("Router is hot or overheating",
"""A warm router is normal, but a very hot router can cause disconnects and slow speed.
1. Place it in an open area with air space around it. Do not put it in a closed cabinet or on top of other hot devices.
2. Keep it out of direct sunlight and away from heaters.
3. Clean dust from the vents with a dry cloth or compressed air while it is unplugged.
4. Use only the original power adapter.
5. Stand it upright if it is designed for vertical placement.
If it stays very hot or smells like burning, unplug it and contact support or replace the router."""),
"router_wont_turn_on": ("Router will not turn on",
"""1. Check that the power outlet works by plugging in another device.
2. Make sure the power adapter is firmly plugged into the router and the wall. Use the original adapter (correct voltage).
3. If there is a power button, make sure it is pressed in.
4. Try a different outlet or power strip.
5. Look at the adapter and cable for damage.
6. If no LED lights up with a working outlet and a good adapter, the router or adapter may be faulty. Contact support or the seller about a warranty replacement."""),
"backup_restore": ("How to back up and restore router settings",
f"""Back up your settings before a firmware update or factory reset.
1. {LOGIN.capitalize()}.
2. Go to Advanced > System > Backup & Restore.
3. Click Backup to download a configuration file to your computer.
4. To restore later, click Browse, choose the saved file, and click Restore. The router reboots.
Only restore a backup made on the same router model and the same firmware version."""),
"no_5ghz_network": ("5 GHz Wi-Fi network is not showing up",
"""1. Check that your device supports 5 GHz. Older phones and laptops only support 2.4 GHz.
2. Check that the router is dual-band, and that the 5 GHz LED is on. If it is off, the band is disabled.
3. Log in to the admin page, open Wireless settings, and make sure 5 GHz is enabled.
4. Move closer to the router, because 5 GHz has shorter range.
5. Some channels (DFS channels) can take a few minutes to start. Try a fixed channel such as 36 or 44.
6. Restart the router and refresh the network list on your device."""),
"wifi_security": ("How to secure your Wi-Fi network",
"""1. Change the default admin password and the default Wi-Fi password.
2. Use WPA3 or WPA2-AES security. Never use WEP or an open network.
3. Choose a long Wi-Fi password (12 or more characters).
4. Turn off WPS and remote management unless you need them.
5. Keep the firmware updated.
6. Put visitors and smart-home devices on the guest network.
7. Check the list of connected devices regularly and remove any you do not recognize."""),
}

os.makedirs("data/raw/faqs", exist_ok=True)
for name, (title, body) in FAQS.items():
    with open(f"data/raw/faqs/{name}.md", "w", encoding="utf-8") as f:
        f.write(f"Source: internal-faq/{name}\nTitle: {title}\n\n{body}\n")
print(f"Created {len(FAQS)} FAQ files")
