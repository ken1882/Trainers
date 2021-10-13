from _G import *

def get_friends():
  res = get_request('https://mist-train-east4.azurewebsites.net/api/Friends')
  return res['r']

def get_rentals():
  res = get_request('https://mist-train-east4.azurewebsites.net/api/Friends/Rental')
  return [res['r']['FriendUsers'], res['r']['OtherUsers']]

def send_request(duid):
  res = get_request(f"https://mist-train-east4.azurewebsites.net/api/Friends/Search/{duid}")
  res = post_request("https://mist-train-east4.azurewebsites.net/api/Friends/SendRequests", [res['r']['UUserId']])
  return res