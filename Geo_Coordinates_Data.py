#This is the Geo Coordinates for POIs and Towers
# Step 1: Define Actual POIs for a 10 km Radius Around Westminster Abbey
import pandas as pd

westminster_shops_pois = [
  {"name": "Selfridges", "category": "Department Store", "latitude": 51.5147, "longitude": -0.1528},
  {"name": "Fortnum & Mason", "category": "Luxury Department Store", "latitude": 51.5093, "longitude": -0.1376},
  {"name": "Harrods", "category": "Luxury Department Store", "latitude": 51.4994, "longitude": -0.1635},
  {"name": "Liberty London", "category": "Luxury Goods", "latitude": 51.5133, "longitude": -0.1407},
  {"name": "The Buckingham Palace Shop", "category": "Souvenir Shop", "latitude": 51.5014, "longitude": -0.1448},
  {"name": "Hamleys", "category": "Toy Store", "latitude": 51.5129, "longitude": -0.1404},
  {"name": "Apple Regent Street", "category": "Electronics", "latitude": 51.5146, "longitude": -0.1410},
  {"name": "Burberry Regent Street", "category": "Fashion", "latitude": 51.5139, "longitude": -0.1406},
  {"name": "M&M’s World London", "category": "Specialty Store", "latitude": 51.5115, "longitude": -0.1316},
  {"name": "Covent Garden Market", "category": "Shopping District", "latitude": 51.5110, "longitude": -0.1236}
]

# Convert POIs to a DataFrame
poi_data = pd.DataFrame(westminster_shops_pois)

westminster_towers = [
    {"tower_id": 1, "latitude": 51.5145, "longitude": -0.1412, "near_shops": ["Selfridges", "Apple Regent Street", "Liberty London"]},
    {"tower_id": 2, "latitude": 51.5018, "longitude": -0.1521, "near_shops": ["Harrods", "The Buckingham Palace Shop"]},
    {"tower_id": 3, "latitude": 51.5109, "longitude": -0.1334, "near_shops": ["Fortnum & Mason", "M&M’s World London"]},
    {"tower_id": 4, "latitude": 51.5132, "longitude": -0.1450, "near_shops": ["Hamleys", "Burberry Regent Street"]},
    {"tower_id": 5, "latitude": 51.4999, "longitude": -0.1380, "near_shops": ["The Buckingham Palace Shop", "Fortnum & Mason"]},
    {"tower_id": 6, "latitude": 51.5118, "longitude": -0.1402, "near_shops": ["Hamleys", "Liberty London"]},
    {"tower_id": 7, "latitude": 51.5155, "longitude": -0.1431, "near_shops": ["Selfridges", "Apple Regent Street"]},
    {"tower_id": 8, "latitude": 51.5120, "longitude": -0.1225, "near_shops": ["Covent Garden Market", "M&M’s World London"]},
    {"tower_id": 9, "latitude": 51.5045, "longitude": -0.1438, "near_shops": ["The Buckingham Palace Shop", "Harrods"]},
    {"tower_id": 10, "latitude": 51.5005, "longitude": -0.1625, "near_shops": ["Harrods"]}
  ]

# Convert POIs to a DataFrame
#towers_data = pd.DataFrame(westminster_towers)
