# Yandex Pay assignment

Решение тестового задания для базовой интеграции Яндекс Сплита.

## Состав

- `integration_flow.md` - схема подключения, оплаты, UI-компонентов и возврата.
- `request_errors.md` - ошибки исходного JSON и исправленный пример.
- `run_test.py` - сценарий создания sandbox-заказа, проверки статуса и полного возврата.
- `create_order.log` - создается только после реального HTTP-запроса.
- `full_refund.log` - создается только после реального запроса возврата и только для оплаченного заказа.
- `yandex_pay_assignment.pdf` - единый отчет.

## Требования

- macOS с Python 3.10 или новее;
- тестовый Merchant ID/ключ, для которого включены тестовые данные и Сплит;
- публичный Callback URL в настройках магазина (для полноценной проверки webhook);
- аккаунт Яндекс ID и доступ к SMS для ручного подтверждения тестовой оплаты.

Скрипт использует только стандартную библиотеку Python. Ключ читается из переменной окружения `YANDEX_PAY_API_KEY` и не записывается в исходный код или логи.

## Запуск на macOS

Из каталога проекта задайте ключ без сохранения в shell history:

```bash
read -s YANDEX_PAY_API_KEY && export YANDEX_PAY_API_KEY && printf '\n'
```

Создайте тестовый заказ:

```bash
python3 run_test.py create
```

Команда напечатает `paymentUrl` и `ORDER_ID`, а также создаст обезличенный `create_order.log`. Откройте `paymentUrl`, убедитесь, что адрес начинается с `https://sandbox`, и вручную завершите тестовую оплату. Создание заказа или открытие ссылки не является успешной оплатой.

Проверьте статус, подставив полученный идентификатор:

```bash
python3 run_test.py status '<ORDER_ID>'
```

Только после появления `paymentStatus: CAPTURED` выполните полный возврат:

```bash
python3 run_test.py refund '<ORDER_ID>'
```

Скрипт сам повторно проверит статус и откажется отправлять возврат, если заказ не оплачен. Успешная отправка метода возврата еще не означает завершение: API асинхронный. Снова запросите статус и убедитесь, что он стал `REFUNDED`.

## Безопасность и логи

- Заголовок Authorization в логах заменяется на `<redacted>`.
- Ссылка на оплату в логе заменяется на `<redacted-payment-url>`.
- `full_refund.log` не создается до реального вызова API.
- Не публикуйте исходный PDF задания: он содержит учетные данные.

## Официальная документация

- [Тестирование](https://pay.yandex.ru/docs/ru/testing)
- [Создание заказа](https://pay.yandex.ru/docs/ru/custom/backend/yandex-pay-api/order/merchant_v1_orders-post)
- [Получение заказа](https://pay.yandex.ru/docs/ru/custom/backend/yandex-pay-api/order/merchant_v1_order-get)
- [Полный возврат](https://pay.yandex.ru/docs/ru/custom/backend/yandex-pay-api/order/merchant_v2_refund-post)
