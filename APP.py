# app.py — Campus Drone Delivery (WebGL + AI-Powered Food Delivery)
# Multi-page app with Live Drones, AI Assistant, Customer Feedback, and Admin Dashboard

import time
import math
import random
from datetime import datetime, timedelta
import json

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Campus Drone Delivery — Food Delivery with Dining Dollars",
    page_icon="🚁",
    layout="wide",
)

st.markdown(
    """
    <style>
      .small-note {opacity:.7; font-size:0.85rem}
      .section-title {font-weight:700; font-size:1.05rem; margin: 6px 0 8px}
      .panel {padding:10px 12px;border-radius:12px;background:#0f141a;border:1px solid #1b2633}
      .map-wrap {border-radius:12px; overflow:hidden; border:1px solid #1b2633}
      .pad-top {margin-top:14px}
      .stButton>button {border-radius:10px}
      .label-pill {display:inline-block;border:1px solid #2a3b4a;border-radius:999px;padding:2px 8px;margin-right:6px}
      .eta-card {
        padding: 12px;
        border-radius: 8px;
        background: #1a2332;
        border-left: 4px solid;
        margin-bottom: 8px;
      }
      .restaurant-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        background: linear-gradient(135deg, #FFC107 0%, #FF9800 100%);
        color: white;
      }
      .feedback-card {
        padding: 16px;
        border-radius: 12px;
        background: #1a2332;
        border: 1px solid #2a3b4a;
        margin-bottom: 12px;
      }
      .priority-high {
        border-left: 4px solid #E31A1C;
      }
      .priority-medium {
        border-left: 4px solid #FFA500;
      }
      .priority-low {
        border-left: 4px solid #33A02C;
      }
      .stat-card {
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1a2332 0%, #2a3b4a 100%);
        text-align: center;
      }
      .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #FFC107;
      }
      .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 4px;
      }
      .order-card {
        padding: 16px;
        border-radius: 12px;
        background: #1a2332;
        border: 1px solid #2a3b4a;
        margin-bottom: 12px;
      }
      .legend-card {
        padding: 12px;
        border-radius: 8px;
        background: #1a2332;
        border: 1px solid #2a3b4a;
        margin-bottom: 8px;
      }
      .legend-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-size: 0.9rem;
      }
      .legend-icon {
        font-size: 1.2rem;
        margin-right: 8px;
        width: 24px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Demo data ----------------
DELIVERY_LOCATIONS = pd.DataFrame([
    ("North Hall", 40.7490, -73.9830, "Residence"),
    ("Central Plaza", 40.7470, -73.9820, "Common Area"),
    ("Science Building", 40.7477, -73.9830, "Academic"),
    ("Student Union", 40.7465, -73.9850, "Dining Hub"),
    ("Recreation Center", 40.7470, -73.9910, "Recreation"),
    ("West Apartments", 40.7474, -73.9940, "Residence"),
    ("East Dorms", 40.7485, -73.9790, "Residence"),
    ("Library", 40.7460, -73.9835, "Academic"),
    ("Engineering Hall", 40.7495, -73.9825, "Academic"),
], columns=["location","lat","lon","type"])

RESTAURANTS = pd.DataFrame([
    ("Chick-fil-A", 40.7465, -73.9875, "Fast Food", 4.6, ["chicken sandwiches", "nuggets", "waffle fries"]),
    ("McDonald's", 40.7452, -73.9895, "Fast Food", 4.2, ["burgers", "fries", "chicken nuggets"]),
    ("Chipotle", 40.7478, -73.9852, "Mexican", 4.4, ["burritos", "bowls", "tacos"]),
    ("Subway", 40.7468, -73.9868, "Sandwiches", 4.1, ["subs", "salads", "wraps"]),
    ("Zaxby's", 40.7455, -73.9910, "Fast Food", 4.5, ["chicken fingers", "wings", "salads"]),
    ("Domino's Pizza", 40.7485, -73.9840, "Pizza", 4.3, ["pizza", "wings", "pasta"]),
    ("Panera Bread", 40.7472, -73.9815, "Cafe", 4.4, ["sandwiches", "soups", "salads"]),
    ("Taco Bell", 40.7460, -73.9920, "Mexican", 4.0, ["tacos", "burritos", "quesadillas"]),
], columns=["name","lat","lon","cuisine","rating","menu_types"])

RESTAURANT_MENUS = {
    "Chick-fil-A": {
        "Chicken Sandwich": 4.99,
        "Spicy Chicken Sandwich": 5.29,
        "Nuggets (8-count)": 4.49,
        "Nuggets (12-count)": 6.49,
        "Waffle Fries": 2.49,
        "Mac & Cheese": 3.49,
        "Chicken Strips (3-count)": 5.99,
        "Lemonade": 2.29,
        "Sweet Tea": 2.19,
        "Milkshake": 4.79
    },
    "McDonald's": {
        "Big Mac": 5.99,
        "Quarter Pounder": 5.79,
        "McChicken": 3.99,
        "10 Piece Nuggets": 5.49,
        "Medium Fries": 2.79,
        "Large Fries": 3.39,
        "McFlurry": 3.99,
        "Medium Coke": 1.99,
        "Apple Pie": 1.49,
        "Hash Browns": 1.99
    },
    "Chipotle": {
        "Chicken Burrito": 9.25,
        "Steak Burrito": 10.95,
        "Chicken Bowl": 9.25,
        "Steak Bowl": 10.95,
        "Veggie Bowl": 8.25,
        "Chips & Guacamole": 4.50,
        "Chips & Queso": 4.25,
        "Quesadilla": 9.75,
        "Fountain Drink": 2.85,
        "Side of Rice": 3.00
    },
    "Subway": {
        "Footlong Turkey": 8.99,
        "Footlong Italian BMT": 9.49,
        "6-inch Turkey": 5.99,
        "6-inch Meatball": 5.49,
        "Chips": 1.50,
        "Cookie": 1.29,
        "Fountain Drink": 2.19,
        "Veggie Delight": 6.49,
        "Chicken Teriyaki": 7.99,
        "Tuna Sub": 6.99
    },
    "Zaxby's": {
        "Chicken Fingers (4pc)": 8.99,
        "Chicken Fingers (6pc)": 11.99,
        "Wings (10pc)": 12.49,
        "Zalad": 8.99,
        "Fries": 2.49,
        "Texas Toast": 1.99,
        "Cole Slaw": 2.49,
        "Sweet Tea": 2.29,
        "Zax Sauce": 0.79,
        "Boneless Wings Meal": 10.49
    },
    "Domino's Pizza": {
        "Large Pepperoni Pizza": 12.99,
        "Large Cheese Pizza": 10.99,
        "Medium 2-Topping": 9.99,
        "Chicken Wings (8pc)": 7.99,
        "Chicken Wings (16pc)": 14.99,
        "Breadsticks": 5.99,
        "Cheesy Bread": 6.49,
        "Pasta Primavera": 7.99,
        "Cinnamon Twist": 5.99,
        "2-Liter Coke": 3.29
    },
    "Panera Bread": {
        "Turkey Sandwich": 9.49,
        "Broccoli Cheddar Soup": 6.99,
        "Caesar Salad": 8.99,
        "Mac & Cheese": 7.99,
        "Grilled Cheese": 6.49,
        "Chicken Noodle Soup": 6.99,
        "Bagel with Cream Cheese": 3.99,
        "Pastry": 3.49,
        "Coffee": 2.79,
        "Fountain Drink": 2.99
    },
    "Taco Bell": {
        "Crunchy Taco": 1.79,
        "Soft Taco": 1.89,
        "Burrito Supreme": 4.99,
        "Quesadilla": 5.29,
        "Nachos BellGrande": 5.49,
        "Crunchwrap Supreme": 5.49,
        "Chalupa": 4.49,
        "Mexican Pizza": 4.99,
        "Fountain Drink": 2.19,
        "Freeze": 3.49
    }
}

DELIVERY_TIME_MINUTES = 8

ISSUE_CATEGORIES = [
    "Late Delivery",
    "Wrong Order",
    "Food Quality",
    "Drone Malfunction",
    "Payment Issue",
    "Missing Items",
    "Temperature Issue",
    "Location Access",
    "Campus Safety Concern",
    "Restaurant Service",
    "Other"
]

# ---------------- Session State ----------------
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = []

if "ai_insights" not in st.session_state:
    st.session_state.ai_insights = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_orders" not in st.session_state:
    st.session_state.active_orders = []

if "order_counter" not in st.session_state:
    st.session_state.order_counter = 1

if "cart_items" not in st.session_state:
    st.session_state.cart_items = []

if "last_order_route" not in st.session_state:
    st.session_state.last_order_route = None

# ---------------- Helpers ----------------
def create_location_markers():
    locations_list = []
    for _, loc in DELIVERY_LOCATIONS.iterrows():
        locations_list.append({
            "location": loc["location"],
            "lat": loc["lat"],
            "lon": loc["lon"],
            "type": loc["type"]
        })
    return pd.DataFrame(locations_list)

def create_restaurant_markers():
    restaurants_list = []
    for _, rest in RESTAURANTS.iterrows():
        restaurants_list.append({
            "name": rest["name"],
            "lat": rest["lat"],
            "lon": rest["lon"],
            "cuisine": rest["cuisine"],
            "rating": rest["rating"]
        })
    return pd.DataFrame(restaurants_list)

def simulate_drone_position(start_lat, start_lon, end_lat, end_lon, progress):
    lat = start_lat + (end_lat - start_lat) * progress
    lon = start_lon + (end_lon - start_lon) * progress
    return lat, lon

def simulated_drones_df():
    rows = []
    for order in st.session_state.active_orders:
        if order["status"] == "In Transit":
            elapsed = (datetime.now() - order["start_time"]).total_seconds() / 60
            progress = min(elapsed / DELIVERY_TIME_MINUTES, 1.0)
            
            lat, lon = simulate_drone_position(
                order["restaurant_lat"], order["restaurant_lon"],
                order["delivery_lat"], order["delivery_lon"],
                progress
            )
            
            rows.append({
                "order_id": order["order_id"],
                "restaurant": order["restaurant"],
                "location": order["location"],
                "lon": lon,
                "lat": lat,
                "icon": "🚁"
            })
    return pd.DataFrame(rows)

def place_order(restaurant, location, items, total):
    rest_data = RESTAURANTS[RESTAURANTS["name"] == restaurant].iloc[0]
    loc_data = DELIVERY_LOCATIONS[DELIVERY_LOCATIONS["location"] == location].iloc[0]
    
    order = {
        "order_id": st.session_state.order_counter,
        "restaurant": restaurant,
        "restaurant_lat": rest_data["lat"],
        "restaurant_lon": rest_data["lon"],
        "location": location,
        "delivery_lat": loc_data["lat"],
        "delivery_lon": loc_data["lon"],
        "items": items,
        "total": total,
        "status": "Preparing",
        "placed_time": datetime.now(),
        "start_time": datetime.now() + timedelta(minutes=3),
        "eta": datetime.now() + timedelta(minutes=3 + DELIVERY_TIME_MINUTES)
    }
    
    st.session_state.active_orders.append(order)
    st.session_state.order_counter += 1
    return order

def analyze_feedback_with_ai(feedback_entry):
    category = feedback_entry["category"]
    
    if category in ["Food Quality", "Drone Malfunction", "Campus Safety Concern"]:
        priority = "High"
    elif category in ["Late Delivery", "Wrong Order", "Missing Items", "Temperature Issue"]:
        priority = "Medium"
    else:
        priority = "Low"
    
    recommendations = []
    
    if category == "Late Delivery":
        recommendations = [
            "Optimize drone routing algorithm for faster campus deliveries",
            "Increase drone fleet during peak hours",
            "Implement weather-aware scheduling"
        ]
    elif category == "Wrong Order":
        recommendations = [
            "Enhance order verification system",
            "Implement barcode scanning",
            "Train restaurant partners"
        ]
    else:
        recommendations = [
            "Review and address reported issue",
            "Follow up with student",
            "Monitor for similar complaints"
        ]
    
    return {
        "priority": priority,
        "recommendations": recommendations,
        "ai_summary": f"AI Analysis: {category} issue. Priority: {priority}.",
        "estimated_impact": "Affects student satisfaction"
    }

def save_feedback(feedback_entry):
    feedback_entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_entry["status"] = "Pending Review"
    feedback_entry["id"] = len(st.session_state.feedback_data) + 1
    
    ai_analysis = analyze_feedback_with_ai(feedback_entry)
    feedback_entry["ai_analysis"] = ai_analysis
    
    st.session_state.feedback_data.append(feedback_entry)
    
    insight = {
        "timestamp": feedback_entry["timestamp"],
        "category": feedback_entry["category"],
        "priority": ai_analysis["priority"],
        "summary": ai_analysis["ai_summary"],
        "recommendations": ai_analysis["recommendations"]
    }
    st.session_state.ai_insights.append(insight)

def generate_ai_response(query):
    query_lower = query.lower()
    
    # ========== ORDER STATUS & TRACKING ==========
    # Check for order status queries (including "my order", "the order", "just ordered")
    if any(phrase in query_lower for phrase in ["my order", "order status", "where is my", "track order", "where's my order", "check order", "order #", "the order i", "order i just", "just ordered", "tell me the order", "what did i order", "what order"]):
        if st.session_state.active_orders:
            recent_order = st.session_state.active_orders[-1]
            pickup_location = recent_order["location"]
            restaurant = recent_order["restaurant"]
            order_id = recent_order["order_id"]
            status = recent_order["status"]
            eta_minutes = int((recent_order["eta"] - datetime.now()).total_seconds() / 60)
            
            if eta_minutes < 0:
                eta_minutes = 0
            
            status_emoji = "👨‍🍳" if status == "Preparing" else "🚁" if status == "In Transit" else "✅"
            
            # Show all items clearly
            items_list = recent_order["items"].split('\n')
            
            return f"""**{status_emoji} Order #{order_id} - {status}**

🍽️ **Restaurant:** {restaurant}

**📦 Your Items:**
{chr(10).join(['  ' + item for item in items_list])}

💵 **Total:** ${recent_order['total']:.2f}

📍 **PICKUP LOCATION:** **{pickup_location}**
⏱️ **ETA:** {eta_minutes} minutes

{"🚁 Your drone is in the air! Track it on the **Live Deliveries** page." if status == "In Transit" else "👨‍🍳 Your food is being prepared. Drone will launch in ~3 minutes!" if status == "Preparing" else "✅ Order delivered! Hope you enjoyed your meal."}

💡 **Tip:** Head to **{pickup_location}** now so you're there when your drone arrives!"""
        else:
            return """**No Active Orders**

You don't have any orders in progress right now. 

🍽️ Ready to order? Go to the **Order Food** page to browse menus and place an order!

I'll track your delivery in real-time once you order. 🚁"""
    
    # ========== SPECIFIC MENU ITEM QUERIES ==========
    # Check if asking about specific menu items
    menu_item_keywords = ["nuggets", "chicken sandwich", "burger", "fries", "burrito", "bowl", "taco", "pizza", "wings", 
                         "sandwich", "salad", "mac and cheese", "cookie", "drink", "milkshake", "quesadilla", "pasta"]
    
    if any(item in query_lower for item in menu_item_keywords):
        # Search for which restaurants have this item
        matching_restaurants = []
        
        for restaurant, menu in RESTAURANT_MENUS.items():
            for menu_item, price in menu.items():
                if any(keyword in menu_item.lower() for keyword in query_lower.split()):
                    matching_restaurants.append({
                        "restaurant": restaurant,
                        "item": menu_item,
                        "price": price
                    })
        
        if matching_restaurants:
            # Get the first match details
            match = matching_restaurants[0]
            restaurant = match["restaurant"]
            rest_info = RESTAURANTS[RESTAURANTS["name"] == restaurant].iloc[0]
            
            # Find closest pickup point
            rest_lat, rest_lon = rest_info["lat"], rest_info["lon"]
            closest_pickup = None
            min_distance = float('inf')
            
            for _, loc in DELIVERY_LOCATIONS.iterrows():
                distance = math.sqrt((rest_lat - loc["lat"])**2 + (rest_lon - loc["lon"])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_pickup = loc["location"]
            
            response = f"""**Found it! 🎉**

🍽️ **{match['item']}** - ${match['price']:.2f}
📍 Available at **{restaurant}**

"""
            
            # Show other options if multiple restaurants have similar items
            if len(matching_restaurants) > 1:
                response += "**Also available at:**\n"
                for other in matching_restaurants[1:4]:  # Show up to 3 more
                    response += f"• {other['restaurant']}: {other['item']} (${other['price']:.2f})\n"
                response += "\n"
            
            response += f"""**📦 Recommended Pickup:** {closest_pickup}
⏱️ **Delivery Time:** 8-11 minutes

🛒 **Ready to order?** Go to the **Order Food** page, select **{restaurant}**, and add this to your cart!"""
            
            return response
        else:
            return f"""**Hmm, I couldn't find that exact item.**

Let me show you what's available! Here are our restaurants:

{chr(10).join([f"• **{row['name']}** - {row['cuisine']}" for _, row in RESTAURANTS.iterrows()])}

💡 **Try asking:**
• "Show me the Chick-fil-A menu"
• "What can I get at Chipotle?"
• "Where can I order pizza?"

Or go to **Order Food** page to browse all menus! 🍽️"""
    
    # ========== PICKUP SPOT RECOMMENDATIONS ==========
    # Better handling for "where do I get" or "where can I order"
    if any(phrase in query_lower for phrase in ["where do i get", "where can i get", "where can i order", "pickup spot for", "get from", "where should i pick up"]):
        # Check which restaurant they're asking about
        for restaurant in RESTAURANTS["name"].tolist():
            if restaurant.lower() in query_lower or any(word in query_lower for word in restaurant.lower().split()):
                rest_info = RESTAURANTS[RESTAURANTS["name"] == restaurant].iloc[0]
                
                # Find closest pickup point to this restaurant
                rest_lat, rest_lon = rest_info["lat"], rest_info["lon"]
                closest_pickup = None
                second_closest = None
                min_distance = float('inf')
                second_min = float('inf')
                
                for _, loc in DELIVERY_LOCATIONS.iterrows():
                    distance = math.sqrt((rest_lat - loc["lat"])**2 + (rest_lon - loc["lon"])**2)
                    if distance < min_distance:
                        second_min = min_distance
                        second_closest = closest_pickup
                        min_distance = distance
                        closest_pickup = loc["location"]
                    elif distance < second_min:
                        second_min = distance
                        second_closest = loc["location"]
                
                return f"""**{restaurant} Delivery 🍽️**

📍 **BEST PICKUP POINT:** **{closest_pickup}**

{closest_pickup} is the closest to {restaurant}, so your drone will arrive fastest here!

⏱️ **Estimated delivery:** 8-11 minutes
⭐ **Rating:** {rest_info['rating']}/5.0

**Alternative Option:**
📦 {second_closest} (slightly farther)

**How to order:**
1. Go to **Order Food** page
2. Select **{restaurant}**
3. Choose **{closest_pickup}** as delivery location
4. Track your drone in real-time! 🚁"""
    
    # ========== WHICH PICKUP POINT FOR USER ==========
    if any(phrase in query_lower for phrase in ["which pickup", "what pickup", "where pickup", "pickup spot should", "where do i have to pick", "where do i pick", "where to pick", "pick it up"]):
        if st.session_state.active_orders:
            recent_order = st.session_state.active_orders[-1]
            eta_minutes = int((recent_order['eta'] - datetime.now()).total_seconds() / 60)
            if eta_minutes < 0:
                eta_minutes = 0
            
            return f"""**📍 Your Pickup Location**

**GO TO: {recent_order['location']}**

🍽️ **Order:** #{recent_order['order_id']} from {recent_order['restaurant']}
⏱️ **ETA:** {eta_minutes} minutes

🗺️ **See the live drone route** on the **Live Deliveries** page!

💡 The drone is flying from {recent_order['restaurant']} directly to {recent_order['location']}. You'll see the blue flight path on the map!"""
        else:
            return """**Choose Your Pickup Spot**

You don't have an active order, but I can help you pick the best spot!

**Tell me:**
• Where are you on campus? (e.g., "I'm at North Hall")
• Which restaurant? (e.g., "I want Chick-fil-A")

Then I'll recommend the perfect pickup point! 📍"""
    
    # ========== USER LOCATION-BASED RECOMMENDATIONS ==========
    # If user mentions where they are
    for _, loc in DELIVERY_LOCATIONS.iterrows():
        if loc["location"].lower() in query_lower or any(word in query_lower for word in loc["location"].lower().split()):
            # Find restaurants closest to this location
            loc_lat, loc_lon = loc["lat"], loc["lon"]
            restaurant_distances = []
            
            for _, rest in RESTAURANTS.iterrows():
                distance = math.sqrt((loc_lat - rest["lat"])**2 + (loc_lon - rest["lon"])**2)
                restaurant_distances.append((rest["name"], rest["cuisine"], rest["rating"], distance))
            
            restaurant_distances.sort(key=lambda x: x[3])
            top_3 = restaurant_distances[:3]
            
            return f"""**You're at {loc['location']}! 📍**

**Nearest restaurants for quick delivery:**

{chr(10).join([f"{i+1}. **{r[0]}** ({r[1]}) - ⭐ {r[2]}/5.0" for i, r in enumerate(top_3)])}

⏱️ All deliver in 8-11 minutes to {loc['location']}

🛒 **Ready to order?** Head to the **Order Food** page and select **{loc['location']}** as your delivery location!"""
    
    # ========== RESTAURANT & MENU QUERIES ==========
    if any(word in query_lower for word in ["menu", "food", "restaurant", "eat", "order", "what can i"]):
        for restaurant in RESTAURANTS["name"].tolist():
            if restaurant.lower() in query_lower or any(word in query_lower for word in restaurant.lower().split()):
                menu_items = RESTAURANT_MENUS[restaurant]
                rest_info = RESTAURANTS[RESTAURANTS["name"] == restaurant].iloc[0]
                
                # Show full menu
                menu_text = "\n".join([f"• **{item}** - ${price:.2f}" for item, price in menu_items.items()])
                
                # Find closest pickup point
                rest_lat, rest_lon = rest_info["lat"], rest_info["lon"]
                closest_pickup = None
                min_distance = float('inf')
                
                for _, loc in DELIVERY_LOCATIONS.iterrows():
                    distance = math.sqrt((rest_lat - loc["lat"])**2 + (rest_lon - loc["lon"])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_pickup = loc["location"]
                
                return f"""**{restaurant} Menu** ⭐ {rest_info['rating']}/5.0

{menu_text}

📍 **Nearest Pickup:** {closest_pickup}
⏱️ **Delivery Time:** 8-11 minutes
💳 **Pay with Dining Dollars**

🛒 **Order now** on the **Order Food** page! 🚁"""
        
        # General restaurant list
        restaurant_list = "\n".join([
            f"• **{row['name']}** ({row['cuisine']}) - ⭐ {row['rating']}/5.0"
            for _, row in RESTAURANTS.iterrows()
        ])
        return f"""**Available Restaurants:**

{restaurant_list}

💡 **Want to see a menu?** Ask:
• "Show me the Chick-fil-A menu"
• "What does Chipotle have?"

🛒 Or visit the **Order Food** page to browse everything!"""
    
    # ========== CANCEL/MODIFY ORDER ==========
    if any(phrase in query_lower for phrase in ["cancel order", "cancel my order", "change order", "modify order"]):
        if st.session_state.active_orders:
            return """**Order Modifications**

⚠️ Orders cannot be canceled or modified once the drone is in flight.

**Need help?** Contact support or submit feedback:
• Go to **Feedback** page
• Or call Campus Dining: (555) 123-4567

💡 For future orders, double-check your items before checkout!"""
        else:
            return """You don't have any active orders to cancel. 

Place a new order anytime on the **Order Food** page! 🍽️"""
    
    # ========== PRICING & PAYMENT ==========
    if any(word in query_lower for word in ["price", "cost", "how much", "dining dollar", "payment", "pay"]):
        return """**Pricing & Payment 💳**

✅ **All prices shown in Dining Dollars**
🆓 **FREE drone delivery** - no extra fees!
💰 **Your balance:** Check the Order Food page

**How payment works:**
1. Add items to cart
2. See total at checkout
3. Dining Dollars auto-deducted
4. Get instant confirmation

All restaurant prices are the same as ordering in person!"""
    
    # ========== HOW IT WORKS ==========
    if any(phrase in query_lower for phrase in ["how", "work", "how does", "how do i"]):
        return """**How Drone Delivery Works 🚁**

**Step-by-step:**
1. 🍽️ Go to **Order Food** page
2. 📋 Choose restaurant & add items to cart
3. 📍 Select your nearest pickup point
4. 💳 Pay with Dining Dollars (no delivery fee!)
5. 🚁 Drone launches in ~3 minutes
6. 📱 Track live on **Live Deliveries** page
7. 📦 Pick up your food at chosen spot (~8 min)

**Features:**
✅ Real-time GPS tracking
✅ 8-11 minute delivery
✅ Safe, secure, climate-controlled
✅ AI-powered assistant (that's me!)

Ready to try it? Head to **Order Food**! 🎉"""
    
    # ========== PICKUP POINTS OVERVIEW ==========
    if any(word in query_lower for word in ["pickup point", "pickup spot", "pickup location", "delivery location"]):
        location_list = "\n".join([
            f"• **{row['location']}** - {row['type']}"
            for _, row in DELIVERY_LOCATIONS.iterrows()
        ])
        return f"""**Campus Pickup Points 📍**

{location_list}

**All locations have:**
✅ 24/7 security monitoring
💡 Well-lit areas
🚁 Drone-optimized landing zones
🎥 Surveillance cameras

💡 **Tip:** Choose the pickup point closest to where you'll be when your food arrives!

🗺️ See all locations on the **Live Deliveries** map."""
    
    # ========== DEFAULT HELPFUL RESPONSE ==========
    return """**Hi! I'm your Campus Drone Delivery Assistant 🤖**

**I can help you with:**

🍽️ **Restaurants & Menus**
• "Show me the Chick-fil-A menu"
• "Where can I get nuggets?"
• "What restaurants are available?"

📍 **Pickup Points**
• "Where do I get Chipotle from?"
• "I'm at North Hall, what's nearby?"
• "Which pickup point for my order?"

📦 **Order Status**
• "Where's my order?"
• "Track my delivery"
• "When will my food arrive?"

❓ **General Help**
• "How does this work?"
• "How much does delivery cost?"
• "Can I cancel my order?"

**Just ask me anything!** I'm here to help make your drone delivery experience smooth and easy. 🚁✨"""

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### 🚁 Campus Drone Delivery")
    
    page = st.radio("", ["Live Deliveries", "Order Food", "AI Assistant", "Feedback", "Admin Dashboard"])
    
    if page == "Live Deliveries":
        st.markdown("---")
        show_restaurants = st.checkbox("Restaurants", value=True)
        show_delivery_points = st.checkbox("Delivery Points", value=True)
        show_drones = st.checkbox("Drones", value=True)
        st.markdown("---")
        refresh_sec = st.slider("Refresh (sec)", 2, 10, 3)
        live_on = st.checkbox("Live update", value=True)

# ================ PAGE: LIVE DELIVERIES ================
if page == "Live Deliveries":
    st.markdown("### 🚁 Live Deliveries")
    
    layers_list = []
    
    # Draw delivery routes for active orders
    if st.session_state.active_orders:
        for order in st.session_state.active_orders:
            if order["status"] == "In Transit":
                route_path = [
                    [order["restaurant_lon"], order["restaurant_lat"]],
                    [order["delivery_lon"], order["delivery_lat"]]
                ]
                
                route_df = pd.DataFrame([{"path": route_path, "order_id": order["order_id"]}])
                
                route_line = pdk.Layer(
                    "PathLayer",
                    data=route_df,
                    get_path="path",
                    get_color=[33, 150, 243, 255],
                    width_min_pixels=6,
                    pickable=True,
                    cap_rounded=True,
                )
                
                layers_list.append(route_line)
    
    # Restaurants (Red)
    if show_restaurants:
        restaurants_df = create_restaurant_markers()
        
        restaurant_markers = pdk.Layer(
            "ScatterplotLayer",
            data=restaurants_df,
            get_position='[lon, lat]',
            get_radius=30,
            get_fill_color=[244, 67, 54, 255],
            stroked=True,
            get_line_color=[255, 193, 7],  # Gold outline for emphasis
            line_width_min_pixels=2,
            pickable=True,
            opacity=0.9,
        )
        
        restaurant_icons = pdk.Layer(
            "TextLayer",
            data=restaurants_df,
            get_position='[lon, lat]',
            get_text="'🍽️'",
            get_color=[255, 255, 255],
            get_size=24,
        )
        
        restaurant_labels = pdk.Layer(
            "TextLayer",
            data=restaurants_df,
            get_position='[lon, lat]',
            get_text='name',
            get_color=[255, 255, 255],
            get_size=12,
            get_pixel_offset=[0, 28],
            get_background_color=[244, 67, 54, 220],
            background=True,
            background_padding=[6, 3],
        )
        
        layers_list.extend([restaurant_markers, restaurant_icons, restaurant_labels])
    
    # Pickup Points (Green)
    if show_delivery_points:
        locations_df = create_location_markers()
        
        delivery_markers = pdk.Layer(
            "ScatterplotLayer",
            data=locations_df,
            get_position='[lon, lat]',
            get_radius=28,
            get_fill_color=[76, 175, 80, 255],
            stroked=True,
            get_line_color=[255, 193, 7],  # Gold outline for emphasis
            line_width_min_pixels=2,
            pickable=True,
            opacity=0.9,
        )
        
        delivery_icons = pdk.Layer(
            "TextLayer",
            data=locations_df,
            get_position='[lon, lat]',
            get_text="'📦'",
            get_color=[255, 255, 255],
            get_size=22,
        )
        
        delivery_labels = pdk.Layer(
            "TextLayer",
            data=locations_df,
            get_position='[lon, lat]',
            get_text='location',
            get_color=[255, 255, 255],
            get_size=11,
            get_pixel_offset=[0, 24],
            get_background_color=[76, 175, 80, 220],
            background=True,
            background_padding=[6, 3],
        )
        
        layers_list.extend([delivery_markers, delivery_icons, delivery_labels])
    
    # Active Drones
    drones_df = simulated_drones_df()
    
    if show_drones and not drones_df.empty:
        drone_markers = pdk.Layer(
            "ScatterplotLayer",
            data=drones_df,
            get_position='[lon, lat]',
            get_radius=35,
            get_fill_color=[33, 150, 243, 255],
            stroked=True,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=2,
            pickable=True,
        )
        
        drone_icons = pdk.Layer(
            "TextLayer",
            data=drones_df,
            get_position='[lon, lat]',
            get_text='icon',
            get_color=[255, 255, 255],
            get_size=24,
        )
        
        layers_list.extend([drone_markers, drone_icons])
    
    # Create exciting animated view for poster presentation
    view = pdk.ViewState(
        latitude=40.7470, 
        longitude=-73.9850, 
        zoom=15.2, 
        pitch=50,  # Angled view for 3D effect
        bearing=20  # Slight rotation for dynamic look
    )
    
    deck = pdk.Deck(
        map_provider="carto",
        map_style="dark",  # Dark style for dramatic poster effect
        initial_view_state=view,
        layers=layers_list,
        tooltip={
            "html": "<b style='font-size:14px'>{name}</b><br/><b style='color:#4CAF50'>{location}</b><br/>Order #{order_id}",
            "style": {
                "backgroundColor": "rgba(0, 0, 0, 0.9)",
                "color": "white",
                "fontSize": "13px",
                "padding": "10px 14px",
                "borderRadius": "8px",
                "border": "2px solid #FFC107"
            }
        }
    )
    
    col1, col2 = st.columns([7, 5])
    
    with col1:
        st.pydeck_chart(deck, use_container_width=True, height=520)
    
    with col2:
        st.markdown("#### 🚁 Active Deliveries")
        
        if st.session_state.active_orders:
            for order in st.session_state.active_orders:
                eta_min = int((order["eta"] - datetime.now()).total_seconds() / 60)
                
                if eta_min < 0:
                    eta_min = 0
                    order["status"] = "Delivered"
                elif (datetime.now() - order["placed_time"]).total_seconds() / 60 >= 3:
                    order["status"] = "In Transit"
                
                status_emoji = "👨‍🍳" if order["status"] == "Preparing" else "🚁" if order["status"] == "In Transit" else "✅"
                
                st.markdown(f"""
                **Order #{order['order_id']}** - ${order['total']:.2f}
                
                {status_emoji} **{order['status']}**
                
                🍽️ {order['restaurant']}  
                📍 → {order['location']}  
                ⏱️ ETA: **{eta_min} min**
                
                ---
                """)
        else:
            st.info("No active deliveries. Place an order to see live tracking!")
    
    if live_on and st.session_state.active_orders:
        time.sleep(refresh_sec)
        st.rerun()

# ================ PAGE: ORDER FOOD ================
elif page == "Order Food":
    st.markdown("### 🍽️ Order Food")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        selected_restaurant = st.selectbox("Restaurant", RESTAURANTS["name"].tolist())
        
        menu = RESTAURANT_MENUS[selected_restaurant]
        
        col_item, col_qty = st.columns([3, 1])
        
        with col_item:
            selected_item = st.selectbox("Item", list(menu.keys()))
        
        with col_qty:
            quantity = st.number_input("Qty", 1, 10, 1)
        
        if st.button("➕ Add to Cart"):
            st.session_state.cart_items.append({
                "item": selected_item,
                "quantity": quantity,
                "price": menu[selected_item],
                "total": menu[selected_item] * quantity
            })
            st.success(f"Added {quantity}x {selected_item}")
            st.rerun()
        
        st.markdown("---")
        st.markdown("#### Your Cart")
        
        if st.session_state.cart_items:
            cart_total = 0
            for idx, item in enumerate(st.session_state.cart_items):
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.write(f"{item['quantity']}x {item['item']}")
                with col_b:
                    st.write(f"${item['total']:.2f}")
                with col_c:
                    if st.button("🗑️", key=f"rm_{idx}"):
                        st.session_state.cart_items.pop(idx)
                        st.rerun()
                cart_total += item['total']
            
            st.write(f"**Total: ${cart_total:.2f}**")
            
            delivery_location = st.selectbox("Delivery Location", DELIVERY_LOCATIONS["location"].tolist())
            
            if st.button("🚁 Place Order", type="primary"):
                items_text = "\n".join([f"{i['quantity']}x {i['item']}" for i in st.session_state.cart_items])
                order = place_order(selected_restaurant, delivery_location, items_text, cart_total)
                
                # Store the route info for display
                rest_data = RESTAURANTS[RESTAURANTS["name"] == selected_restaurant].iloc[0]
                loc_data = DELIVERY_LOCATIONS[DELIVERY_LOCATIONS["location"] == delivery_location].iloc[0]
                
                st.session_state.last_order_route = {
                    "restaurant": selected_restaurant,
                    "restaurant_lat": rest_data["lat"],
                    "restaurant_lon": rest_data["lon"],
                    "pickup_spot": delivery_location,
                    "pickup_lat": loc_data["lat"],
                    "pickup_lon": loc_data["lon"],
                    "order_id": order["order_id"]
                }
                
                st.success(f"✅ Order #{order['order_id']} placed!")
                st.info(f"📍 **Go to {delivery_location}** to pick up your order!\n\n🗺️ View the delivery route on the Live Deliveries page.")
                st.session_state.cart_items = []
                st.balloons()
                time.sleep(3)
                st.rerun()
        else:
            st.info("Cart is empty")
    
    with col2:
        st.markdown("**Balance: $847.50**")
        
        # Show route visualization if user just placed an order
        if st.session_state.last_order_route:
            st.markdown("---")
            st.markdown("#### 📍 Your Delivery Route")
            
            route_info = st.session_state.last_order_route
            st.success(f"**Order #{route_info['order_id']}**")
            st.write(f"🍽️ From: **{route_info['restaurant']}**")
            st.write(f"📦 To: **{route_info['pickup_spot']}**")
            st.info("🗺️ View the live route on the **Live Deliveries** page!")
            
            if st.button("View Live Map", use_container_width=True):
                st.switch_page("pages/live_deliveries.py") if False else st.info("Go to Live Deliveries in sidebar")

# ================ PAGE: AI ASSISTANT ================
elif page == "AI Assistant":
    st.markdown("### 🤖 AI Assistant")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = generate_ai_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ================ PAGE: FEEDBACK ================
elif page == "Feedback":
    st.markdown("### 📝 Feedback")
    
    with st.form("feedback_form"):
        student_name = st.text_input("Name (optional)")
        student_email = st.text_input("Email (optional)")
        issue_category = st.selectbox("Category", ISSUE_CATEGORIES)
        description = st.text_area("Description")
        
        if st.form_submit_button("Submit"):
            if description:
                feedback_entry = {
                    "name": student_name or "Anonymous",
                    "email": student_email or "Not provided",
                    "category": issue_category,
                    "description": description
                }
                save_feedback(feedback_entry)
                st.success("Feedback submitted!")
            else:
                st.error("Please provide a description")

# ================ PAGE: ADMIN DASHBOARD ================
elif page == "Admin Dashboard":
    st.markdown("### 📊 Campus Drone Delivery Admin Dashboard")
    st.caption("Real-time analytics and service management")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = len(st.session_state.active_orders) + st.session_state.order_counter - 1
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_orders}</div>
            <div class="stat-label">Total Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_deliveries = len([o for o in st.session_state.active_orders if o["status"] == "In Transit"])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color: #2196F3;">{active_deliveries}</div>
            <div class="stat-label">Active Drones</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_feedback = len(st.session_state.feedback_data)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_feedback}</div>
            <div class="stat-label">Student Feedback</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        high_priority = sum(1 for f in st.session_state.feedback_data 
                           if f.get("ai_analysis", {}).get("priority") == "High")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color: #E31A1C;">{high_priority}</div>
            <div class="stat-label">High Priority Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Active deliveries overview
    st.markdown("#### 🚁 Active Deliveries")
    
    if st.session_state.active_orders:
        for order in st.session_state.active_orders:
            eta_min = int((order["eta"] - datetime.now()).total_seconds() / 60)
            
            if eta_min < 0:
                eta_min = 0
                order["status"] = "Delivered"
            elif (datetime.now() - order["placed_time"]).total_seconds() / 60 >= 3:
                order["status"] = "In Transit"
            
            status_color = "#FFC107" if order["status"] == "Preparing" else "#2196F3" if order["status"] == "In Transit" else "#4CAF50"
            
            col_a, col_b, col_c, col_d = st.columns([1, 2, 2, 1])
            
            with col_a:
                st.markdown(f"**#{order['order_id']}**")
            with col_b:
                st.write(f"{order['restaurant']}")
            with col_c:
                st.write(f"→ {order['location']}")
            with col_d:
                st.markdown(f"<span style='color:{status_color}'>{order['status']}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
    else:
        st.info("No active deliveries at the moment")
    
    # Feedback management
    if st.session_state.feedback_data:
        st.markdown("#### 📋 Student Feedback")
        
        feedback_df = pd.DataFrame([
            {
                "ID": f["id"],
                "Time": f["timestamp"],
                "Category": f["category"],
                "Priority": f["ai_analysis"]["priority"],
                "Status": f["status"]
            }
            for f in st.session_state.feedback_data
        ])
        
        st.dataframe(feedback_df, use_container_width=True, height=250)
        
        st.markdown("---")
        st.markdown("#### 🔍 Detailed Feedback Analysis")
        
        for feedback in reversed(st.session_state.feedback_data[-5:]):
            priority = feedback["ai_analysis"]["priority"]
            
            with st.expander(f"#{feedback['id']} - {feedback['category']} ({priority} Priority)"):
                col_a, col_b = st.columns([1, 1])
                
                with col_a:
                    st.markdown("**Student Feedback:**")
                    st.write(f"**From:** {feedback['name']}")
                    st.write(f"**Category:** {feedback['category']}")
                    st.write(f"**Status:** {feedback['status']}")
                    st.markdown("**Description:**")
                    st.write(feedback['description'])
                
                with col_b:
                    st.markdown("**🤖 AI Analysis:**")
                    st.info(feedback['ai_analysis']['ai_summary'])
                    
                    st.markdown("**💡 Recommendations:**")
                    for i, rec in enumerate(feedback['ai_analysis']['recommendations'], 1):
                        st.write(f"{i}. {rec}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Resolved", key=f"res_{feedback['id']}"):
                        feedback['status'] = "Resolved"
                        st.success("Marked resolved")
                        st.rerun()
                with col2:
                    if st.button("🔄 In Progress", key=f"prog_{feedback['id']}"):
                        feedback['status'] = "In Progress"
                        st.info("Status updated")
                        st.rerun()
                with col3:
                    if st.button("📧 Contact", key=f"email_{feedback['id']}"):
                        st.info(f"Email: {feedback['email']}")
        
        # Export options
        st.markdown("---")
        st.markdown("#### 📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Feedback (JSON)", use_container_width=True):
                json_data = json.dumps(st.session_state.feedback_data, indent=2)
                st.download_button(
                    "Download JSON",
                    json_data,
                    f"drone_delivery_feedback_{datetime.now().strftime('%Y%m%d')}.json",
                    "application/json"
                )
        
        with col2:
            if st.button("📊 Generate Report", use_container_width=True):
                report = f"""CAMPUS DRONE DELIVERY - ADMIN REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DELIVERY STATISTICS:
- Total Orders: {len(st.session_state.active_orders) + st.session_state.order_counter - 1}
- Active Deliveries: {len(st.session_state.active_orders)}
- Completed Deliveries: {st.session_state.order_counter - 1 - len(st.session_state.active_orders)}

FEEDBACK SUMMARY:
- Total Feedback: {len(st.session_state.feedback_data)}
- High Priority: {sum(1 for f in st.session_state.feedback_data if f.get('ai_analysis', {}).get('priority') == 'High')}
- Medium Priority: {sum(1 for f in st.session_state.feedback_data if f.get('ai_analysis', {}).get('priority') == 'Medium')}
- Low Priority: {sum(1 for f in st.session_state.feedback_data if f.get('ai_analysis', {}).get('priority') == 'Low')}

SERVICE LOCATIONS:
- Active Restaurants: {len(RESTAURANTS)}
- Pickup Points: {len(DELIVERY_LOCATIONS)}

CAMPUS COMPLIANCE: All operations meet university safety standards."""
                
                st.download_button(
                    "Download Report",
                    report,
                    f"drone_delivery_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    "text/plain"
                )
    else:
        st.info("No feedback data yet. Students can submit feedback on the Feedback page.")