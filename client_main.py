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
            row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew"  # Change columnspan to 3 and sticky to "nsew"
        )

        # Also fix the column configuration to distribute space properly
        self.left_frame.grid_columnconfigure(0, weight=1)  # Contacts label column
        self.left_frame.grid_columnconfigure(1, weight=1)  # Create Group button column
        self.left_frame.grid_columnconfigure(2, weight=1)  # Broadcast button column

        # This for loop displays all contacts and retreives unicast chat history
        self.contacts = client.get_contacts()
        self.groups = client.get_user_groups()
        self.chat_history = dict() # {'user1':{'user1':'msg11', 'user2':'msg12',...,username:'msg1n'}, user2:..., group1:...}
        
        for contact in self.contacts:
            contact_btn = ctk.CTkButton(
                self.contacts_frame,
                text=contact,
                command=lambda c=contact: self.select_contact(c),
            )
            contact_btn.pack(padx=5, pady=5, fill="x")
            
            self.chat_history[contact] = client.retrieve_chat_history(contact, 'unicast')
            
        # Create group chats and retreive group history
        for group in self.groups:
            group_button = ctk.CTkButton(
                self.contacts_frame,
                text=group,
                command=lambda g=group: self.select_contact(g),
            )
            group_button.pack(padx=5, pady=5, fill="x")
            
            self.chat_history[group] = client.retrieve_chat_history(group, 'multicast')     
             
        # Retreive Broadcast history
        self.broadcast_history = client.retrieve_chat_history(receiver_username=None, chat_type='broadcast') 
        print(self.chat_history)
        # --------------------------
        #   Right Frame: Chat Area
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
        
        # Setup message callbacks and start listening for messages
        self.setup_message_callbacks()
        
    def setup_message_callbacks(self):
        # Setup callbacks for messages
        def on_message_received(sender, message):
            # Update UI if we're in the chat with this sender
            if self.selected_contact == sender:
                self.add_message(message=message, sender=sender)
            # You might want to add a notification system for messages from other contacts
        
        def on_group_message_received(group, sender, message):
            # Update UI if we're in the group chat
            if self.selected_contact == group:
                self.add_message(message=message, sender=sender)
            # You might want to add a notification system for messages in other groups
        
        # Set the callbacks on the client
        client.message_callback = on_message_received
        client.group_message_callback = on_group_message_received
        
        # Start the listening thread
        client.start_listening()

    def create_group(self):
        # First, prompt the user to enter a group name
        group_name = ctk.CTkInputDialog(
            title="Create Group", text="Enter the name of the group:"
        ).get_input()

        if not group_name:
            messagebox.showwarning("Warning", "Group name cannot be empty.")
            return

        # Create a custom dialog to select contacts
        select_members_dialog = ctk.CTkToplevel(self)
        select_members_dialog.title(f"Add Members to {group_name}")
        select_members_dialog.geometry("300x400")
        select_members_dialog.resizable(False, False)
        select_members_dialog.grab_set()  # Make it modal

        # Label
        ctk.CTkLabel(select_members_dialog, text="Select contacts to add:").pack(pady=10)

        # Frame for contacts
        contacts_frame = ctk.CTkScrollableFrame(select_members_dialog, width=250, height=280)
        contacts_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Create checkboxes for each contact
        contact_vars = {}
        for contact in self.contacts:
            var = ctk.IntVar(value=0)
            contact_vars[contact] = var
            ctk.CTkCheckBox(contacts_frame, text=contact, variable=var).pack(pady=3, anchor="w")

        # Add selected users to group and close dialog
        def confirm_selection():
            selected_contacts = [contact for contact, var in contact_vars.items() if var.get() == 1]
            
            if not selected_contacts:
                messagebox.showwarning("Warning", "Please select at least one contact.")
                return

            try:
                # Call the client method to create a group and add members
                if client.create_group(group_name, selected_contacts):
                    # Add the group to the UI
                    group_button = ctk.CTkButton(
                        self.contacts_frame,
                        text=f"Group: {group_name}",  # Prefix with "Group:" to differentiate
                        command=lambda g=group_name: self.select_contact(g),
                    )
                    group_button.pack(padx=5, pady=5, fill="x")
                    
                    # Initialize an empty chat history for the group
                    self.groups.append(group_name)
                    self.chat_history[group_name] = []
                    
                    messagebox.showinfo("Success", f"Group '{group_name}' created successfully!")
                    select_members_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to create group.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create group: {e}")
            
            select_members_dialog.destroy()

        # Buttons
        buttons_frame = ctk.CTkFrame(select_members_dialog)
        buttons_frame.pack(pady=10, fill="x")
        
        ctk.CTkButton(
            buttons_frame, text="Cancel", command=select_members_dialog.destroy
        ).pack(side="left", padx=10, pady=5, expand=True)
        
        ctk.CTkButton(
            buttons_frame, text="Create Group", command=confirm_selection
        ).pack(side="right", padx=10, pady=5, expand=True)

    def open_broadcast_chat(self):
        self.selected_contact = 'broadcast'
        # Set the chat title to "Broadcast"
        self.chat_title_label.configure(text="Broadcast Chat")

        # Clear existing chat messages
        for widget in self.chat_display.winfo_children():
            widget.destroy()

        if self.broadcast_history:
            for message_dict in self.broadcast_history:
                for sender, message in message_dict.items():
                    self.add_message(message=message, sender=sender) if sender != client.username else self.add_message(message=message, sender='me')

    def select_contact(self, contact):
        self.selected_contact = contact
        self.chat_title_label.configure(text=f"Chat with {contact}")

        # Clear existing chat messages
        for widget in self.chat_display.winfo_children():
            widget.destroy()

        # {'user1':{'user1':'msg11', 'user2':'msg12',...,username:'msg1n'}, user2:..., group1:...}
        # self.chat_history[contact] 
        # self.add_message('Hello there!')
        # self.add_message('Hey! How are you?', sender='me')
        
        if self.chat_history[contact]:
            for message_dict in self.chat_history[contact]:
                for sender, message in message_dict.items():
                    self.add_message(message=message, sender=sender) if sender != client.username else self.add_message(message=message, sender='me')
        

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
                wraplength=300,
                justify='left',
            )
            message_label.pack(side="right", padx=10)
        else:
            
            username_label = ctk.CTkLabel(
            message_frame,
            text=sender,
            bg_color='transparent',
            font=("Helvetica", 10),  # Smaller font for username
            text_color="#888888",    # Gray color for username
            anchor="w",              # Left-aligned text
        )
            username_label.pack(side="top", anchor="w", padx=10, pady=(2, 0))
            
            # Other user's messages are left-aligned
            message_label = ctk.CTkLabel(
                message_frame,
                text=message,
                fg_color="#1c8018",
                corner_radius=5,
                anchor="w",
                wraplength=300,
                justify='left',
            )
            message_label.pack(side="left", padx=10)

    def send_message(self):
        msg = self.message_entry.get()
        if not msg or not self.selected_contact:
            return
            
        success = False
        
        try:
            if self.selected_contact in self.contacts:  # Unicast message
                success = client.send_unicast(self.selected_contact, msg=msg)
            elif self.selected_contact in self.groups:  # Multicast message
                success = client.send_multicast(self.selected_contact, msg=msg)
            elif self.selected_contact == 'broadcast':  # Broadcast message
                success = client.send_broadcast(msg=msg)
                
            if success:
                self.add_message(msg, sender="me")
                self.message_entry.delete(0, ctk.END)
            else:
                messagebox.showerror('Error', 'Failed to send message')
        except Exception as e:
            messagebox.showerror('Error', f'Error sending message: {str(e)}')

    def attach_file(self):
        print("Attach file button clicked")


if __name__ == "__main__":
    login_app = LoginSignupApp()
    login_app.mainloop()
