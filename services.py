import sqlite3
from database import get_connection

def add_stock(product_name: str, quantity: int, unit_price: float = 0.0, client_id: int = 1) -> str:
    """Adds stock or registers an item scoped strictly to client_id."""
    conn = get_connection()
    cursor = conn.cursor()
    clean_name = product_name.strip()

    cursor.execute(
        "SELECT id, stock, price FROM products WHERE client_id = ? AND LOWER(name) = LOWER(?)",
        (client_id, clean_name)
    )
    row = cursor.fetchone()

    if row:
        p_id, cur_stock, cur_price = row
        new_stock = cur_stock + quantity
        new_price = unit_price if unit_price > 0 else cur_price
        cursor.execute("UPDATE products SET stock = ?, price = ? WHERE id = ?", (new_stock, new_price, p_id))
    else:
        cursor.execute(
            "INSERT INTO products (client_id, name, stock, price) VALUES (?, ?, ?, ?)",
            (client_id, clean_name, quantity, unit_price)
        )

    cursor.execute(
        "INSERT INTO transactions (client_id, product_name, quantity_change, action_type) VALUES (?, ?, ?, 'RESTOCK')",
        (client_id, clean_name, quantity)
    )
    conn.commit()
    conn.close()
    return f"Successfully added {quantity} units of '{clean_name}'."

def reduce_stock(product_name: str, quantity: int, client_id: int = 1) -> str:
    """Deducts stock scoped strictly to client_id."""
    conn = get_connection()
    cursor = conn.cursor()
    clean_name = product_name.strip()

    cursor.execute(
        "SELECT id, stock FROM products WHERE client_id = ? AND LOWER(name) = LOWER(?)",
        (client_id, clean_name)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return f"Error: Product '{clean_name}' does not exist in your catalog."

    p_id, cur_stock = row
    if cur_stock < quantity:
        conn.close()
        return f"Declined: Insufficient stock. You only have {cur_stock} units of '{clean_name}' available."

    new_stock = cur_stock - quantity
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, p_id))
    cursor.execute(
        "INSERT INTO transactions (client_id, product_name, quantity_change, action_type) VALUES (?, ?, ?, 'SALE')",
        (client_id, clean_name, -quantity)
    )
    conn.commit()
    conn.close()
    return f"Successfully recorded sale of {quantity} units of '{clean_name}'."

def query_stock(product_name: str = "", client_id: int = 1) -> str:
    """Queries stock catalog strictly for client_id. Accepts empty string or None."""
    conn = get_connection()
    cursor = conn.cursor()

    name_clean = (product_name or "").strip()

    if name_clean:
        cursor.execute(
            "SELECT name, stock, price FROM products WHERE client_id = ? AND LOWER(name) = LOWER(?)",
            (client_id, name_clean)
        )
        rows = cursor.fetchall()
    else:
        cursor.execute(
            "SELECT name, stock, price FROM products WHERE client_id = ? ORDER BY name ASC",
            (client_id,)
        )
        rows = cursor.fetchall()

    conn.close()
    if not rows:
        return "No inventory items found matching your catalog query."

    return "\n".join([f"• {r[0]}: {r[1]} units (Unit Price: ${r[2]:.2f})" for r in rows])

TOOL_REGISTRY = {
    "add_stock": add_stock,
    "reduce_stock": reduce_stock,
    "query_stock": query_stock
}
