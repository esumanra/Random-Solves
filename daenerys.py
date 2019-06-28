from datetime import datetime

def say_hello(func):
  def wrapper():
    print(datetime.now().second)
    for k in range(100000): func()
    print(datetime.now().second)
  return wrapper

@say_hello
def my_name_is():
  print("mani")

my_name_is()