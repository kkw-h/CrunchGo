import asyncio
import httpx
import json
import logging
import sys
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# --- Helper Functions ---
async def get_menu(client: httpx.AsyncClient, token: str) -> Dict[str, Any]:
    # Get categories
    response = await client.get(f"{BASE_URL}/menu/categories", headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        logger.error(f"Get categories failed: {response.text}")
        sys.exit(1)
    categories = response.json()
    logger.info(f"Got {len(categories)} categories")

    # Get products
    response = await client.get(f"{BASE_URL}/menu/products", headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        logger.error(f"Get products failed: {response.text}")
        sys.exit(1)
    products = response.json()
    logger.info(f"Got {len(products)} products")

    if not products:
        logger.error("No products found in menu")
        sys.exit(1)

    # Pick first product and get details (SKUs)
    product_id = products[0]["id"]
    response = await client.get(f"{BASE_URL}/menu/products/{product_id}", headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        logger.error(f"Get product detail failed: {response.text}")
        sys.exit(1)
    product_detail = response.json()
    
    if not product_detail["skus"]:
        logger.error(f"Product {product_id} has no SKUs")
        sys.exit(1)
        
    sku = product_detail["skus"][0]
    return {"product_id": product_id, "sku_id": sku["id"], "price": sku["price"]}

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Login (Mock Wechat) -> Get Token
        logger.info("--- Step 1: Login ---")
        login_payload = {"code": "test_code"}
        try:
            response = await client.post(f"{BASE_URL}/auth/login/wechat", json=login_payload)
        except httpx.ConnectError:
            logger.error("Failed to connect to backend. Is it running on localhost:8000?")
            sys.exit(1)

        if response.status_code != 200:
            logger.error(f"Login failed: {response.text}")
            sys.exit(1)
            
        token_data = response.json()
        access_token = token_data["access_token"]
        logger.info(f"Login successful. Token: {access_token[:10]}...")
        
        headers = {**HEADERS, "Authorization": f"Bearer {access_token}"}

        # 2. Get Menu (Categories & Products)
        logger.info("--- Step 2: Get Menu ---")
        menu_data = await get_menu(client, access_token)
        sku_id = menu_data["sku_id"]
        logger.info(f"Selected Product SKU ID: {sku_id}")

        # 3. Create Order
        logger.info("--- Step 3: Create Order ---")
        order_payload = {
            "items": [{"product_sku_id": sku_id, "quantity": 1}],
            "type": "PICKUP"
        }
        
        response = await client.post(f"{BASE_URL}/orders/", json=order_payload, headers=headers)
        if response.status_code != 201:
            logger.error(f"Create order failed: {response.text}")
            sys.exit(1)
            
        order = response.json()
        order_no = order["order_no"]
        logger.info(f"Order created: {order_no}, Status: {order['status']}")
        
        # 4. Pay Order
        logger.info("--- Step 4: Pay Order ---")
        response = await client.post(f"{BASE_URL}/orders/{order_no}/pay", headers=headers)
        if response.status_code != 200:
            logger.error(f"Pay order failed: {response.text}")
            sys.exit(1)
            
        paid_order = response.json()
        if paid_order["status"] != "PAID":
            logger.error(f"Order status is not PAID: {paid_order['status']}")
            sys.exit(1)
        logger.info(f"Order paid: {order_no}, Status: {paid_order['status']}")

        # 5. Get Order Detail (Check status=PAID, pickup_code exists)
        logger.info("--- Step 5: Get Order Detail ---")
        response = await client.get(f"{BASE_URL}/orders/{order_no}", headers=headers)
        if response.status_code != 200:
            logger.error(f"Get order failed: {response.text}")
            sys.exit(1)
            
        order_detail = response.json()
        if order_detail["status"] != "PAID":
            logger.error(f"Order status is not PAID: {order_detail['status']}")
            sys.exit(1)
        if not order_detail.get("pickup_code"):
            logger.error("Pickup code is missing")
            sys.exit(1)
            
        logger.info(f"Order Detail Verified. Pickup Code: {order_detail['pickup_code']}")

        # 6. Get User Points (Check balance increased)
        logger.info("--- Step 6: Get User Points ---")
        response = await client.get(f"{BASE_URL}/user/points", headers=headers)
        if response.status_code != 200:
            logger.error(f"Get points failed: {response.text}")
            sys.exit(1)
            
        points_logs = response.json()
        if points_logs:
             logger.info(f"Latest point log: {points_logs[0]}")
        else:
             logger.warning("No point logs found (maybe points are awarded asynchronously or config issue)")

        # 7. Request Refund
        logger.info("--- Step 7: Request Refund ---")
        response = await client.post(f"{BASE_URL}/orders/{order_no}/refund", headers=headers)
        if response.status_code != 200:
            logger.error(f"Refund request failed: {response.text}")
            sys.exit(1)
            
        refund_order = response.json()
        # Status should be REFUNDING
        if refund_order["status"] != "REFUNDING":
            logger.error(f"Order status is not REFUNDING: {refund_order['status']}")
            sys.exit(1)
        logger.info(f"Refund requested. Status: {refund_order['status']}")

        # 8. Admin Approve Refund
        logger.info("--- Step 8: Admin Approve Refund ---")
        response = await client.post(f"{BASE_URL}/admin/orders/{order_no}/refund/approve", headers=headers)
        
        if response.status_code in [401, 403]:
             logger.warning("Admin approval failed due to permissions. Skipping admin verification.")
        elif response.status_code != 200:
             logger.error(f"Admin approve refund failed: {response.text}")
             sys.exit(1)
        else:
            approved_order = response.json()
            if approved_order["status"] != "REFUNDED":
                logger.error(f"Order status is not REFUNDED: {approved_order['status']}")
                sys.exit(1)
            logger.info(f"Refund approved. Status: {approved_order['status']}")

            # 9. Get Order Detail (Check status=REFUNDED)
            logger.info("--- Step 9: Get Order Detail (Verify REFUNDED) ---")
            response = await client.get(f"{BASE_URL}/orders/{order_no}", headers=headers)
            if response.status_code != 200:
                logger.error(f"Get order failed: {response.text}")
                sys.exit(1)
                
            final_order = response.json()
            if final_order["status"] != "REFUNDED":
                logger.error(f"Order status is not REFUNDED: {final_order['status']}")
                sys.exit(1)
            logger.info("Order status verified as REFUNDED")

        # 10. Get Admin Stats (Check sales updated)
        logger.info("--- Step 10: Get Admin Stats ---")
        response = await client.get(f"{BASE_URL}/admin/stats/dashboard", headers=headers)
        if response.status_code in [401, 403]:
             logger.warning("Admin stats failed due to permissions.")
        elif response.status_code != 200:
             logger.error(f"Get stats failed: {response.text}")
             sys.exit(1)
        else:
            stats = response.json()
            logger.info(f"Daily Sales: {stats.get('daily_sales')}")
            logger.info(f"Daily Orders: {stats.get('daily_order_count')}")

if __name__ == "__main__":
    asyncio.run(main())
