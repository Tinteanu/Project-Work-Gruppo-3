import json
import urllib3

# https://it.tradingview.com/markets/stocks-italy/market-movers-active/


def min(values):
    min = values[0]
    for i in range(1, len(values)):
        if min > values[i]:
            min = values[i]
    return min


def max(values):
    max = values[0]
    for i in range(1, len(values)):
        if max < values[i]:
            max = values[i]
    return max


def switch(x, y):
    temp = x
    x = y
    y = temp
    return x, y


def check_valid(date_to_validate_data, data, token):
    for date in data[token + " Time Series"]:
        date_data = list(map(int, date.split("-")))
        if date_data[0] == date_to_validate_data[0]:
          if date_data[1] == date_to_validate_data[1]:
            if date_data[2] == date_to_validate_data[2]:
              return True
    return False


def avg(values):
    return sum(values) / len(values)


def company(event):
  
  open = []
  high = []
  low = []
  close = []
  volume = []
  date1 = ""
  date2 = ""
  
  comp_symbol = (event["queryStringParameters"]["fetch_symbol"]).lower()
  inp_period = (event["queryStringParameters"]["fetch_period"]).lower()
  
  if inp_period == "settimanale":
      period = "TIME_SERIES_WEEKLY"
      token = "Weekly"
  elif inp_period == "mensile":
      period = "TIME_SERIES_MONTHLY"
      token = "Monthly"
  else:
      return "Error period"

  http = urllib3.PoolManager()

  request = http.request(
      "GET",
      f"https://www.alphavantage.co/query?function={period}&symbol={comp_symbol}&apikey=F3FV4ARAKOYQT44K")
  data = eval(request.data.decode("utf-8"))

  

  # ----------------------------
  # CONTROLLO DATE
    
  date1 = str(event["queryStringParameters"]["fetch_date_one"])
  date2 = str(event["queryStringParameters"]["fetch_date_two"])
    
  # Suddivido la stringa in lista con separatore "-" e converto la lista di stringhe in lisa di int
  date1_data = list(map(int, date1.split("-")))
  date2_data = list(map(int, date2.split("-")))
    
  # Scambi le date così da avere la più recente in "date1_data" e "date1"
  if date1_data[1] < date2_data[1]:
    date1_data, date2_data = switch(date1_data, date2_data)
    date1, date2 = switch(date1, date2)
    
  if date1_data[2] < date2_data[2]:
    date1_data, date2_data = switch(date1_data, date2_data)
    date1, date2 = switch(date1, date2)
    
  if date1_data[0] < date2_data[0]:
    date1_data, date2_data = switch(date1_data, date2_data)
    date1, date2 = switch(date1, date2)
    
    
  date1_is_valid = check_valid(date1_data, data, token)
  date2_is_valid = check_valid(date2_data, data, token)
    
  if not date1_is_valid:
      for i in range(0, 14):
        date1_data[2] += 1
        if date1_data[2] > 31:
          date1_data[2] = 1
          date1_data[1] += 1
        if date1_data[1] > 12:
          date1_data[1] = 1
          date1_data[0] += 1
        if check_valid(date1_data, data, token):
          date1 = (
            str(date1_data[0])
            + "-"
            + str(date1_data[1]).zfill(2)
            + "-"
             + str(date1_data[2]).zfill(2)
          )
          date1_is_valid = True
          break
    
  if not date2_is_valid:
    for i in range(0, 14):
      date2_data[2] -= 1
      if date2_data[2] < 1:
        date2_data[2] = 31
        date2_data[1] -= 1
      if date2_data[1] < 1:
        date2_data[1] = 12
        date2_data[0] -= 1
      if check_valid(date2_data, data, token): 
        date2 = (
          str(date2_data[0])
          + "-"
          + str(date2_data[1]).zfill(2)
          + "-"
          + str(date2_data[2]).zfill(2)
        )
        date2_is_valid = True
        break

      
  for date in data[token + " Time Series"]:
    append1 = False
    append2 = False
      
    date_data = list(map(int, date.split("-")))
      
    if date_data[0] < date1_data[0]:
      append1 = True
    elif date_data[0] == date1_data[0] and date_data[1] < date1_data[1]:
      append1 = True
    elif date_data[1] == date1_data[1] and date_data[2] <= date1_data[2]:
      append1 = True

    if date_data[0] > date2_data[0]:
      append2 = True
    elif date_data[0] == date2_data[0] and date_data[1] > date2_data[1]:
      append2 = True
    elif date_data[1] == date2_data[1] and date_data[2] >= date2_data[2]:
      append2 = True

      
    if append1 and append2:
      open.append(float(data[token + " Time Series"][date]["1. open"]))
      high.append(float(data[token + " Time Series"][date]["2. high"]))
      low.append(float(data[token + " Time Series"][date]["3. low"]))
      close.append(float(data[token + " Time Series"][date]["4. close"]))
      volume.append(int(data[token + " Time Series"][date]["5. volume"]))

  # ---------------------------
  # MAX, MIN, AVERAGE
  
  open_min = min(open)
  high_min = min(high)
  low_min = min(low)
  close_min = min(close)
  volume_min = min(volume)

  open_max = max(open)
  high_max = max(high)
  low_max = max(low)
  close_max = max(close)
  volume_max = max(volume)

  open_avg = round(avg(open), 4)
  high_avg = round(avg(high), 4)
  low_avg = round(avg(low), 4)
  close_avg = round(avg(close), 4)
  volume_avg = round(avg(volume))

  # ----------------------------
  # TREND 
  
  open_trend = open[0] - open[len(open) - 1]
  high_trend = high[0] - high[len(open) - 1]
  low_trend = low[0] - low[len(low) - 1]
  close_trend = close[0] - close[len(close) - 1]
  volume_trend = volume[0] - volume[len(volume) - 1]

  if open_trend > 0:
    open_trend = "positive"
  else:
    open_trend = "negative"

  if high_trend > 0:
    high_trend = "positive"
  else:
    high_trend = "negative"

  if low_trend > 0:
    low_trend = "positive"
  else:
    low_trend = "negative"

  if close_trend > 0:
    close_trend = "positive"
  else:
    close_trend = "negative"

  if volume_trend > 0:
    volume_trend = "positive"
  else:
    volume_trend = "negative"

  json_trend_dict = {
    "open": open_trend,
    "high": high_trend,
    "low": low_trend,
    "close": close_trend,
    "volume": volume_trend,
  }
  
  output_json_trend = json.dumps(json_trend_dict)
  
  output_data = {
    "body" : {
      "output_json" : {
        "min": {
        "open": open_min,
        "high": high_min,
        "low": low_min,
        "close": close_min,
        "volume": volume_min,
      }, "max": {
        "open": open_max,
        "high": open_max,
        "low": low_max,
        "close": close_max,
        "volume": volume_max,
      }, "avg": {
        "open": open_avg,
        "high": high_avg,
        "low": low_avg,
        "close": close_avg,
        "volume": volume_avg,
      },
      "output_json_trend" : {
        "open": open_trend,
        "high": high_trend,
        "low": low_trend,
        "close": close_trend,
        "volume": volume_trend,
        }
      }
    }
  }
  
  return output_data


def lambda_handler(event, context):
    try:
        return {"statusCode": 200, "body": json.dumps(company(event))}
    except:
        return {"statusCode": 400, "body": json.dumps("Error")}