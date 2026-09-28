import sqlite3
import difflib
import re
from database import get_connection

def normalize_text(text: str) -> str:
    """Removes non-alphanumeric noise, strips plural 's'/'es', and lowercases."""
    t = text.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    # Strip basic plural suffixes for matching
    if t.endswith('es') and len(t) > 3:
        t = t[:-2]
    elif t.endswith('s') and len(t) > 2:
        t = t[:-1]
    return re.sub(r'\s+', ' ', t).strip()

def find_canonical_sku(input_name: str, client_id: int):
    """
    Finds the exact or best fuzzy-matched product name already in the database.
    Returns (canonical_name, match_type) where match_type is 'EXACT', 'FUZZY', or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE client_id = ?", (client_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return input_name.strip(), None

    existing_names = [r[0] for r in rows]

    # 1. Exact case-insensitive check
    for name in existing_names:
        if name.strip().lower() == input_name.strip().lower():
            return name, "EXACT"

    # 2. Normalized check (ignoring hyphens, spaces, and plural endings)
    norm_input = normalize_text(input_name)
    for name in existing_names:
        if normalize_text(name) == norm_input:
            return name, "FUZZY"

    # 3. High-confidence string similarity matching (threshold 0.78)
    matches = difflib.get_close_matches(input_name.strip().lower(), [n.lower() for n in existing_names], n=1, cutoff=0.78)
    if matches:
        matched_lower = matches[0]
        for name in existing_names:
            if name.lower() == matched_lower:
                return name, "FUZZY"

    return input_name.strip(), None

def add_stock(product_name: str, quantity: int, unit_price: float = 0.0, client_id: int = 1, is_new_sku: bool = False) -> str:
    """
    Safely restocks existing items or creates a new SKU if explicitly authorized.
    Automatically resolves minor misspellings and plurals.
    """
    conn = get_connection()
    cursor = conn.cursor()
    clean_input = product_name.strip()

    # Resolve against existing SKUs
    canonical_name, match_type = find_canonical_sku(clean_input, client_id)

    cursor.execute(
        "SELECT id, stock, price FROM products WHERE client_id = ? AND name = ?",
        (client_id, canonical_name)
    )
    row = cursor.fetchone()

    if row:
        p_id, cur_stock, cur_price = row
        new_stock = cur_stock + quantity
        new_price = unit_price if unit_price > 0 else cur_price
        cursor.execute("UPDATE products SET stock = ?, price = ? WHERE id = ?", (new_stock, new_price, p_id))
        cursor.execute(
            "INSERT INTO transactions (client_id, product_name, quantity_change, action_type) VALUES (?, ?, ?, 'RESTOCK')",
            (client_id, canonical_name, quantity)
        )
        conn.commit()
        conn.close()

        msg = f"Successfully added {quantity} units to '{canonical_name}'."
        if match_type == "FUZZY":
            msg += f" (Resolved from '{clean_input}')"
        return msg

    # Product does not exist
    if not is_new_sku:
        conn.close()
        return (
            f"Notice: Product '{clean_input}' was not found in your catalog. "
            f"If you want to register a brand new item, please specify: 'Add new SKU {clean_input}'."
        )

    # Authorized new SKU registration
    cursor.execute(
        "INSERT INTO products (client_id, name, stock, price) VALUES (?, ?, ?, ?)",
        (client_id, clean_input, quantity, unit_price)
    )
    cursor.execute(
        "INSERT INTO transactions (client_id, product_name, quantity_change, action_type) VALUES (?, ?, ?, 'RESTOCK')",
        (client_id, clean_input, quantity)
    )
    conn.commit()
    conn.close()
    return f"Successfully registered new catalog product '{clean_input}' with {quantity} units at ${unit_price:.2f} each."

def reduce_stock(product_name: str, quantity: int, client_id: int = 1) -> str:
    """Deducts stock scoped strictly to client_id with fuzzy name resolution."""
    conn = get_connection()
    cursor = conn.cursor()
    clean_input = product_name.strip()

    canonical_name, match_type = find_canonical_sku(clean_input, client_id)

    cursor.execute(
        "SELECT id, stock FROM products WHERE client_id = ? AND name = ?",
        (client_id, canonical_name)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return f"Error: Product '{clean_input}' does not exist in your catalog."

    p_id, cur_stock = row
    if cur_stock < quantity:
        conn.close()
        return f"Declined: Insufficient stock. You only have {cur_stock} units of '{canonical_name}' available."

    new_stock = cur_stock - quantity
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, p_id))
    cursor.execute(
        "INSERT INTO transactions (client_id, product_name, quantity_change, action_type) VALUES (?, ?, ?, 'SALE')",
        (client_id, canonical_name, -quantity)
    )
    conn.commit()
    conn.close()

    msg = f"Successfully recorded sale of {quantity} units of '{canonical_name}'."
    if match_type == "FUZZY":
        msg += f" (Resolved from '{clean_input}')"
    return msg

def query_stock(product_name: str = "", client_id: int = 1) -> str:
    """Queries stock catalog strictly for client_id with fuzzy name resolution."""
    conn = get_connection()
    cursor = conn.cursor()
    name_clean = (product_name or "").strip()

    if name_clean:
        canonical_name, _ = find_canonical_sku(name_clean, client_id)
        cursor.execute(
            "SELECT name, stock, price FROM products WHERE client_id = ? AND name = ?",
            (client_id, canonical_name)
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

def delete_stock(product_name: str, client_id: int = 1, confirm: bool = False) -> str:
    """
    Safely deletes a product SKU from catalog with explicit confirmation and audit logging.
    """
    clean_input = product_name.strip()
    canonical_name, match_type = find_canonical_sku(clean_input, client_id)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, stock, price FROM products WHERE client_id = ? AND name = ?",
        (client_id, canonical_name)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return f"Error: Product '{clean_input}' was not found in your catalog."

    p_id, cur_stock, cur_price = row

    if not confirm:
        conn.close()
        valuation = cur_stock * cur_price
        return (
            f"⚠️ CONFIRMATION REQUIRED: Deleting '{canonical_name}' will permanently purge "
            f"{cur_stock} units worth ${valuation:,.2f} from your catalog. "
            f"To execute, please confirm by stating: 'Confirm delete product {canonical_name}'."
        )

    # 1. Log decommissioning in immutable audit ledger
    cursor.execute(
        "INSERT INTO transactions (client_id, product_name, quantity_change, action_type) VALUES (?, ?, ?, 'DECOMMISSION')",
        (client_id, canonical_name, -cur_stock)
    )

    # 2. Purge from products catalog
    cursor.execute("DELETE FROM products WHERE id = ?", (p_id,))
    conn.commit()
    conn.close()

    msg = f"🗑️ Permanently removed '{canonical_name}' ({cur_stock} units liquidated) from catalog."
    if match_type == "FUZZY":
        msg += f" (Resolved from '{clean_input}')"
    return msg

TOOL_REGISTRY = {
    "add_stock": add_stock,
    "reduce_stock": reduce_stock,
    "query_stock": query_stock,
    "delete_stock": delete_stock
}
