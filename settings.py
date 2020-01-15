"""
Settings location
"""

PAGE_INDEXES = {
    "unlock_page": 0,
    "users_page": 1,
    "main_page": 2,
    "inventory_page": 3,
    "fruit_page": 4,
    "vegetable_page": 5,
    "dairy_page": 6,
    "meat_page": 7,
    "spread_page": 8,
    "sauce_page": 9,
    "drink_page": 10,
    "other_page": 11,
    "expirations_page": 12,
    "scan_page": 13,
    "custom_product_page": 14,
    "custom_product_expiration_page": 15,
    "custom_product_category_page": 16,
}

PLATFORM_API = None

SCANNER_PIN = 27
IR_PIN = 17

KEYBOARD_KEYS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'space', 'delete']

CATEGORIES = [
    "fruit",
    "vegetable",
    "dairy",
    "meat",
    "spread",
    "sauce",
    "drink",
    "other"
]

OTHER_LIST_WIDGETS_PREFIXES = [
    "expirations",
    "scanner"
]

ALL_SCROLLABLE_LIST_WIDGETS_PREFIXES = CATEGORIES + OTHER_LIST_WIDGETS_PREFIXES
