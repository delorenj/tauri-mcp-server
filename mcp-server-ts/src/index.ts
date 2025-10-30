#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { registerAllTools, initializeSocket } from "./tools/index.js";
import express from "express";
import cors from "cors";

// Create server instance
const server = new McpServer({
  name: "tauri-mcp",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    transport: 'stdio' as 'stdio' | 'sse',
    port: 8467,
    host: '127.0.0.1'
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '--transport':
      case '-t':
        const transport = args[i + 1];
        if (transport === 'sse' || transport === 'stdio') {
          config.transport = transport;
        }
        i++;
        break;
      case '--port':
      case '-p':
        const port = parseInt(args[i + 1], 10);
        if (!isNaN(port)) {
          config.port = port;
        }
        i++;
        break;
      case '--host':
      case '-h':
        config.host = args[i + 1];
        i++;
        break;
      case '--help':
        console.log(`
Tauri MCP Server

Usage: tauri-mcp-server [options]

Options:
  -t, --transport <type>  Transport type: stdio (default) or sse
  -p, --port <port>       Port for SSE transport (default: 8467)
  -h, --host <host>       Host for SSE transport (default: 127.0.0.1)
  --help                  Show this help message

Examples:
  tauri-mcp-server                           # Run with stdio transport
  tauri-mcp-server --transport sse           # Run with SSE on default port 8467
  tauri-mcp-server -t sse -p 9000           # Run with SSE on port 9000
        `);
        process.exit(0);
    }
  }

  return config;
}

async function main() {
  try {
    const config = parseArgs();

    console.error("=== Tauri MCP Server Starting ===");
    console.error("Process ID:", process.pid);
    console.error("Working directory:", process.cwd());
    console.error("Node version:", process.version);
    console.error("Environment NODE_ENV:", process.env.NODE_ENV);
    console.error("Transport:", config.transport);
    if (config.transport === 'sse') {
      console.error("SSE Host:", config.host);
      console.error("SSE Port:", config.port);
    }
    console.error("Args:", process.argv);

    // Connect to the Tauri socket server at startup
    console.error("Attempting to initialize socket connection...");
    await initializeSocket();

    // Register all tools with the server
    console.error("Registering tools with MCP server...");
    registerAllTools(server);

    if (config.transport === 'sse') {
      // Set up SSE transport with Express
      console.error("Setting up SSE transport...");
      const app = express();

      // Enable CORS for all routes
      app.use(cors({
        origin: true,
        credentials: true
      }));

      // Add JSON parsing middleware
      app.use(express.json());

      // Create SSE transport - this will be created when first GET request comes in
      let transport: SSEServerTransport;

      // Handle GET requests for SSE connection establishment
      app.get("/sse", async (req, res) => {
        console.error("SSE GET request - establishing SSE connection");
        transport = new SSEServerTransport("/sse", res);
        await server.connect(transport);
        console.error("SSE transport connected and ready for requests");
      });

      // Handle POST requests for MCP commands
      app.post("/sse", async (req, res) => {
        console.error("SSE POST request - handling MCP command");
        if (!transport) {
          res.status(503).json({ error: "SSE connection not established. Connect via GET first." });
          return;
        }
        // The transport should handle the POST request automatically
        // Just acknowledge that we received it
        res.status(200).json({ status: "received" });
      });

      // Start the Express server
      app.listen(config.port, config.host, () => {
        console.error(`Tauri MCP Server running on SSE at http://${config.host}:${config.port}/sse`);
      });
    } else {
      // Connect the server to stdio transport
      console.error("Connecting to stdio transport...");
      const transport = new StdioServerTransport();
      await server.connect(transport);
      console.error("Tauri MCP Server running on stdio");
    }
  } catch (error) {
    console.error("Fatal error in main():", error);
    console.error("Error stack:", error instanceof Error ? error.stack : 'No stack trace');
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
