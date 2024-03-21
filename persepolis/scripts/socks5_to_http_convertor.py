# -*- coding: utf-8 -*-
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# This script is forked from this code: https://gist.github.com/zengxs/dc6cb4dea4495ecaab7b44abb07a581f

import asyncio
import logging
import re
from asyncio import StreamReader, StreamWriter, StreamReaderProtocol
from collections import namedtuple

import socks  # python-pysocks must be installed


HttpHeader = namedtuple('HttpHeader', ['method', 'url', 'version', 'connect_to', 'is_connect'])

class SocksToHttpConvertor():
    def __init__(self, socks5_host, socks5_port, socks5_username=None, socks5_password=None):
        self.socks5_host = socks5_host
        self.socks5_port = socks5_port
        self.username = socks5_username
        self.password = socks5_password



    async def dial(self, client_conn, server_conn):
        async def io_copy(reader: StreamReader, writer: StreamWriter):
            while True:
                data = await reader.read(8192)
                if not data:
                    break
                writer.write(data)
            writer.close()

        asyncio.ensure_future(io_copy(client_conn[0], server_conn[1]))
        asyncio.ensure_future(io_copy(server_conn[0], client_conn[1]))


    async def open_socks5_connection(self, host, port, socks5_host, socks5_port, username = None, password = None, limit=2 ** 16, loop=None):
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, addr=socks5_host, port=socks5_port, username=username, password=password)
        s.connect((host, port))

        if not loop:
            loop = asyncio.get_event_loop()

        reader = StreamReader(limit=limit, loop=loop)
        protocol = StreamReaderProtocol(reader, loop=loop)
        transport, _ = await loop.create_connection(lambda: protocol, sock=s)
        writer = StreamWriter(transport, protocol, reader, loop)
        return reader, writer


    async def read_until_end_of_http_header(self, reader: StreamReader):
        lines = []
        while True:
            line = await reader.readline()
            lines.append(line)
            if line == b'\r\n':
                break

        return b''.join(lines)


    def parse_http_header(self, header: bytes):
        lines = header.split(b'\r\n')
        fl = lines[0].decode()
        method, url, version = fl.split(' ', 2)

        if method.upper() == 'CONNECT':
            host, port = url.split(':', 1)
            port = int(port)
        else:
            # find Host header line
            host_text = None
            for header_line in lines:
                hl = header_line.decode()
                if re.match(r'^host:', hl, re.IGNORECASE):
                    host_text = re.sub(r'^host:\s*', '', hl, count=1, flags=re.IGNORECASE)
                    break

            if not host_text:
                raise ValueError("No http host line")

            if ':' not in host_text:
                host = host_text
                port = 80
            else:
                host, port = host_text.split(':', 1)
                port = int(port)

        is_connect = method.upper() == 'CONNECT'
        return HttpHeader(method=method, url=url, version=version, connect_to=(host, port), is_connect=is_connect)


    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        try:
            http_header_bytes = await self.read_until_end_of_http_header(reader)
            http_header = self.parse_http_header(http_header_bytes)
        except (IOError, ValueError) as e:
            logging.error(e)
            writer.close()
            return

        server_conn = await self.open_socks5_connection(
            host = http_header.connect_to[0],
            port = http_header.connect_to[1],
            socks5_host = self.socks5_host,
            socks5_port = self.socks5_port,
        )

        if http_header.is_connect:
            writer.write(b'HTTP/1.0 200 Connection Established\r\n\r\n')
        else:
            server_writer = server_conn[1]
            server_writer.write(http_header_bytes)

        asyncio.ensure_future(self.dial((reader, writer), server_conn))



    def runSocksConvertor(self, http_host, http_port):
        loop = asyncio.get_event_loop()
        server = asyncio.start_server(self.handle_connection, host=http_host, port=http_port)
        try:
            server = loop.run_until_complete(server)
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()

# convert = SocksToHttpConvertor('127.0.0.1', 9050) 
# convert.runSocksConvertor('127.0.0.1', 9061)

