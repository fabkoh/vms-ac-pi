import os
import logging
import netifaces

def restart_eth0():
    """Restart the eth0 network interface."""
    os.system("sudo ifconfig eth0 down")
    os.system("sudo ifconfig eth0 up")

def get_default_gateway():
    """Use netifaces module to get the default gateway."""
    try:
        return netifaces.gateways().get("default", {}).get(netifaces.AF_INET, [None])[0]
    except Exception as e:
        logging.exception("Error getting default gateway: %s", e)
        return None
