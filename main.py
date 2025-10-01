import create  # ใช้ฟังก์ชันใน create.py

def main():
    while True:
        print("\n===== Library Menu =====")
        print("1) Add Book")
        print("2) Add Member")
        print("3) View Books")
        print("4) View Members")
        print("5) Search Book by ID")
        print("6) Search Member by ID")
        print("7) Update Book")
        print("8) Update Member")
        print("9) Delete Book")
        print("10) Delete Member")
        print("0) Exit")
        choice = input("Select option: ")

        if choice == "1":
            create.add_book()
        elif choice == "2":
            create.add_member()
        elif choice == "3":
            create.view_books()
        elif choice == "4":
            create.view_members()
        elif choice == "5":
            create.search_book()
        elif choice == "6":
            create.search_member()
        elif choice == "7":
            create.update_book()
        elif choice == "8":
            create.update_member()
        elif choice == "9":
            create.delete_book()
        elif choice == "10":
            create.delete_member()
        elif choice == "0":
            print("Exiting program...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
