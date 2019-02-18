"""
Utility module.
"""

from . import params


# The Base58 digits.
BASE58_DIGITS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_encode(address_bignum):
    """
    This function converts an address in bignum formatting
    to a string in base58, it doesn't prepend the '1' prefix
    for the network address.

    :param address_bignum: The address in numeric format
    :returns: The string in base58
    """
    basedigits = []
    while address_bignum > 0:
        address_bignum, rem = divmod(address_bignum, 58)
        basedigits.insert(0, BASE58_DIGITS[rem])
    return ''.join(basedigits)

def base58_decode(address):
    """
    This function converts an base58 string to a numeric
    format.

    :param address: The base58 string
    :returns: The numeric value decoded
    """
    address_bignum = 0
    for char in address:
        address_bignum *= 58
        digit = BASE58_DIGITS.index(char)
        address_bignum += digit
    return address_bignum

def services_to_text(services):
    """
    Converts the services field into a textual
    representation.
    """
    service_strings = []
    named_services = []
    # Converts every service we have a name for that this endpoint offers.
    for service_name, flag_mask in params.SERVICES.items():
        if services & flag_mask:
            service_strings.append(service_name)
            named_services.append(flag_mask)

    # For those services that don't have a name, show them anyway.
    for service_mask_shift in range(32):
        service_mask = 1 << service_mask_shift
        if (not service_mask in named_services) and (services & service_mask):
            service_strings.append(f"NODE_UNKNOWN_{service_mask_shift}")
    return service_strings
