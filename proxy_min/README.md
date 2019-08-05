# Proxy Minimalist

Proxy server itu apa sih? Nah proxy server itu bisa dibilang kayak server penengah gitu yang menerima request dari client yang akan mengakses resource dari luar (misal buka page google, atau yang lainnya). Proxy server ini punya banyak fungsi, seperti mengenkapsulasi host didalamnya dan bisa digunakan untuk logging, caching, security, dan sebagainya.

## Getting Started

### Prerequisites

- Python 3.6+

### Usage

Jalankan script dengan perintah

```
$ python proxy.py
```

Jika script berjalan dengan sukses, akan muncul informasi berikut

```
[*] Started proxy on port {PORT}
```

Konfigurasi browser/sistem operasi anda untuk menggunakan HTTP proxy sesuai informasi yang diberikan.
Incoming request ke proxy akan ditandai dengan informasi

```
[+] Connected by {ADDR}
```

Selanjutnya, dapat dilakukan beberapa aksi terhadap request yang datang jika resource yang diminta oleh request tersebut tidak ada di dalam blacklist

```
C - Forward the request (Teruskan request)
P - Print request header (Print header request)
E - Add or edit header (Tambah atau edit header request)
B - Block the request (Blok request)
```

## Configurations

Terdapat beberapa konfigurasi yang dapat diatur pada file `config.ini`

```
[DEFAULT]
BLACKLIST = http://www\.columbia\.edu.*,http://wirasuta.com
HOST = 127.0.0.1
PORT = 7175
```

### BLACKLIST

Berisi pattern url yang diblok oleh proxy. Gunakan tanda `,` tanpa spasi untuk beberapa pattern url. Harus merupakan regular expression yang valid

### HOST

Berisi host proxy server

### PORT

Berisi port proxy server
