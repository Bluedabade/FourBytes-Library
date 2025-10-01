from module import books, members, borrows, report

def menu_books():
    while True:
        print("\n--- Manage Books ---")
        print("1) Add Book")
        print("2) View Books")
        print("3) Update Book")
        print("4) Delete Book")
        print("0) Back to Main Menu")
        c = input("Select option: ").strip()
        if c == "1":
            books.add_book()
        elif c == "2":
            books.view_books()
        elif c == "3":
            books.update_book()
        elif c == "4":
            books.delete_book()
        elif c == "0":
            break
        else:
            print("Invalid choice.")

def menu_members():
    while True:
        print("\n--- Manage Members ---")
        print("1) Add Member")
        print("2) View Members")
        print("3) Update Member")
        print("4) Delete Member")
        print("0) Back to Main Menu")
        c = input("Select option: ").strip()
        if c == "1":
            members.add_member()
        elif c == "2":
            members.view_members()
        elif c == "3":
            members.update_member()
        elif c == "4":
            members.delete_member()
        elif c == "0":
            break
        else:
            print("Invalid choice.")

def menu_borrows():
    while True:
        print("\n--- Manage Borrows/Returns ---")
        print("1) Add Borrow")
        print("2) Return Book")
        print("3) View Borrows")
        print("0) Back to Main Menu")
        c = input("Select option: ").strip()
        if c == "1":
            borrows.add_borrow()
        elif c == "2":
            borrows.return_book()
        elif c == "3":
            borrows.view_borrows()
        elif c == "0":
            break
        else:
            print("Invalid choice.")

def main():
    while True:
        print("\n===== Library Management System =====")
        print("1) Manage Books")
        print("2) Manage Members")
        print("3) Manage Borrows/Returns")
        print("4) Generate Report")
        print("0) Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            menu_books()
        elif choice == "2":
            menu_members()
        elif choice == "3":
            menu_borrows()
        elif choice == "4":
            report.generate_report()
        elif choice == "0":
            print("Exiting program...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
