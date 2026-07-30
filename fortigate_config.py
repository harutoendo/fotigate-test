#!/usr/bin/env python3

import os
import sys
import json
import argparse
import requests
from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings()


def api_request(
    scheme: str,
    host: str,
    port: int,
    token: str,
    method: str,
    path: str,
    **kwargs,
):
    base = f"{scheme}://{host}:{port}/"
    url = urljoin(base, path)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = requests.request(
        method,
        url,
        headers=headers,
        verify=False,
        timeout=30,
        **kwargs,
    )

    try:
        data = resp.json()
    except Exception:
        resp.raise_for_status()
        return resp

    if not resp.ok:
        raise RuntimeError(
            f"API error: HTTP {resp.status_code}, body={json.dumps(data, ensure_ascii=False)}"
        )

    return data


def set_hostname(
    scheme: str,
    host: str,
    port: int,
    token: str,
    hostname: str,
):
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


def get_hostname(
    scheme: str,
    host: str,
    port: int,
    token: str,
):
    data = api_request(
        scheme,
        host,
        port,
        token,
        "GET",
        "api/v2/cmdb/system/global",
    )

    results = data.get("results", {})
    return results.get("hostname", "")


def main():
    parser = argparse.ArgumentParser(
        description="FortiGate hostname configuration"
    )

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
        default=os.getenv("FGT_SCHEME", "https"),
        choices=["http", "https"],
    )

    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("FGT_PORT", "443")),
    )

    args = parser.parse_args()

    if not args.host:
        print("FGT_HOST is required", file=sys.stderr)
        sys.exit(2)

    if not args.token:
        print("FGT_API_TOKEN is required", file=sys.stderr)
        sys.exit(2)

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

    current_name = get_hostname(
        args.scheme,
        args.host,
        args.port,
        args.token,
    )

    print(
        f"Hostname updated: {args.host} -> {current_name}"
    )


if __name__ == "__main__":
    main()