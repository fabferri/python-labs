<properties
pageTitle= 'Socket-Based Messaging in Python: sender and receiver'
description= "Socket-Based Messaging in Python: sender and receiver"
services="Python"
documentationCenter="https://github.com/fabferri/"
authors="fabferri"
editor=""/>

<tags
   ms.service="configuration-Example-Python"
   ms.devlang="Python"
   ms.topic="article"
   ms.tgt_pltfrm="python"
   ms.workload="socket"
   ms.date="04/10/2025"
   ms.author="fabferri" />

# Socket-Based Messaging in Python: sender and receiver

`async_tcp_server.py`: it is the receiver <br>
`async_tcp_client.py`: it is the sender <br>

<br>

**async_tcp_server.py** <br>
This asynchronous TCP server handles multiple client connections using asyncio, logging incoming data with timestamps and packet size comparisons. It supports optional UTF-8 decoding, queues incoming messages for processing, and ensures graceful shutdown on interruption. Designed for single-threaded operation (Windows-compatible), it provides detailed logging to both console and file for monitoring and debugging.

<br>

**async_tcp_client.py** <br>
This Python script uses asyncio to simulate multiple parallel TCP client connections to a server. Each client sends batches of messages with optional encoding, handles connection errors gracefully, and includes configurable parameters for host, port, number of connections, and message batches. It demonstrates asynchronous communication, error handling, and controlled message flow using delays.


`Tags: Python, Visual Studio Code` <br>
`date: 04-10-25` <br>

<!--Image References-->

<!--Link References-->
