#!/usr/bin/env python3

import argparse
import logging
import ldap
import sys


class LogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.DEBUG, logging.INFO)


def parseargs():
    """Process command line arguments"""
    parser = argparse.ArgumentParser(description="Change mail attribute of OpenLDAP user")
    parser.add_argument("name", help="Firstname and lastname of OpenLDAP entry")
    parser.add_argument("mail", help="New email address for user")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="generate additional debug information")
    parser.add_argument("-V", "--version", action="version", version="1.0.0")
    return parser.parse_args()


def get_logger(debug: bool = False) -> logging.Logger:
    """Retrieve logging object"""
    logger = logging.getLogger()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    h1 = logging.StreamHandler(sys.stdout)
    h1.setLevel(logging.DEBUG)
    h1.addFilter(LogFilter())

    h2 = logging.StreamHandler(sys.stderr)
    h2.setLevel(logging.WARNING)

    logger.addHandler(h1)
    logger.addHandler(h2)

    return logger


def ldap_connect() -> ldap.ldapobject.LDAPObject:
    """
    Connect to local OpenLDAP server using sasl method EXTERNAL

    This method only works if the ldap server is running on the same
    server as the script. The user that is running the script must
    have been authorized by the OpenLDAP server configuration.
    """
    url = 'ldapi:///'

    con = ldap.initialize(url)
    # Must be called before setting the connection
    con.set_option(ldap.OPT_REFERRALS, 0)
    
    # Actually establish the connection to the server
    con.sasl_external_bind_s()

    return con


def ldap_getuser(con: ldap.ldapobject.LDAPObject, name: str) -> str:
    """Search for ldap entry with a certain name and returns its dn"""
    base = 'dc=ip1'
    search_filter = "(objectClass=inetOrgPerson)"
    attr_list = ["cn"]
    ret_dn = None

    res = con.search_st(base, ldap.SCOPE_SUBTREE, search_filter, attr_list, timeout=4)
    for dn, attrs in res:
        for val in attrs["cn"]:
            #print(f"{dn}: Name={val.decode('utf-8')}")
            if name == val.decode('utf-8'):
                ret_dn = dn

    return ret_dn


def ldap_updateuser(con: ldap.ldapobject.LDAPObject, dn: str, mail_address: str):
    """
    Update ldap entry: set mail attribute

    First delete all existing values, then add the value. This is a safe way
    to perform the operation, as we don't know if this particular value already exists,
    or if there are already one or more other values in the attribute.
    """ 
    modlist_del = [(ldap.MOD_DELETE, "mail", None)]
    modlist_add = [(ldap.MOD_ADD, "mail", mail_address.encode('utf-8'))]

    try:
        con.modify_s(dn, modlist_del)
    except ldap.NO_SUCH_ATTRIBUTE:
        pass
    con.modify_s(dn, modlist_add)


def main():
    con = None
    args = parseargs()
    logger = get_logger(args.debug)

    user_name = args.name
    mail_address = args.mail

    try:
        con = ldap_connect()
        user_dn = ldap_getuser(con, user_name)
        if user_dn:
            ldap_updateuser(con, user_dn, mail_address)
        else:
            logger.warning(f"User '{user_name}' not found")
    except ldap.LDAPError as e:
        logger.error(f'{type(e)}: {e}')
        exit(1)
    finally:
        if con:
            con.unbind_ext_s()

if __name__ == '__main__':
    main()
