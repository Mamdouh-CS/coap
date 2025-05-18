# 🔐 Implementation and Analysis of a CoAP-Based IoT Communication System

This project demonstrates a secure Constrained Application Protocol (CoAP) communication system tailored for IoT environments. It uses token-based authentication and AES encryption to ensure basic access control and data confidentiality over UDP.

---

## 📦 Features

- Lightweight CoAP server and client built with Python 2.7
- Token-based authentication for access control
- AES (CBC mode) encryption for payload confidentiality
- Packet-level inspection with Wireshark
- Compatible with Linux/VirtualBox setups

---

## 🛠 Requirements

- Python 2.7
- Libraries:
  - `txThings`
  - `Twisted`
  - `pycryptodome`
- OS: Linux (tested on Ubuntu VM)

Install dependencies:

```bash
pip install twisted
pip install pycryptodome
```
## 🚀 How to Run Non Secure 

### 1. Start the CoAP Server

Open a terminal and run:

```bash
python2 coapserver.py
```

## 2. 📡 Run a CoAP Client

Choose a client script based on the resource you want to access:

### ✅ Access `/counter`
```bash
python2 coapclient.py
```

### ✅ Access `/well-known/core`
```bash
python2 coapclient-well.py
```

### ✅ Access `/time`
```bash
python2 coapclient_observe.py
```

## 🚀 How to Run Secure 

### 1. Start the CoAP Server

Open a terminal and run:

```bash
python2 encrypt-coapserver.py
```

### 1. Start the CoAP Client

Open a terminal and run:

```bash
python2 encrypt-coapcient.py
```

## ✅ Conclusion

This project demonstrates a lightweight, secure CoAP-based communication system tailored for IoT environments. By leveraging the `txThings` library along with Twisted and PyCrypto, the system enables efficient resource access and observation over UDP.

Key features include:
- Implementation of a CoAP server capable of handling multiple resources (`/counter`, `/time`, `.well-known/core`)
- Python-based CoAP clients for querying and observing server resources
- AES encryption and token-based authentication for payload security
- Full communication and traffic analysis using Wireshark

The system runs successfully on both Linux virtual machines, proving its suitability for constrained environments where low-power, secure communication is essential.



