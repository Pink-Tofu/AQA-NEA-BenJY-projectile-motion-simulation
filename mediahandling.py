import tkinter as tk
import cv2
from os.path import exists
import PIL
from PIL import Image, ImageTk

import numpy as np
import sys

class Video:
    def __init__(self):
        self.ok = False
        # Private attributes
        self.__centroid_coords = []
        self.__radius_values = []
        
        self.video_path, self.ready = self.vid_input()
        if self.ready == False:
            self.webcam_preview()
        else:
            self.detect_ball_vid()

    def get_radius_values(self):
        # Getter method for retrieving list of radius values
        if len(self.__radius_values) == 0:
            print('No projectile detected! Please relaunch the program.')
            sys.exit(0)

        return self.__radius_values

    def get_centroid_coords(self):
        # Getter method for retrieving list of centroid values
        return self.__centroid_coords

    @staticmethod
    def vid_input():
        FileExists = False
        while FileExists != True:
            print('Type in the name of the video file you wish to upload.')
            print('Press \'W\' if you wish to access the webcam instead.')
            # Gets user input for simulation mode
            inp = input()
            
            if inp == 'W':
                # Initialise video feed from webcam
                vid_inp = cv2.VideoCapture(0)
                FileExists = True
                ready = False
            else:
                file_name = f'videos\{inp}.mov'
                # Check if file exists
                FileExists = exists(file_name)
                if FileExists == True:
                    # Initialise video feed from video file
                    vid_inp = cv2.VideoCapture(file_name)
                    print('Showing video feed. Click window or press any key to stop.')
                else:
                    # Displays erorr message for when file entered does not exist
                    print('')
                    print('Invalid command or file does not exist (cAsE sEnSiTiVe!).')
                    print('')
                ready = True
                
        return vid_inp, ready

    def ok_button_pressed(self):
        self.ok = True

    def webcam_preview(self):
        root = tk.Tk()
        root.title("Video Feed Preview")

        # Create canvas to display video feed
        canvas = tk.Canvas(root, width=640, height=480)
        canvas.pack()

        # Add label for instructions to press OK button
        label = tk.Label(root, text="Please position your webcam. Press OK when ready to detect the projectile.")
        label.pack()

        # Create OK button
        ok_button = tk.Button(root, text="OK", command=lambda:[root.destroy(), self.ok_button_pressed()])
        ok_button.pack()

        # Capture video feed and display on canvas
        while not self.ok:
            ret, frame = self.video_path.read()
            frame = cv2.flip(frame, 1)
            if not ret:
                break

            # Convert frame to RGB and resize for display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))

            # Display frame on canvas
            photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo

            # Update tkinter window
            root.update()


        self.detect_ball_webcam()

    def detect_ball_webcam(self):
        # Define the range of colour for the ball in HSV space
        lower_bound = np.array([29, 86, 6])
        upper_bound = np.array([64, 255, 255])

        # Create a Tkinter window
        root = tk.Tk()
        root.title("Ball Detector")

        # Create a canvas to display the video feed
        canvas_width = 640
        canvas_height = 480
        canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
        canvas.pack()

        # Create a "Done" button
        def on_done():
            # Close the OpenCV window and release the video capture
            cv2.destroyAllWindows()
            self.video_path.release()
            # Close the Tkinter window
            root.destroy()

        done_button = tk.Button(root, text="Done", command=on_done)
        done_button.pack()

        while True:
            # Read a frame from the webcam
            ret, frame = self.video_path.read()
            frame = cv2.flip(frame, 1)

            # Check if video feed has ended
            if not ret:
                print("Video feed ended")
                break

            # Convert the frame to HSV colour space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Threshold the HSV image to get only ball colours
            mask = cv2.inRange(hsv, lower_bound, upper_bound)

            # Perform a series of morphological operations to remove noise and close gaps in the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # Find contours in the mask
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            # Loop over the contours
            for c in cnts:
                # Compute the minimum enclosing circle and centroid for the contour
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                centre = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # Only proceed if the radius is large enough
                if radius > 10:
                    self.__centroid_coords.append(centre)
                    self.__radius_values.append(radius)

                    # Draw the circle and centroid on the frame
                    cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
                    cv2.circle(frame, centre, 8, (0, 0, 255), cv2.FILLED)

                self.show_centroids(frame, self.__centroid_coords)

            # Show the frame on the Tkinter canvas
            if frame is not None:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgTk = ImageTk.PhotoImage(image=img)
                canvas.create_image(0, 0, anchor="nw", image=imgTk)
                root.update()

    def detect_ball_vid(self):
        # Define the range of colour for the ball in HSV space
        lower_bound = np.array([29, 86, 6])
        upper_bound = np.array([64, 255, 255])

        # Set the window properties
        cv2.namedWindow("Video Feed", cv2.WINDOW_NORMAL)

        while True:
            # Read a frame from the webcam
            ret, frame = self.video_path.read()
            
            # Check if video feed has ended
            if not ret:
                print("Video feed ended")
                break

            # Get the original size of the frame
            height, width, _ = frame.shape

            # Calculate the aspect ratio of the frame
            aspect_ratio = width / height

            # Resize the window to match the aspect ratio of the frame
            cv2.resizeWindow("Video Feed", int(600 * aspect_ratio), 600)

            # Convert the frame to HSV colour space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Threshold the HSV image to get only ball colours
            mask = cv2.inRange(hsv, lower_bound, upper_bound)

            # Perform a series of morphological operations to remove noise and close gaps in the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # Find contours in the mask
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            
            # Loop over the contours
            for c in cnts:
                # Compute the minimum enclosing circle and centroid for the contour
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                centre = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                # Only proceed if the radius is large enough
                if radius > 10:
                    self.__centroid_coords.append(centre)
                    self.__radius_values.append(radius)
                    
                    # Draw the circle and centroid on the frame
                    cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
                    cv2.circle(frame, centre, 8, (0, 0, 255), cv2.FILLED)

                self.show_centroids(frame, self.__centroid_coords)
            
            # Show the frame
            try:
                if frame is not None:
                    cv2.imshow("Video Feed", frame)
                    cv2.waitKey(100)
            except:
                print('No video feed detected.')

        # Destroys all windows
        cv2.destroyAllWindows()

    def show_centroids(self, frame, centroids):
        # Draw accumulated centroids on current frame
        trace_colour = 255
        for i in centroids:
            cv2.circle(frame, (i[0], i[1]), 6, (0, trace_colour, 0), cv2.FILLED)
            if trace_colour < 100:
                trace_colour = 255
            trace_colour -= 1

