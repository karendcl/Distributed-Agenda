def start_network(server, loop):
    print("NEW NETWORK")
    loop.set_debug(True)

    loop.run_until_complete(server.listen(8468))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()

def connect_node(server, ip, port, loop):
    print("CONNECT NODE")
    loop.set_debug(True)

    loop.run_until_complete(server.listen(8468))
    bs_node = (ip, int(port))
    print(f'Node: {bs_node}')
    loop.run_until_complete(server.bootstrap([bs_node]))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()

async def set(server, ip, port, args):
    await server.listen(8469)
    bootstrap_node = (ip, int(port))
    await server.bootstrap([bootstrap_node])
    await server.set(args.key, args.value)
    server.stop()

async def get(server, ip, port, args):
    await server.listen(8469)
    bootstrap_node = (ip, int(port))
    await server.bootstrap([bootstrap_node])
    # print(f"KEY FROM GET {args.key}")
    result = await server.get(args.key)
    print(result)
    server.stop()
    return result
