from calculations import *

import tkinter as tk
from tkinter import ttk


from tkinter import messagebox
import queue
from PIL import Image, ImageTk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import queue
import decimal


class LoadingScreen(tk.Canvas):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.config(bg='#00356B', highlightbackground='#39FF14',
                    highlightthickness=5)
        self.create_widgets()

    def create_widgets(self):
        # Creates several widgets, including text labels, rectangles, and an animated image.
        self.create_text(200, 90, text='BenJY', font=('Arial', 25))
        self.create_text(
            200, 130, text='A Projectile Motion Simulation', font=('Arial', 20))
        self.create_rectangle(50, 300, 350, 320, disabledfill='#39FF14',
                              width=1, activeoutline='#39FF14', outline='#39FF14')
        self.progress = self.create_rectangle(
            50, 180, 50, 200, width=0, fill='#FF10F0')
        self.loading_texts = ['Launching...', 'Please wait...',
                             'Almost there...', 'Just a moment...', 'Hang on...']
        self.loading_text = self.create_text(
            200, 310, text=self.loading_texts[0], font=('Arial', 12))
        self.images = [Image.open(
            f'images/loading/loading{i}.gif') for i in range(100)]
        self.icon_images = [image.resize((120, 120)) for image in self.images]
        self.photo_images = [ImageTk.PhotoImage(
            image) for image in self.icon_images]
        self.image_index = 0
        self.image_object = self.create_image(
            200, 220, image=self.photo_images[self.image_index])
        # Creates two queues, one for animating the image and the other for updating the loading text.
        self.animate_image_queue = queue.Queue()
        self.loading_text_queue = queue.Queue()
        self.animate_image_queue.put(0)
        self.loading_text_queue.put(0)
        self.progress_value = 0
        self.after(10, self.animate_image)
        self.after(1000, self.update_loading_text)

    def update_loading_text(self):
        try:
            self.loading_text_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            # Use of linear queue 
            # Moves the first item in a list called loading_texts to the end of the list
            # Updates the text displayed on a Canvas object called loading_text with the new first item in the list.
            self.loading_texts.append(self.loading_texts.pop(0))
            self.itemconfig(self.loading_text, text=self.loading_texts[0])
        finally:
            self.loading_text_queue.put(0)
        self.after(1000, self.update_loading_text)

    def animate_image(self):
        try:
            self.animate_image_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            # Increments the index of the current image being displayed if an item was successfully retrieved
            self.image_index += 1
            if self.image_index == len(self.icon_images):
                self.image_index = 0
            self.itemconfig(self.image_object,
                            image=self.photo_images[self.image_index])
            # Updates the position of a progress bar on the Canvas object based on the current progress
            self.coords(self.progress, 51, 302, 50 +
                        self.get_progress_width(), 320)
        finally:
            # Adds 0 to the animate_image_queue queue if the current image index is less than the length of the list of images minus 1 (to prevent an infinite loop).
            if self.image_index < len(self.icon_images) - 1:
                self.animate_image_queue.put(0)
        self.after(10, self.animate_image)

    def set_progress(self, value):
        # Sets and updates the progress value for the progress bar widget.
        self.progress_value = value
        self.update_idletasks()
        if self.progress_value == 100:
            self.animate_image_queue.put(None)
            self.master.after(1000, self.master.destroy)
        else:
            self.animate_image_queue.put(0)

    def get_progress_width(self):
        return (self.progress_value / 100) * 300


def run_splash_screen():
    root = tk.Tk()
    root.geometry('400x400')
    root.overrideredirect(True)

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the x and y coordinates to center the window
    x = (screen_width // 2) - (400 // 2)
    y = (screen_height // 2) - (400 // 2)

    # Set the window position
    root.geometry('+{}+{}'.format(x, y))

    splash = LoadingScreen(root, width=400, height=400)
    splash.pack()

    for i in range(101):
        splash.set_progress(i)
        splash.after(50)
        splash.update_idletasks()
        root.update()

    root.mainloop()

class PhysicsExplanation:
    def __init__(self, master):
        self.master = master
        self.master.geometry('500x400')
        self.master.title("Physics Explanation")
        
        # Create the notebook widget
        self.notebook = ttk.Notebook(self.master)
        
        # Create tabs and add them to the notebook
        self.tab1 = tk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Actual Path")
        
        self.tab2 = tk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Predicted Path")
        
        self.tab3 = tk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Diagram")

        self.tab4 = tk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="Fun Facts!")
        
        # Add content to the tabs
        self.add_tab1_content()
        self.add_tab2_content()
        self.add_tab3_content()
        self.add_tab4_content()
        
        # Pack the notebook widget
        self.notebook.pack(expand=True, fill='both')
        
    def add_tab1_content(self):
        # Add content to the first tab
        label = tk.Label(self.tab1, text="Without air resistance (actual path),\nthe path of a projectile appears to be a\nperfect negative quadratic (parabolic).", font=("Arial", 12))
        label.place(relx=0.5, rely=0.5, anchor="center")
        
    def add_tab2_content(self):
        # Add content to the second tab
        label = tk.Label(self.tab2, text="As a projectile moves through the air,\nit is slowed down by air resistance.\nAir resistance decreases the horizontal component of a projectile.\n\nWith air resistance (predicted path), the path of a projectile\nappears to be “squashed” in the horizontal direction.\nThe maximum height, horizontal distance travelled (range)\nand the velocity of the projectile are all reduced.\n\nThe effect of air resistance is relatively small,\nhence it is usually neglected when solving\nphysics and mathematics problems at A-Level.", font=("Arial", 12))
        label.place(relx=0.5, rely=0.5, anchor="center")
        
    def add_tab3_content(self):
        # Add content to the third tab
        # Load the image
        image = Image.open('images\diagram.jpg')
        photo = ImageTk.PhotoImage(image)
        # Create a label for the image
        image_label = tk.Label(self.tab3, image=photo)
        image_label.image = photo
        image_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def add_tab4_content(self):
        # Add content to the fourth tab
        texts = ["Factors that affect the amount of\nair resistance acting on a projectile:\n", 
                "1. Surface to volume ratio of the projectile.\n The larger the surface to volume ratio,\nthe greater the effect of air resistance on the object.", 
                "2. The surface of the projectile.\n The rougher the surface, the greater the air resistance.", 
                "3. Speed of the projectile.\n The greater the speed of the object, the greater the air resistance.", 
                "4. Mass of the projectile.\n The smaller the mass of the object,\nthe larger the effect of air resistance on it."]
        for text in texts:
            label = tk.Label(self.tab4, text=text, font=("Arial", 12))
            label.pack(padx=10, pady=10)


class Display:
    def __init__(self):
        # Composition
        self.projectile = ProjectileMotion()

    def horizontal_distance_prompt(self):
        initial_angle = round(self.projectile.convert_radians_to_degrees(self.projectile.theta), 2)
        initial_velocity = round(self.projectile.initial_velocity, 2)
        time_of_flight = round(self.projectile.get_time_of_flight(), 2)
        hdistance = self.projectile.hdistance_travelled

        # Calculate the horizontal distance travelled by the projectile.
        # Round horizontal distance travelled to exactly 2 decimal places.
        hdistance_decimal = decimal.Decimal(hdistance)
        hdistance_rounded = hdistance_decimal.quantize(decimal.Decimal('0.00'))

        # Create a Tkinter window
        hdprompt = tk.Tk()
        hdprompt.title('Horizontal Distance Estimation')

        # Create a function to handle closing the window
        def on_closing():
            if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
                messagebox.showinfo(
                    "Exit", f"Initial angle = {initial_angle} degrees\nInitial velocity = {initial_velocity} m/s\nPredicted horizontal distance = {hdistance_rounded} m\nTime of flight = {time_of_flight} s\n\nGENERATING GRAPH...")
                hdprompt.destroy()
                self.graph()

        # Set the on_closing function to handle the close event
        hdprompt.protocol("WM_DELETE_WINDOW", on_closing)

        # Create a label with the initial angle and velocity values
        label = tk.Label(
            hdprompt, text=f"\nCalculate the horizontal distance travelled by the projectile.\nGive your answer accurate to two decimal places.\n\nInitial angle = {initial_angle} degrees\nInitial velocity = {initial_velocity} m/s\nTime of flight = {time_of_flight} s\n")
        label.pack(pady=10)

        # Create a function to check if the entered value is correct
        def check_answer():
            # Get the entered value and check if it is correct
            entered_value = entry.get()
            if not entered_value:
                messagebox.showerror(
                    "Invalid input", "'Horizontal Distance' is a required field.")
                return
            try:
                float(entered_value)
            except ValueError:
                messagebox.showerror(
                    "Invalid input", "The value of horizontal distance should be numerical.\n\nGive your answer accurate to two decimal places!")
                return
            if str(entered_value) == str(hdistance_rounded):
                # Display success message and close the window
                messagebox.showinfo(
                    "Correct", "Correct value of horizontal distance entered!\n\nGENERATING GRAPH...")
                hdprompt.destroy()
                self.graph()
            else:
                # Display error message
                messagebox.showerror(
                    "Incorrect", "The value of horizontal distance entered is incorrect.")

        # Create a label and entry box for the horizontal distance value
        horizontal_distance_label = tk.Label(
            hdprompt, text="Horizontal Distance")
        horizontal_distance_label.pack()
        entry = tk.Entry(hdprompt)
        entry.pack(pady=10)

        # Create a button to check the entered value
        check_button = tk.Button(
            hdprompt, text="Check Answer", command=check_answer)
        check_button.pack(pady=10)

        # Create a button to quit the program
        def quit_program():
            # Change this text
            if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
                messagebox.showinfo(
                    "Exit", f"Initial angle = {initial_angle} degrees\nInitial velocity = {initial_velocity} m/s\nPredicted horizontal distance = {hdistance_rounded} m\nTime of flight = {time_of_flight} s\n\nGENERATING GRAPH...")
                hdprompt.destroy()
                self.graph()

        exit_button = tk.Button(hdprompt, text="Exit", command=quit_program)
        exit_button.pack(pady=10)

        # Run the Tkinter event loop
        hdprompt.mainloop()

    def graph(self):
        # Displays the graph
        self.projectile.plot_trajectories()

    def physics_explanations(self):
        # Creates a tkinter window to display the physics explanations.
        root = tk.Tk()
        app = PhysicsExplanation(root)
        root.mainloop()

