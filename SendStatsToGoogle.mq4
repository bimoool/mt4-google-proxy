#property strict

input string WebhookURL = "http://127.0.0.1:5000/send";
input int UpdateIntervalSec = 300;

datetime lastSend = 0;

void OnTick()
{
   if (TimeCurrent() - lastSend >= UpdateIntervalSec)
   {
      double balance = AccountBalance();
      double equity = AccountEquity();
      double profit = AccountProfit();
      double drawdown = balance - equity;

      string payload =
         "{"
         "\"account\":\"" + IntegerToString(AccountNumber()) + "\","
         "\"balance\":" + DoubleToString(balance, 2) + ","
         "\"equity\":" + DoubleToString(equity, 2) + ","
         "\"profit\":" + DoubleToString(profit, 2) + ","
         "\"drawdown\":" + DoubleToString(drawdown, 2) +
         "}";

      char post[];
      StringToCharArray(payload, post);

      char result[];
      string headers = "Content-Type: application/json\r\n";
      string cookie = "";
      string referer = "";
      int timeout = 5000;

      int res = WebRequest("POST", WebhookURL, cookie, referer, timeout, post, ArraySize(post) - 1, result, headers);

      if (res == -1)
      {
         Print("Ошибка WebRequest: ", GetLastError());
      }
      else
      {
         string response = CharArrayToString(result);
         Print("Ответ сервера: ", response);
      }

      lastSend = TimeCurrent();
   }
}