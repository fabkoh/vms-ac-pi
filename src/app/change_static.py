import logging
import os

from src import healthcheck
from src.app.utils.network_utils import restart_eth0, get_default_gateway

CONF_FILE = "/etc/dhcpcd.conf"
DEFAULT_DNS = "8.8.8.8"

def change_static_ip(ip_address, routers, dns=DEFAULT_DNS):
    """Change the static IP address configuration."""
    try:
        with open(CONF_FILE, "r") as file:
            data = file.readlines()

        eth_index = None
        for i, line in enumerate(data):
            if "interface eth0" in line:
                eth_index = i
                break

        if eth_index is not None:
            data[eth_index + 1] = f"static ip_address={ip_address}/24\n"
            data[eth_index + 2] = f"static routers={routers}\n"
            data[eth_index + 3] = f"static domain_name_servers={dns}\n"

            with open(CONF_FILE, "w") as file:
                file.writelines(data)

            restart_eth0()
        else:
            logging.warning("No eth0 interface found in configuration.")
    except Exception as ex:
        logging.exception("IP changing error: %s", ex)

def change_dhcp():
    """Change the configuration to use DHCP."""
    try:
        with open(CONF_FILE, "r") as f:
            data = f.readlines()

        eth_index = None
        for i, line in enumerate(data):
            if line.startswith("interface eth0"):
                eth_index = i
                break

        if eth_index is not None:
            for i in range(4):
                data[eth_index + i] = "# " + data[eth_index + i]

            with open(CONF_FILE, "w") as f:
                f.writelines(data)

            restart_eth0()
        else:
            logging.warning("No eth0 interface found in configuration.")
    except Exception as e:
        logging.exception("Error changing to DHCP: %s", e)

def change_ip(static, ip_address):
    """Change IP address configuration.

    Args:
        static (bool): Whether to use a static IP.
        ip_address (str): The new IP address to use.
    """
    try:
        curr_static = healthcheck.check_ip_static()
        curr_ip = healthcheck.get_host_ip()

        if static and (curr_static != static or ip_address != curr_ip):
            change_static_ip(ip_address, get_default_gateway(), DEFAULT_DNS)
        elif not static and curr_static != static:
            change_dhcp()
    except Exception as e:
        logging.exception("Error changing IP: %s", e)

if __name__ == "__main__":
    os.system("sudo ifconfig eth0 up")
