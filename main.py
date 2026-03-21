import customtkinter as ctk

root = ctk.CTk()
#root.resizable(False, False)
root.geometry("800x800")

diceResultLabel = ctk.CTkLabel(root)
diceResultLabel.place(relx=0.5, rely=0.5, anchor="center")

typingDisplayFrame = ctk.CTkFrame(root)
typingDisplayFrame.place(relx=0.5, rely=0.5)
typingDisplayFrame.config()

root.mainloop()