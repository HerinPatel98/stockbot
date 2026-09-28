from database import get_db_connection

def add_stock(product_name: str, quantity: int, unit_price: float = 0.0) -> str:
    """Add incoming stock to inventory or register a new product.
    
    Args:
        product_name: The descriptive title of the item/product.
        quantity: The positive number of units received.
        unit_price: Price per unit in dollars (optional, default 0.0).
    """
    clean_name = product_name.strip().title()
    if quantity <= 0:
        return "Failed: Quantity to add must be greater than zero."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quantity, unit_price FROM products WHERE name = ?", (clean_name,))
        row = cursor.fetchone()

        if row:
            new_qty = row[0] + quantity
            price = unit_price if unit_price > 0 else row[1]
            cursor.execute("UPDATE products SET quantity = ?, unit_price = ? WHERE name = ?", (new_qty, price, clean_name))
        else:
            new_qty = quantity
            cursor.execute("INSERT INTO products (name, quantity, unit_price) VALUES (?, ?, ?)", (clean_name, quantity, unit_price))

        cursor.execute(
            "INSERT INTO transactions (product_name, change_qty, action) VALUES (?, ?, 'RESTOCK')",
            (clean_name, quantity)
        )
        conn.commit()
    return f"Confirmed: Added {quantity} units to '{clean_name}'. Updated total stock: {new_qty}."

def reduce_stock(product_name: str, quantity: int) -> str:
    """Record a sale, dispatch, or write-off of existing stock.
    
    Args:
        product_name: The name of the product sold or dispatched.
        quantity: The positive number of units sold.
    """
    clean_name = product_name.strip().title()
    if quantity <= 0:
        return "Failed: Quantity to sell must be greater than zero."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM products WHERE name = ?", (clean_name,))
        row = cursor.fetchone()

        if not row:
            return f"Failed: Item '{clean_name}' does not exist in inventory records."
        
        current_stock = row[0]
        if current_stock < quantity:
            return f"Failed: Insufficient stock. Only {current_stock} units of '{clean_name}' available, but requested {quantity}."

        new_qty = current_stock - quantity
        cursor.execute("UPDATE products SET quantity = ? WHERE name = ?", (new_qty, clean_name))
        cursor.execute(
            "INSERT INTO transactions (product_name, change_qty, action) VALUES (?, ?, 'SALE')",
            (clean_name, -quantity)
        )
        conn.commit()
    return f"Confirmed: Recorded sale of {quantity} units of '{clean_name}'. Remaining stock: {new_qty}."

def query_stock(product_name: str = "") -> str:
    """Inspect current inventory levels for a specific product or view all products.
    
    Args:
        product_name: Specific product to look up. Leave empty to retrieve all stock.
    """
    clean_name = product_name.strip().title()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if clean_name:
            cursor.execute("SELECT name, quantity, unit_price FROM products WHERE name = ?", (clean_name,))
            row = cursor.fetchone()
            if row:
                return f"Product: {row[0]} | Current Stock: {row[1]} units | Price: ${row[2]:.2f}"
            return f"No records found for product '{clean_name}'."
        
        cursor.execute("SELECT name, quantity, unit_price FROM products ORDER BY name ASC")
        rows = cursor.fetchall()
        if not rows:
            return "Inventory is currently empty."
        
        items = [f"• {r[0]}: {r[1]} units (${r[2]:.2f})" for r in rows]
        return "Current Stock Levels:\n" + "\n".join(items)

# Explicit mapping of tool names for execution
TOOL_REGISTRY = {
    "add_stock": add_stock,
    "reduce_stock": reduce_stock,
    "query_stock": query_stock,
}