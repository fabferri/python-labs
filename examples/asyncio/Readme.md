<properties
pageTitle= 'Python: asyncio examples'
description= "Python: asyncio examples"
services="Python"
documentationCenter="https://github.com/fabferri/"
authors="fabferri"
editor=""/>

<tags
   ms.service="configuration-Example-Azure"
   ms.devlang="Azure libraries for Python"
   ms.topic="article"
   ms.tgt_pltfrm="Azure"
   ms.workload="Python"
   ms.date="01/12/2023"
   ms.author="fabferri" />

# Python: asyncio examples
[asyncio](https://docs.python.org/3/library/asyncio.html) is a library to write concurrent code using the async/await syntax. <br>
asyncio works with Coroutines. Coroutines are nothing but a specialized version of Python generator functions. <br>

A [coroutine](https://docs.python.org/3.11/library/asyncio-task.html#coroutine) is a function that can suspend its execution before reaching the return and it can indirectly pass the control to another coroutine for some time.

A coroutine may suspend for many reasons, such as executing another coroutine, e.g. awaiting another task, or waiting for some external resources. Coroutines are used for concurrency.


`Tags: Python` <br>
`date: 03-12-23` <br>

<!--Image References-->

<!--Link References-->
