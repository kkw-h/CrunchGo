import httpx
import time
import hashlib
import logging
from app.core.config import settings
from app.models.order import Order

logger = logging.getLogger(__name__)

class PrinterService:
    @staticmethod
    async def print_order(order: Order):
        """
        Format order details and send to printer API.
        """
        # 1. Format the receipt content
        content = PrinterService._format_receipt(order)

        if not settings.PRINTER_USER or not settings.PRINTER_SN:
            logger.warning("Printer settings not configured. Logging receipt content instead:")
            logger.warning(f"\n{content}")
            return

        # 2. Prepare API parameters (Mock implementation for Feie/Yilianyun)
        # Real implementation would require specific API endpoint and signature generation
        # e.g. http://api.feieyun.cn/Api/Open/
        
        api_url = "http://api.feieyun.cn/Api/Open/"
        user = settings.PRINTER_USER
        ukey = settings.PRINTER_UKEY
        sn = settings.PRINTER_SN
        stime = str(int(time.time()))
        
        # Signature: sha1(user + ukey + stime)
        sig_str = f"{user}{ukey}{stime}"
        sig = hashlib.sha1(sig_str.encode("utf-8")).hexdigest()

        payload = {
            "user": user,
            "stime": stime,
            "sig": sig,
            "apiname": "Open_printMsg",
            "sn": sn,
            "content": content,
            "times": "1" # Print 1 copy
        }

        # 3. Send Request
        try:
            async with httpx.AsyncClient() as client:
                # In a real scenario, we would post to the API
                # response = await client.post(api_url, data=payload)
                # result = response.json()
                
                # Mocking the response for now to avoid actual network errors with invalid creds
                logger.info(f"Sending print request for Order {order.order_no} to {api_url}")
                logger.info(f"Payload: {payload}")
                
                # Simulate success
                logger.info("Print command sent successfully (Mock).")
                
        except Exception as e:
            logger.error(f"Failed to print order {order.order_no}: {e}")

    @staticmethod
    def _format_receipt(order: Order) -> str:
        """
        Format order into a printable string.
        """
        # Define some formatting constants
        line_width = 32
        separator = "-" * line_width
        
        lines = []
        lines.append(f"<center>{settings.PROJECT_NAME}</center>")
        lines.append(separator)
        lines.append(f"Order No: {order.order_no}")
        lines.append(f"Time: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(separator)
        
        # Table Header
        # Using simplified formatting. 
        # Real printers often support tags like <BR>, <CB>, etc.
        lines.append("Item             Qty   Price")
        lines.append(separator)
        
        for item in order.items:
            # Simple truncation/padding logic
            name = item.product_name_snapshot[:16].ljust(16)
            qty = f"x{item.quantity}".center(5)
            price = f"{item.price_snapshot:.2f}".rjust(8)
            lines.append(f"{name}{qty}{price}")
            
            # If specs exist, print them on next line
            if item.specs_snapshot:
                # Basic cleaning of JSON string for display if needed
                # For now just printing the raw string or simplified
                lines.append(f"  {item.specs_snapshot}")

        lines.append(separator)
        lines.append(f"Total:                 {order.total_amount:.2f}")
        lines.append(separator)
        lines.append("<center>Thank you!</center>")
        
        return "\n".join(lines)
