
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk



class GUI(): 
    def __init__(self):
        
        self.root = tk.Tk()
        self.root.title("Main GUI")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        self.window = ttk.Frame(self.notebook)
        self.notebook.add(self.window, text="Petrinet")
        
        self.empty_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.empty_frame, text="Empty Tab")
        
        self.window.photo = None  # Initialize as None
        

    
    def create_gui(self):
        # Create the top frame
        top_frame = ttk.Frame(self.window)
        top_frame.grid(row=0, column=1, padx=10, pady=10)
        
        # Create the central frame 
        central_frame = ttk.Frame(self.window)
        central_frame.grid(row=1, column=1, padx=10, pady=10)
 
        # Create the frame to the left
        left_frame = ttk.Frame(self.window)
        left_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ns")
 
        # Create the frame to the right
        right_frame = ttk.Frame(self.window)
        right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="ns")
 
        # Create another frame below the three defined frames
        bottom_frame = ttk.Frame(self.window)
        bottom_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
 
        # Configure grid row and column weights to make central frame expand
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        
        
        def update_image(event=None):
            # Define the fixed size for the image    
            fixed_width = 800
            fixed_height = 600

            # Update the image displayed in the GUI
            image = Image.open("step.JPG")
            resized_image = image.resize((fixed_width, fixed_height))
            photo = ImageTk.PhotoImage(resized_image)

            # Remove any existing label before creating a new one
            for widget in central_frame.winfo_children():
                widget.destroy()
        
            label = tk.Label(central_frame, image=photo)
            label.image = photo
            label.pack()
        
        # Bind the <Configure> event to the central_frame
        central_frame.bind("<Configure>", update_image)
        # Call the update_image function to display the initial image
        update_image()
        

        def backward_button_click():
            print("backward button clicked!")
        def forward_button_click():
            print("forward button clicked!")
        
        def pause_button_click():
            print("pause button clicked!")
        def play_button_click():
            print("play button clicked!")
            
            
        def next_button_click():
             print("next button clicked!")
        def previous_button_click():
             print("previous button clicked!")
             
        
        def reset_button_click():
            print("Reset button clicked!")
        def relode_button_click():
            print("Relode button clicked!")
            for widget in central_frame.winfo_children():
                widget.destroy()
            update_image() 
            


        # Create a frame to hold the buttons
        buttons_frame = tk.Frame(bottom_frame)
        buttons_frame.pack(padx=10, pady=10 ,anchor="w")

        # Load the custom button images
        backward_image = ImageTk.PhotoImage(file=r"icons\backward.png")
        forward_image = ImageTk.PhotoImage(file=r"icons\forward.png")
        pause_image = ImageTk.PhotoImage(file=r"icons\pause.png")
        play_image = ImageTk.PhotoImage(file=r"icons\play.png")
        next_image = ImageTk.PhotoImage(file=r"icons\next.png")
        previous_image = ImageTk.PhotoImage(file=r"icons\previous.png")
        relode_image = ImageTk.PhotoImage(file=r"icons\repeat.png")   
        reset_image = ImageTk.PhotoImage(file=r"icons\reset.png")

        # Create the buttons with the custom images
        backward_button = ttk.Button(buttons_frame, image=backward_image, command=backward_button_click)
        forward_button = ttk.Button(buttons_frame, image=forward_image, command=forward_button_click)
        pause_button = ttk.Button(buttons_frame, image=pause_image, command=pause_button_click)
        play_button = ttk.Button(buttons_frame, image=play_image, command=play_button_click)     
        next_button = ttk.Button(buttons_frame, image=next_image, command=next_button_click) 
        previous_button = ttk.Button(buttons_frame, image=previous_image, command=previous_button_click)  
        relode_button = ttk.Button(buttons_frame, image=relode_image, command=relode_button_click)   
        reset_button = ttk.Button(buttons_frame, image=reset_image, command=reset_button_click)      
        
        # Keep a reference to the image
        backward_button.image = backward_image 
        forward_button.image = forward_image 
        pause_button.image = pause_image        
        play_button.image = play_image   
        next_button.image = next_image
        previous_button.image = previous_image
        relode_button.image = relode_image
        reset_button.image = reset_image
        
        # pack buttons in the GUI 
        backward_button.pack(side="left", padx=5, pady=5)
        forward_button.pack(side="left", padx=5, pady=5)
        pause_button.pack(side="left", padx=5, pady=5)
        play_button.pack(side="left", padx=5, pady=5)
        previous_button.pack(side="left", padx=5, pady=5)
        next_button.pack(side="left", padx=5, pady=5)
        relode_button.pack(side="right", padx=5, pady=5)    
        reset_button.pack(side="right", padx=50, pady=5)


    def __call__(self):
        self.create_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)  # Bind the close event
        self.root.mainloop()

    def on_window_close(self):
        self.root.quit()  # Quit the main event loop
        self.root.destroy()  # Destroy the root window


if __name__ == "__main__":
    gui = GUI()
    gui()
    




    

    

    