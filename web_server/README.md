# Paralel Web Server

A web server is actually a simple TCP server which parse HTTP requests and send a reply back. You can see the detail of HTTP in this document [https://tools.ietf.org/html/rfc1945](https://tools.ietf.org/html/rfc1945)

However, a good web server is expected to be able to handle multiple clients at the same time. In order to achieve that, you need to make it either asynchronous, multi-threaded, or multi-processed.

## Getting Started

### Prerequisites

- Python 3.6+

### Usage

Jalankan script dengan perintah

```
$ python server.py
```

Jika script berjalan dengan sukses, akan muncul informasi berikut

```
[*] Started listening on port {PORT}
```

Lakukan `GET` request ke `/execute/<delay dalam ms>` atau `POST` request ke `/execute` dengan parameter `duration` pada body request yang bertipe `x-www-form-urlencoded`
