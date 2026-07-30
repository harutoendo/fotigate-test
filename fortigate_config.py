#!/usr/bin/env python3

import os
import sys
import argparse
import requests
from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings()


def api_request(scheme, host, port, token, method, path, **kwargs):
    base = f"{scheme}://{host}:{port}/"
    url = urljoin(base, path)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.request(
        method,
        url,
        headers=headers,
        verify=False,
        timeout=30,
        **kwargs,
    )

    response.raise_for_status()

    try:
        return response.json()
    except Exception:
        return {}


def set_hostname(scheme, host, port, token, hostname):
    payload = {"hostname": hostname}

    return api_request(
        scheme,
        host,
        port,
        token,
        "PUT",
        "api/v2/cmdb/system/global",
        json=payload,
    )


def get_hostname(scheme, host, port, token):
    data = api_request(
        scheme,
        host,
        port,
        token,
        "GET",
        "api/v2/cmdb/system/global",
    )

    return data.get("results", {}).get("hostname", "")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--host",
        default=os.getenv("FGT_HOST"),
    )

    parser.add_argument(
        "--token",
        default=os.getenv("FGT_API_TOKEN"),
    )

    parser.add_argument(
        "--hostname",
        required=True,
    )

    parser.add_argument(
        "--scheme",
        default="https",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=443,
    )

    args = parser.parse_args()

    if not args.host:
        sys.exit("FGT_HOST is required")

    if not args.token:
        sys.exit("FGT_API_TOKEN is required")

    print(
        f"[INFO] target={args.scheme}://{args.host}:{args.port}/api/v2 ..."
    )

    set_hostname(
        args.scheme,
        args.host,
        args.port,
        args.token,
        args.hostname,
    )

    print(
        f"Hostname updated: {args.host} -> {args.hostname}"
    )


if __name__ == "__main__":
    main()