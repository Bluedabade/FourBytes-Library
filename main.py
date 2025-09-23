import create  # 

def main():
    while True:
        print("\n===== Library Menu =====")
        print("1) Add Book")
        print("2) Add Member")
        print("3) View Books")
        print("4) View Members")
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
        elif choice == "0":
            print("Exiting program...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
