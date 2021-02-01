# ldap-test
This simple example script uses the 'ldap' Python3 module to access a local OpenLDAP server using the sasl EXTERNAL mechanism. 

There is also an 'ldap3' module. Here are the differences between both modules in a nutshell:

### Module 'ldap'
- Maintained by OpenLDAP developers
- Wrapper of OpenLDAP client libraries
- Use it if you only access OpenLDAP servers

### Module 'ldap3'
- RFC conform
- More pythonic
- Use it to access all sorts of LDAP servers

### Function endings in module 'ldap'
In the 'ldap' module, there are different sets of function calls you need to be aware of. E.g. there is a function called 'search', but also a function called 'search_s', 'search_st', 'search_ext' and 'search_ext_s'. Which one do you use?

- Functions ending with '_s' are synchronous, meaning that when the function returns you have the result. If the result set is very large, it could be that this kind of function blocks your program too long. But if you don't transfer too much data and the OpenLDAP server is not too busy, this is the function that you usually want to call.
- Functions ending with '_st' are synchronous function calls that have an additional timeout parameter.
- Functions ending with _ext' allow you to specify additional parameters like a sizelimit.
