#This is the Geo Coordinates for POIs and Towers
# Step 1: Define Actual POIs for a 10 km Radius Around Westminster Abbey
import pandas as pd

westminster_shops_pois = [
    {"poi_id": 1, "poi_name": "Selfridges", "poi_category": "Department Store", 
     "poi_latitude": 51.5147, "poi_longitude": -0.1528,
     "poi_description": "An iconic London department store renowned for its luxurious shopping experience, Selfridges offers a diverse range of designer fashion, beauty products, home goods, and gourmet dining. Its striking architecture and innovative window displays make it a must-visit destination for both locals and tourists alike"},
     
    {"poi_id": 2, "poi_name": "Fortnum & Mason", "poi_category": "Luxury Department Store", 
     "poi_latitude": 51.5093, "poi_longitude": -0.1376,
     "poi_description": "A historic luxury department store offering fine foods, gifts, and afternoon tea in a refined setting."},
     
    {"poi_id": 3, "poi_name": "Harrods", "poi_category": "Luxury Department Store", 
     "poi_latitude": 51.4994, "poi_longitude": -0.1635,
     "poi_description": "World-famous luxury department store known for upscale fashion, food halls, and exquisite souvenirs."},
     
    {"poi_id": 4, "poi_name": "Liberty London", "poi_category": "Luxury Goods", 
     "poi_latitude": 51.5133, "poi_longitude": -0.1407,
     "poi_description": "Iconic Tudor-style store specializing in luxury fabrics, beauty products, and unique designer collections."},
     
    {"poi_id": 5, "poi_name": "The Buckingham Palace Shop", "poi_category": "Souvenir Shop", 
     "poi_latitude": 51.5014, "poi_longitude": -0.1448,
     "poi_description": "Official palace shop offering exclusive royal-themed souvenirs, gifts, and commemorative items."},
     
    {"poi_id": 6, "poi_name": "Hamleys", "poi_category": "Toy Store", 
     "poi_latitude": 51.5129, "poi_longitude": -0.1404,
     "poi_description": "The world’s oldest toy store featuring a wide range of toys, games, and entertainment for all ages."},
     
    {"poi_id": 7, "poi_name": "Apple Regent Street", "poi_category": "Electronics", 
     "poi_latitude": 51.5146, "poi_longitude": -0.1410,
     "poi_description": "Flagship Apple store showcasing the latest gadgets, with expert support and interactive demos."},
     
    {"poi_id": 8, "poi_name": "Burberry Regent Street", "poi_category": "Fashion", 
     "poi_latitude": 51.5139, "poi_longitude": -0.1406,
     "poi_description": "Luxury fashion boutique offering the latest Burberry collections, including its signature trench coats."},
     
    {"poi_id": 9, "poi_name": "M&M’s World London", "poi_category": "Specialty Store", 
     "poi_latitude": 51.5115, "poi_longitude": -0.1316,
     "poi_description": "Colorful, multi-story store filled with M&M-themed merchandise and personalized candy creations."},
     
    {"poi_id": 10, "poi_name": "Covent Garden Market", "poi_category": "Shopping District", 
     "poi_latitude": 51.5110, "poi_longitude": -0.1236,
     "poi_description": "Vibrant shopping and dining destination featuring boutique stores, street performers, and local crafts."}
]

# Convert POIs to a DataFrame
westminster_shops_pois_df = pd.DataFrame(westminster_shops_pois)

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
    {"tower_id": 10, "latitude": 51.5005, "longitude": -0.1625, "near_shops": ["Harrods"]},
    {"tower_id": 11, "latitude": 51.5160, "longitude": -0.1520, "near_shops": ["Selfridges", "Apple Regent Street"]},
    {"tower_id": 12, "latitude": 51.5142, "longitude": -0.1508, "near_shops": ["Selfridges", "Liberty London"]},
    {"tower_id": 13, "latitude": 51.5149, "longitude": -0.1540, "near_shops": ["Selfridges", "Hamleys"]}
]

# Convert POIs to a DataFrame
#towers_data = pd.DataFrame(westminster_towers)
