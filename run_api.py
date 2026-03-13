#!/usr/bin/env python3
"""
Entry point to run the HTTP API backend for the C# frontend.
"""

import uvicorn


def main():
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()

