# MCP API Server

## Download requirements

```bash
pip install -r requirements.txt
```

## Agno version with tools

To run the Agno version with tools, you can use the following command :

```bash
python chatbot.py
```

## MCP version

To run the MCP version, you can use the following command:

```bash
python mcp_client/mcp_http_bridge.py
```

## Main differences

For now, the MCP version does not have any of the tools that the Agno version has.
It cannot get the price of a crypto, cannot initiate any transaction, etc.

But, this implementation is more flexible and faster.
It's a real MCP implementation, with a real client and a real server.

Here's the architecture of the MCP version:

```Frontend Vue.js
    ↓ HTTP/JSON (interface)
[mcp_client/api_routes.py]
    ↓ Appels vers
[mcp_client/mcp_client.py]
    ↓ ClientSession + stdio_client
    ↓ MCP Protocol (JSON-RPC stdio)
[mcp_serveur/mcp_server_sdk.py]
    ↓ Server + @server.call_tool()
    ↓ SDK MCP officiel
OpenAI API```