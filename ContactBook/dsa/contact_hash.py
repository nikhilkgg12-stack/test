# ==============================================================================
# DATA STRUCTURES & ALGORITHMS (DSA): HASH TABLE / DICTIONARY
# ==============================================================================
# Project: Contact Book / Address Manager
# Concept: Hashing & Fast Lookup using Python Dictionary
# ==============================================================================
# 
# WHY HASHING?
# ------------
# In standard lists/arrays, finding a contact by phone number requires checking
# each element one by one from start to end (Linear Search: O(N) time complexity).
# If there are 1,000,000 contacts, it may take up to 1,000,000 steps.
#
# With Hashing (Hash Table / Python Dictionary):
# A hash function calculates a unique memory index for each key (phone number).
# This gives AVERAGE TIME COMPLEXITY:
#   - Insertion: O(1) [Constant Time]
#   - Search:    O(1) [Constant Time]
#   - Deletion:  O(1) [Constant Time]
#
# Even with 1,000,000 contacts, a search takes approximately 1 single step!
# ==============================================================================

# Global in-memory hash table for storing contacts
# Key: Phone Number (string) -> Value: Contact Dictionary / Information
contacts_hash = {}


def add_contact_to_hash(phone, contact_data):
    """
    Inserts a contact into the hash table.
    Time Complexity: O(1) average.
    
    :param phone: String representing the phone number (Unique Key)
    :param contact_data: Dictionary containing details of the contact
    """
    # Clean and store the phone number as a string key
    key = str(phone).strip()
    contacts_hash[key] = contact_data
    return True


def search_contact(phone):
    """
    Searches for a contact by phone number in the hash table.
    Time Complexity: O(1) average.
    
    :param phone: Phone number to search
    :return: Contact data if found, None otherwise
    """
    key = str(phone).strip()
    # Direct O(1) hash lookup using Python dictionary 'in' operator
    if key in contacts_hash:
        return contacts_hash[key]
    return None


def delete_contact_from_hash(phone):
    """
    Removes a contact from the hash table by phone number.
    Time Complexity: O(1) average.
    
    :param phone: Phone number to remove
    :return: True if deleted, False if not found
    """
    key = str(phone).strip()
    if key in contacts_hash:
        del contacts_hash[key]
        return True
    return False


def get_all_from_hash():
    """
    Returns all contacts stored in the hash table.
    """
    return list(contacts_hash.values())


def load_contacts_to_hash(contact_list):
    """
    Populates the hash table using contacts fetched from the MySQL database.
    Useful for caching database records into memory for rapid searches.
    """
    contacts_hash.clear()
    for contact in contact_list:
        if "phone" in contact and contact["phone"]:
            add_contact_to_hash(contact["phone"], contact)


# ==============================================================================
# DEMONSTRATION & TESTING (Can be run directly in College Viva)
# Run: python dsa/contact_hash.py
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DSA DEMO: CONTACT LOOKUP USING HASHING (DICTIONARY)")
    print("=" * 60)

    # 1. Adding contacts (Insertion: O(1))
    print("\n1. Adding contacts to Hash Table...")
    add_contact_to_hash("9876543210", {"name": "Rahul Sharma", "group": "College", "email": "rahul@gmail.com"})
    add_contact_to_hash("9123456780", {"name": "Aman Kumar", "group": "Friends", "email": "aman@gmail.com"})
    add_contact_to_hash("9988776655", {"name": "Priya Patel", "group": "Work", "email": "priya@example.com"})
    print("Current Hash Table Keys:", list(contacts_hash.keys()))

    # 2. Searching contacts (Lookup: O(1))
    search_query = "9876543210"
    print(f"\n2. Searching for contact with phone: {search_query}")
    result = search_contact(search_query)
    if result:
        print("Found in O(1) time:", result)
    else:
        print("Contact not found.")

    # 3. Searching for a non-existent contact
    unknown_query = "9999999999"
    print(f"\n3. Searching for non-existent contact: {unknown_query}")
    print("Result:", search_contact(unknown_query))

    # 4. Deleting a contact (Deletion: O(1))
    print(f"\n4. Deleting contact with phone: {search_query}")
    delete_contact_from_hash(search_query)
    print("Hash Table after deletion:", list(contacts_hash.keys()))
    print("=" * 60)
