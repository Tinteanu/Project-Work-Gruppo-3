# Project Work #2

by Sassano Matteo, Tinteanu Antonio and Yaroslav Myronchuk


## Request

Design, Develop and Test an Alexa application that is able to:


- Given the company name and period (week or month) return the min, max and average value


- Given the company name and period (week or month) return the current trend (positive or negative)


You need to convert company name into symbol (using a static file on s3 to convert from company name to symbol to be used in APIs


Develop back-end with AWS lambda


API used: https://www.alphavantage.co/documentation/
Key used: F3FV4ARAKOYQT44K


## Lambda Python Code

First of all we wrote the python code capable of extracting out of the API request data every parameter we needed, to then proceed by using those attributes to complete the two tasks assigned to us. 

We use a token to determine the type of response we want from the API, either "Weekly" or "Monthly"



We first cicle through every date present in the API data, and for every one we save the values of the five attributes, "*open*", "*high*", "*low*", "*close*" and "*volume*", in individual lists.


    for date in data[token + " Time Series"]:
      open.append(float(data[token + " Time Series"][date]["1. open"]))
      high.append(float(data[token + " Time Series"][date]["2. high"]))
      low.append(float(data[token + " Time Series"][date]["3. low"]))
      close.append(float(data[token + " Time Series"][date]["4. close"]))
      volume.append(int(data[token + " Time Series"][date]["5. volume"]))


Once we get our lists of data, we then proceed on completing the fist task.


### First Task

To proceed with the first task we use the "*min*", "*max*" and "*avg*" functions so we can obtain the minimum, maximum and avarege value respectively, for every list.


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
    
    
    def avg(values):
      return sum(values) / len(values)


Once this is done, we can finally create and dump our json dictionary to use as our APIs output.


    json_dict = {
      "open": {
        "min": open_min,
        "max": open_max,
        "avg": open_avg
      },
      "high": {
        "min": high_min,
        "max": high_max,
        "avg": high_avg
      },
      "low": {
        "min": low_min,
        "max": low_max,
        "avg": low_avg
      },
      "close": {
        "min": close_min,
        "max": close_max,
        "avg": close_avg
      },
      "volume": {
        "min": volume_min,
        "max": volume_max,
        "avg": volume_avg
      }
    }
    
    output_json = json.dumps(json_dict)
    
### Second Task

For the second task we take out of the lists of data the fist and last values. Then we calculate the value of the trend by subtracing the  first value to the last, for example:


    open_trend = open[0] - open[len(open) - 1]


Then we check that value to determine if it's negative or positive.


    if open_trend > 0:
      open_trend = "positive"
    else:
      open_trend = "negative"


As the last step we once again create a json dictionary, to later dump and use as output.


    json_trend_dict = {
      "open": open_trend,
      "high": high_trend,
      "low": low_trend,
      "close": close_trend,
      "volume": volume_trend
    }
    
    output_json_trend = json.dumps(json_trend_dict)


### Date Management

During this step we also developed a way to check if two given dates are valid, for later use (the user will need to specify a period of time, using two dates, in which to operate all of our tasks).


Given two dates, "*date1*" and "*date2*", we first extract the day, month and year data in a list.


    date1_data = list(map(int, date1.split("-")))
    date2_data = list(map(int, date2.split("-")))


Then comparing the two we use a simple "*switch*" function to always have the first date as the most recent.


    def switch(x, y):
      temp = x
      x = y
      y = temp
      return x, y
 
 After that is done we actually check if the two dates are present in the API data using another function called "*check_valid*".


     def check_valid(date_to_validate_data, data, token):
      for date in data[token + " Time Series"]:
        date_data = list(map(int, date.split("-")))
        if date_data[0] == date_to_validate_data[0]:
          if date_data[1] == date_to_validate_data[1]:
            if date_data[2] == date_to_validate_data[2]:
              return True
      return False


If the two dates are present then we can safely proceed, but if one of them or both are not valid we increase the interval of the period given, as to obtain two valid dates present in the API data. We increase the first date with the following process:


    if not date1_is_valid:
      for i in range(0, 14):
        date1_data[2] += 1
        if date1_data[2] > 31:
          date1_data[2] = 1
          date1_data[1] += 1
          if date1_data[1] > 12:
            date1_data[1] = 1
            date1_data[0] += 1
        if check_valid(date1_data, data):
          date1 = str(date1_data[0]) + "-" + str(date1_data[1]).zfill(2) + "-" + str(date1_data[2]).zfill(2)
          date1_is_valid = True
          break


And then we do the same for the second date decresing it instead.
