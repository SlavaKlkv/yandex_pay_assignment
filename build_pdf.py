#!/usr/bin/env python3
"""Сборка единого PDF-отчета из подготовленных материалов."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "yandex_pay_assignment.pdf"

pdfmetrics.registerFont(TTFont("DejaVu", "/System/Library/Fonts/Supplemental/Arial.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Mono", "/System/Library/Fonts/Supplemental/Andale Mono.ttf"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="RuBody", fontName="DejaVu", fontSize=9.4, leading=13, spaceAfter=5))
styles.add(ParagraphStyle(name="RuSmall", fontName="DejaVu", fontSize=7.6, leading=10, textColor=colors.HexColor("#445064")))
styles.add(ParagraphStyle(name="RuTitle", fontName="DejaVu-Bold", fontSize=22, leading=27, textColor=colors.HexColor("#111827"), alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="RuH1", fontName="DejaVu-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#111827"), spaceBefore=9, spaceAfter=7))
styles.add(ParagraphStyle(name="RuH2", fontName="DejaVu-Bold", fontSize=11.5, leading=15, textColor=colors.HexColor("#1F2937"), spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="RuCallout", fontName="DejaVu", fontSize=9, leading=13, backColor=colors.HexColor("#FFF7ED"), borderColor=colors.HexColor("#FB923C"), borderWidth=0.8, borderPadding=8, spaceBefore=6, spaceAfter=8))
styles.add(ParagraphStyle(name="PdfCode", fontName="DejaVu-Mono", fontSize=6.5, leading=8.4, textColor=colors.HexColor("#111827"), backColor=colors.HexColor("#F1F5F9"), borderColor=colors.HexColor("#CBD5E1"), borderWidth=0.5, borderPadding=7, spaceBefore=5, spaceAfter=7))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
    canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(18 * mm, 10 * mm, "Тестовое задание - интеграция Яндекс Сплита")
    canvas.drawRightString(192 * mm, 10 * mm, f"Страница {doc.page}")
    canvas.restoreState()


def p(text, style="RuBody"):
    return Paragraph(text, styles[style])


def bullets(items):
    result = []
    for item in items:
        result.append(Paragraph(f"• {item}", ParagraphStyle(name=f"b{len(result)}", parent=styles["RuBody"], leftIndent=10, firstLineIndent=-7)))
    return result


doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=20 * mm, title="Тестовое задание - Яндекс Пэй")
doc.addPageTemplates(PageTemplate(id="main", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")], onPage=footer))
story = []

story += [Spacer(1, 30 * mm), p("Тестовое задание", "RuTitle"), p("Специалист технической поддержки Яндекс Пэй", "RuTitle"), Spacer(1, 8 * mm)]
summary = Table([
    [p("Контур", "RuSmall"), p("Sandbox", "RuBody")],
    [p("Механика", "RuSmall"), p("Базовая оплата, только Сплит", "RuBody")],
    [p("Документация", "RuSmall"), p("Проверена по актуальным официальным страницам 30.09.2026", "RuBody")],
    [p("Фактический запуск", "RuSmall"), p("Тестовая оплата и полный возврат выполнены; итоговый статус - REFUNDED", "RuBody")],
], colWidths=[42 * mm, 116 * mm])
summary.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#CBD5E1")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
story += [summary, Spacer(1, 12 * mm), p("Важно: секрет из исходного задания не включен в этот документ. Логи обезличены; ссылка на оплату и заголовок Authorization скрыты.", "RuCallout"), PageBreak()]

story += [p("1. Последовательность подключения Сплита", "RuH1")]
sections = [
    ("1.1. Подготовка", [
        "Зарегистрировать магазин в кабинете Яндекс Пэй, подключить услугу Сплит и дождаться активации тестовой среды.",
        "Включить тестовые данные, настроить тестовый Callback URL и получить Merchant ID. В sandbox он используется как ключ Merchant API.",
        "Хранить ключ только на бэкенде. Передавать его как <font name='DejaVu-Mono'>Authorization: Api-Key &lt;key&gt;</font>; добавлять уникальный X-Request-Id.",
    ]),
    ("1.2. Бейдж и виджет", [
        "Подключить Web SDK с официального домена. В карточке товара установить бейдж Сплита с типом bnpl, суммой, Merchant ID и товарным контекстом.",
        "Добавить виджет в карточку товара. В PaymentData указать только SPLIT. Учесть, что виджет или бейдж могут скрыться, если Сплит недоступен пользователю.",
        "На шаге выбора способа оплаты показывать Сплит как единственный метод. Фронтенд и бэкенд должны использовать одинаковый availablePaymentMethods.",
    ]),
    ("1.3. Создание и оплата заказа", [
        "Бэкенд повторно проверяет цены и наличие, генерирует уникальный строковый orderId и вызывает POST /api/merchant/v1/orders.",
        "Передаются RUB, availablePaymentMethods=[SPLIT], полная корзина, redirectUrls и при необходимости данные риска и фискализации. Денежные значения и quantity.count - строки.",
        "Фронтенд получает только paymentUrl и открывает форму. Создание ссылки не является оплатой.",
        "Результат подтверждается webhook и/или GET /api/merchant/v1/orders/{order_id}. Успех - CAPTURED; PENDING требует повторной проверки; FAILED - терминальная ошибка.",
    ]),
    ("1.4. Полный возврат", [
        "Перед возвратом запросить заказ и убедиться, что статус CAPTURED или PARTIALLY_REFUNDED.",
        "Вызвать POST /api/merchant/v2/orders/{order_id}/refund с уникальным externalOperationId и refundAmount, равным доступному остатку. Для полного возврата корзину можно не передавать.",
        "Метод асинхронный: HTTP 200 означает прием запроса, а не окончание. Завершение полного возврата подтверждает статус REFUNDED.",
    ]),
]
for heading, items in sections:
    story.append(p(heading, "RuH2")); story.extend(bullets(items))

story += [PageBreak(), p("2. Ошибки исходного JSON", "RuH1")]
error_rows = [
    [p("Проблема", "RuSmall"), p("Почему это ошибка и как исправить", "RuSmall")],
    [p("orderId - число", "RuBody"), p("Схема ожидает строку; передать \"930318\".", "RuBody")],
    [p("quantity.count - число", "RuBody"), p("Тип string&lt;double&gt;; передать \"1\" и \"4\".", "RuBody")],
    [p("Доступен только CARD", "RuBody"), p("Для сценария «только Сплит» передать [\"SPLIT\"].", "RuBody")],
    [p("Служебные redirect URL", "RuBody"), p("Intranet и внутренний трекер недоступны внешнему покупателю. Нужны публичные HTTPS-страницы магазина.", "RuBody")],
]
t = Table(error_rows, colWidths=[45 * mm, 113 * mm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F1FF")), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#CBD5E1")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
story += [t, p("Арифметика корректна: 22 990,54 + (5 500,00 x 4) = 44 990,54. unitPrice 24 000,00 у второй позиции означает цену одной единицы до скидки; значение выглядит необычно, но total согласован с discountedUnitPrice.", "RuCallout"), p("Исправленный пример", "RuH2")]
corrected = '''{
  "availablePaymentMethods": ["SPLIT"],
  "metadata": "Не забыть пробить чек",
  "purpose": "Проведение оплаты покупки",
  "cart": {
    "items": [
      {"discountedUnitPrice": "22990.54", "productId": "126329",
       "title": "Роттердам Velvet Pink", "total": "22990.54",
       "quantity": {"count": "1"}},
      {"discountedUnitPrice": "5500.00", "unitPrice": "24000.00",
       "productId": "126330", "title": "Роттердам Velvet Blue",
       "total": "22000.00", "quantity": {"count": "4"}}
    ],
    "total": {"amount": "44990.54"}
  },
  "currencyCode": "RUB",
  "orderId": "930318",
  "redirectUrls": {
    "onError": "https://shop.example/order/930318/error",
    "onSuccess": "https://shop.example/order/930318/success",
    "onAbort": "https://shop.example/order/930318/abort"
  },
  "ttl": 1800
}'''
story.append(Preformatted(escape(corrected), styles["PdfCode"]))

story += [PageBreak(), p("3. Воспроизводимый тест", "RuH1"), p("Сценарий реализован в run_test.py без сторонних зависимостей. Ключ берется из переменной окружения YANDEX_PAY_API_KEY. Скрипт создает лог только после фактически выполненного HTTP-запроса и блокирует возврат, пока заказ не имеет допустимый статус.", "RuBody"), p("Команды для macOS", "RuH2")]
commands = """read -s YANDEX_PAY_API_KEY && export YANDEX_PAY_API_KEY && printf '\\n'
python3 run_test.py create
python3 run_test.py status '<ORDER_ID>'
python3 run_test.py refund '<ORDER_ID>'"""
story.append(Preformatted(commands, styles["PdfCode"]))
story += [p("После create необходимо вручную открыть paymentUrl и подтвердить тестовую оплату. После статуса CAPTURED команда refund отправляет полный возврат. Так как возврат асинхронный, итог подтверждается статусом REFUNDED.", "RuCallout"), p("Выполненные этапы", "RuH2")]
story.extend(bullets([
    "создан новый sandbox-заказ и получена платежная ссылка;",
    "завершена тестовая оплата через Сплит;",
    "после CAPTURED отправлен полный возврат и получен итоговый статус REFUNDED.",
]))

story += [p("Фактический результат запуска", "RuH2"), p("30.09.2026 в 17:32 UTC выполнен POST https://sandbox.pay.yandex.ru/api/merchant/v1/orders. Получены HTTP 200, status=success и paymentUrl. Идентификатор заказа: assignment-c8219b58-699b-4464-841c-fd28dc81ed42. Затем завершена тестовая оплата через Сплит. В 17:41 UTC отправлен полный возврат на 44 990,54 рубля; API принял асинхронную операцию с HTTP 200 и status=PENDING. Последующая проверка заказа через GET /api/merchant/v1/orders/{order_id} вернула HTTP 200 с итоговым paymentStatus=REFUNDED. Все действия выполнены в sandbox, поэтому реальные деньги не списывались.", "RuBody"), p("Обезличенный лог создания заказа", "RuH2")]
log_text = (ROOT / "create_order.log").read_text(encoding="utf-8")
story.append(Preformatted(log_text, styles["PdfCode"]))
story += [p("Обезличенный лог полного возврата", "RuH2")]
refund_log_text = (ROOT / "full_refund.log").read_text(encoding="utf-8")
story.append(Preformatted(refund_log_text, styles["PdfCode"]))
story += [p("Итоговая проверка статуса", "RuH2"), Preformatted("HTTP 200\norderId: assignment-c8219b58-699b-4464-841c-fd28dc81ed42\npaymentStatus: REFUNDED", styles["PdfCode"])]

story += [PageBreak(), p("Источники", "RuH1")]
sources = [
    ("Интеграция для онлайн-магазинов", "https://pay.yandex.ru/docs/ru/custom/integration-guide"),
    ("Базовая механика", "https://pay.yandex.ru/docs/ru/payments/basic"),
    ("Создание заказа", "https://pay.yandex.ru/docs/ru/custom/backend/yandex-pay-api/order/merchant_v1_orders-post"),
    ("Получение заказа", "https://pay.yandex.ru/docs/ru/custom/backend/yandex-pay-api/order/merchant_v1_order-get"),
    ("Возврат v2", "https://pay.yandex.ru/docs/ru/custom/backend/yandex-pay-api/order/merchant_v2_refund-post"),
    ("Аутентификация API", "https://pay.yandex.ru/docs/ru/custom/backend/yandex-pay-api/"),
    ("Тестирование", "https://pay.yandex.ru/docs/ru/testing"),
    ("Web SDK", "https://pay.yandex.ru/docs/ru/custom/web-sdk/"),
    ("Бейджи", "https://pay.yandex.ru/docs/ru/custom/web-sdk/badges"),
    ("Виджеты", "https://pay.yandex.ru/docs/ru/custom/web-sdk/ultimate-widget"),
]
for name, url in sources:
    story.append(p(f'<link href="{url}" color="#2563EB">{name}</link><br/><font size="7">{url}</font>'))
story += [Spacer(1, 6 * mm), p("Адреса из исходного PDF с префиксом /ru/docs заменены на действующий порядок /docs/ru. Все технические утверждения в отчете опираются на перечисленные официальные страницы Яндекс Пэй.", "RuCallout")]

doc.build(story)
print(OUTPUT)
