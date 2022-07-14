from django.shortcuts import render

baseObj = {
    "page": 1,
    "rows": 20,
    "publisherType": None,
    "asset": "USDT",
    "tradeType": "BUY",
    "fiat": "USD",
    "payTypes": []
}
print(len(baseObj))