
from django.db import models
WILAYA_ZONES = {
    "09":"A","16":"A","35":"A","42":"A","31":"B","25":"B","05":"B",
    "06":"B","15":"B","23":"B","19":"B","21":"B","41":"B","13":"B",
    "22":"B","27":"B","29":"B","14":"C","26":"C","28":"C","17":"C",
    "38":"C","20":"C","18":"C","34":"C","36":"C","40":"C","44":"C",
    "03":"D","07":"D","08":"D","11":"D","30":"D","33":"D","37":"D",
    "39":"D","47":"D","49":"D","50":"D","51":"D","52":"D","53":"D",
    "54":"D","55":"D","56":"D","57":"D","58":"D",
}
ZONE_PRICES = {
    "A":{"standard":350,"express":600,"std_days":"1-2j","exp_days":"24h"},
    "B":{"standard":450,"express":750,"std_days":"2-3j","exp_days":"48h"},
    "C":{"standard":550,"express":900,"std_days":"3-5j","exp_days":"72h"},
    "D":{"standard":700,"express":1200,"std_days":"5-7j","exp_days":"4-5j"},
}
def get_delivery_cost(wilaya, method="standard"):
    zone = WILAYA_ZONES.get(wilaya,"C")
    p    = ZONE_PRICES.get(zone, ZONE_PRICES["C"])
    if method == "pickup":  return {"price":0,"days":"Immédiat","zone":zone}
    if method == "express": return {"price":p["express"],"days":p["exp_days"],"zone":zone}
    return {"price":p["standard"],"days":p["std_days"],"zone":zone}
