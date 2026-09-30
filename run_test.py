#!/usr/bin/env python3
"""Безопасный воспроизводимый сценарий sandbox: создать заказ, проверить статус, вернуть оплату."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://sandbox.pay.yandex.ru/api/merchant"
TOTAL = "44990.54"


def api_key() -> str:
    value = os.environ.get("YANDEX_PAY_API_KEY")
    if not value:
        raise SystemExit("Не задана переменная окружения YANDEX_PAY_API_KEY")
    return value


def request(method: str, path: str, body: dict | None = None) -> tuple[int, dict, dict]:
    request_id = str(uuid.uuid4())
    raw = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": f"Api-Key {api_key()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Request-Id": request_id,
        "X-Request-Timeout": "10000",
        "X-Request-Attempt": "0",
    }
    req = urllib.request.Request(BASE_URL + path, data=raw, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            response_body = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            response_body = json.loads(text)
        except json.JSONDecodeError:
            response_body = {"raw": text}
        status = exc.code
    public_request = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "url": BASE_URL + path,
        "headers": {
            "Authorization": "Api-Key <redacted>",
            "Content-Type": "application/json",
            "X-Request-Id": request_id,
            "X-Request-Timeout": "10000",
            "X-Request-Attempt": "0",
        },
        "body": body,
    }
    return status, response_body, public_request


def write_log(path: Path, public_request: dict, status: int, response: dict) -> None:
    safe_response = dict(response)
    data = safe_response.get("data")
    if isinstance(data, dict) and "paymentUrl" in data:
        data = dict(data)
        data["paymentUrl"] = "<redacted-payment-url>"
        safe_response["data"] = data
    path.write_text(
        json.dumps(
            {"request": public_request, "httpStatus": status, "response": safe_response},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def create_order(order_id: str) -> None:
    body = {
        "availablePaymentMethods": ["SPLIT"],
        "preferredPaymentMethod": "SPLIT",
        "metadata": "Тестовое задание: оплата и полный возврат",
        "purpose": "Тестовая оплата покупки",
        "cart": {
            "items": [
                {
                    "discountedUnitPrice": "22990.54",
                    "productId": "126329",
                    "title": "Роттердам Velvet Pink",
                    "total": "22990.54",
                    "quantity": {"count": "1"},
                },
                {
                    "discountedUnitPrice": "5500.00",
                    "unitPrice": "24000.00",
                    "productId": "126330",
                    "title": "Роттердам Velvet Blue",
                    "total": "22000.00",
                    "quantity": {"count": "4"},
                },
            ],
            "total": {"amount": TOTAL},
        },
        "currencyCode": "RUB",
        "orderId": order_id,
        "redirectUrls": {
            "onError": "https://example.com/payment/error",
            "onSuccess": "https://example.com/payment/success",
            "onAbort": "https://example.com/payment/abort",
        },
        "ttl": 1800,
    }
    status, response, public_request = request("POST", "/v1/orders", body)
    write_log(Path("create_order.log"), public_request, status, response)
    print(json.dumps({"httpStatus": status, "response": response}, ensure_ascii=False, indent=2))
    print(f"ORDER_ID={order_id}")


def get_order(order_id: str) -> dict:
    status, response, _ = request("GET", f"/v1/orders/{order_id}")
    print(json.dumps({"httpStatus": status, "response": response}, ensure_ascii=False, indent=2))
    return response


def refund(order_id: str) -> None:
    status_response = get_order(order_id)
    payment_status = (status_response.get("data") or {}).get("order", {}).get("paymentStatus")
    if payment_status not in {"CAPTURED", "PARTIALLY_REFUNDED"}:
        raise SystemExit(
            f"Возврат остановлен: статус заказа {payment_status!r}; требуется CAPTURED или PARTIALLY_REFUNDED"
        )
    body = {
        "externalOperationId": str(uuid.uuid4()),
        "refundAmount": TOTAL,
        "motive": "Полный возврат тестовой покупки",
    }
    status, response, public_request = request("POST", f"/v2/orders/{order_id}/refund", body)
    write_log(Path("full_refund.log"), public_request, status, response)
    print(json.dumps({"httpStatus": status, "response": response}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="Создать sandbox-заказ и записать create_order.log")
    create.add_argument("--order-id", default=f"assignment-{uuid.uuid4()}")
    status = sub.add_parser("status", help="Получить актуальный статус заказа")
    status.add_argument("order_id")
    refund_parser = sub.add_parser("refund", help="Выполнить полный возврат оплаченного заказа")
    refund_parser.add_argument("order_id")
    args = parser.parse_args()
    if args.command == "create":
        create_order(args.order_id)
    elif args.command == "status":
        get_order(args.order_id)
    else:
        refund(args.order_id)


if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"Сетевая ошибка: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
