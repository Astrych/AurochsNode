# Aurochs Node

Pinkcoin experimental full node implementation in Python.

The main goal of the project is to create tools to test, prototype and experiment with new consensus mechanisms in easy and fast way. The main and official next version of Pinkcoin full node will be based on Bitcoin code and is located in [PinkNext repository](https://github.com/PinkNextDev/PinkNext).

### **This is work-in-progress, not finsihed yet!**

## What is currently working:

- Pinkcoin node messaging protocol.

## Work in progress:

1. Secure messaging protocol implementation
2. Refactoring

## Things to do next:

1. Writing tests
2. Paralelisation of concurent connections
3. Saving downloaded data (blockchian) in a database
4. Consensus mechanism implementation
5. ...

Initial inspiration and code based on: https://github.com/perone/protocoin

Tests
=====

How to run:
```sh
py.test tests
```
