#code for the shop system
class Shop:
    def __init__(self):
        """Initialize the shop with basic items."""
        self.items = ["Health Potion", "Speed Boost", "New Weapon"]

    def display_items(self):
        """Display shop items (placeholder)."""
        for idx, item in enumerate(self.items, start=1):
            print(f"{idx}. {item}")

    def buy_item(self, item_number):
        """Handle item purchase (placeholder)."""
        if 0 < item_number <= len(self.items):
            print(f"You bought {self.items[item_number - 1]}!")
        else:
            print("Invalid selection.")
