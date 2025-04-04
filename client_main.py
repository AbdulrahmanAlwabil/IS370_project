import customtkinter as ctk
from tkinter import messagebox
from client.client import Client

# Initialize the customtkinter appearance
ctk.set_appearance_mode("Dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme(
    "dark-blue"
)  # Available themes: "blue" (default), "green", "dark-blue"

client = Client()

class LoginSignupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login / Signup")
        self.geometry("400x300")
        self.resizable(False, False)

        # Configure grid layout for the main window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Frame for login/signup
        self.frame = ctk.CTkFrame(self)
        self.frame.pack()

        # Username entry
        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.frame, placeholder_text="Password", show="*"
        )
        self.password_entry.pack(pady=10)

        # Login button
        self.login_button = ctk.CTkButton(self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        # Signup button
        self.signup_button = ctk.CTkButton(
            self.frame, text="Signup", command=self.signup
        )
        self.signup_button.pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        response = client.authenticate_user(username, password)
        
        
        # Add your login logic here
        if 'AUTH' in response:
            self.destroy()
            app = MessengerApp()
            app.mainloop()
        elif 'DECL' in response:
            messagebox.showerror('Error', 'Password is incorrect')
        else:
            messagebox.showerror("Error", "Please fill both username and password")

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        response = client.create_user(username, password)
        
        # Add your signup logic here
        if 'AUTH' in response:
            messagebox.showinfo("Success", "Signup successful! Please login.")
        elif 'DECL' in response:
            messagebox.showerror("Error", "Username is taken.")
        else:
            messagebox.showerror('Error', 'Please fill both username and password')


class MessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Instant Messenger")
        self.geometry("800x600")
        self.resizable(False, False)

        # Configure grid layout for the main window (2 columns)
        self.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_columnconfigure(1, weight=3)

        # ---------------------------
        # Left Frame: Contacts Panel
        # ---------------------------
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Title for contacts
        self.contacts_label = ctk.CTkLabel(
            self.left_frame, text="Contacts", font=("Helvetica", 16)
        )
        self.contacts_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Button to create a group
        self.create_group_button = ctk.CTkButton(
            self.left_frame, text="Create Group", command=self.create_group
        )
        self.create_group_button.grid(row=0, column=1, padx=2, pady=2, sticky="e")

        # Button to broadcast messages
        self.broadcast_button = ctk.CTkButton(
            self.left_frame, text="Broadcast", command=self.open_broadcast_chat
        )
        self.broadcast_button.grid(row=0, column=2, padx=2, pady=2, sticky="e")

        # Scrollable frame for the list of contacts
        self.contacts_frame = ctk.CTkScrollableFrame(
            self.left_frame, width=180, height=500
        )
        self.contacts_frame.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nswe"
        )

        
        self.contacts = client.get_contacts() or [] 
        for contact in self.contacts:
            contact_btn = ctk.CTkButton(
                self.contacts_frame,
                text=contact,
                command=lambda c=contact: self.select_contact(c),
            )
            contact_btn.pack(padx=5, pady=5, fill="x")

        # --------------------------
        # Right Frame: Chat Area
        # --------------------------
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=0)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Label showing the selected contact's name (or instruction to select one)
        self.chat_title_label = ctk.CTkLabel(
            self.right_frame, text="Select a contact to chat", font=("Helvetica", 16)
        )
        self.chat_title_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Scrollable frame to display chat messages
        self.chat_display = ctk.CTkScrollableFrame(self.right_frame, height=400)
        self.chat_display.grid(row=1, column=0, padx=10, pady=5, sticky="nswe")

        # Bottom frame contains the message entry and the buttons
        self.bottom_frame = ctk.CTkFrame(self.right_frame)
        self.bottom_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # Entry widget for typing messages
        self.message_entry = ctk.CTkEntry(
            self.bottom_frame, placeholder_text="Type your message here..."
        )
        self.message_entry.grid(
            row=0, column=0, padx=5, pady=5, sticky="ew", columnspan=2
        )

        # Button to send the message
        self.send_button = ctk.CTkButton(
            self.bottom_frame, text="Send", command=self.send_message
        )
        self.send_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Button to attach an image or video
        self.attach_button = ctk.CTkButton(
            self.bottom_frame, text="Attach", command=self.attach_file
        )
        self.attach_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Currently selected contact (None initially)
        self.selected_contact = None

    def create_group(self):
        # Prompt the user to enter a group name
        group_name = ctk.CTkInputDialog(
            title="Create Group", text="Enter the name of the group:"
        ).get_input()

        if group_name:
            try:
                from database.db_manager import create_group

                # Call the create_group function from db_manager.py
                create_group(group_name)
                messagebox.showinfo("Success", f"Group '{group_name}' created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create group: {e}")
        else:
            messagebox.showwarning("Warning", "Group name cannot be empty.")

    def open_broadcast_chat(self):
        # Set the chat title to "Broadcast"
        self.chat_title_label.configure(text="Broadcast Chat")

        # Clear existing chat messages
        for widget in self.chat_display.winfo_children():
            widget.destroy()

        # Optionally, you can add logic here to load previous broadcast messages in the future
        print("Opened broadcast chat.")

    def select_contact(self, contact):
        self.selected_contact = contact
        self.chat_title_label.configure(text=f"Chat with {contact}")

        # Clear existing chat messages
        for widget in self.chat_display.winfo_children():
            widget.destroy()

        # Optionally, populate with a dummy conversation
        self.add_message(f"Hello! This is {contact}.", sender="other")
        self.add_message("Hi! How are you?", sender="me")

    def add_message(self, message, sender="other"):

        # Create a container frame for the message bubble
        message_frame = ctk.CTkFrame(self.chat_display)
        message_frame.pack(fill="x", padx=5, pady=2)

        if sender == "me":
            # User's messages are right-aligned
            message_label = ctk.CTkLabel(
                message_frame,
                text=message,
                fg_color="#284b9e",
                corner_radius=5,
                anchor="e",
            )
            message_label.pack(side="right", padx=10)
        else:
            # Other user's messages are left-aligned
            message_label = ctk.CTkLabel(
                message_frame,
                text=message,
                fg_color="#1c8018",
                corner_radius=5,
                anchor="w",
            )
            message_label.pack(side="left", padx=10)

    def send_message(self):
        msg = self.message_entry.get()
        if msg and self.selected_contact:
            self.add_message(msg, sender="me")
            self.message_entry.delete(0, ctk.END)
            # Place your functionality for sending the message here

    def attach_file(self):
        # Place your functionality for attaching an image or video here
        print("Attach file button clicked")


if __name__ == "__main__":
    login_app = LoginSignupApp()
    login_app.mainloop()
