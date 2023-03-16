import numpy as np
from scipy.optimize import curve_fit
import math

import matplotlib.pyplot as plt

from mediahandling import *


class Calculate:
    def __init__(self):
        self.num_stds = 3

    # Removes anomalies from a list of values.
    def remove_list_anomalies(self, list_of_values):
        # Returns an empty list if original list is empty
        if len(list_of_values) == 0:
            return []
        else:
            # Gets mean of values in the list
            mean = sum(list_of_values) / len(list_of_values)
            # Calculates standard deviation of the values in the list
            std_dev = (sum((x - mean)**2 for x in list_of_values) /
                       len(list_of_values))**0.5
            #  Removes any values that are more than self.num_stds standard deviations away from the mean.
            return [x for x in list_of_values if abs(x - mean) < self.num_stds * std_dev]

    def get_average(self, list_of_values):
        # Returns 0 if original list is empty
        if len(list_of_values) == 0:
            return 0
        # Returns the mean of the values in the list
        else:
            return sum(list_of_values) / len(list_of_values)

    def estimate_initial_gradient(self, xlist, ylist):
        # Calculates the gradient between the first and fifth points.
        dx = xlist[0] - xlist[4]
        dy = ylist[0] - ylist[4]
        gradient = dy / dx

        return gradient

    def get_curve_function_coeffs(self, degree, xlist, ylist):
        # Converts the two lists of x and y coordinates into numpy arrays
        x_data = np.array(xlist)
        y_data = np.array(ylist)

        # Define the function to fit
        def func(x, *params):
            return np.polyval(params, x)

        # Initial guess for the parameters
        p0 = np.ones(degree + 1)

        # Perform the curve fitting
        coeffs, _ = curve_fit(func, x_data, y_data, p0=p0)

        # Return the coefficients of the polynomial curve
        return coeffs

    def get_pixel_to_real_world_conversion_ratio(self, pixel_units, real_world_objects):

        Valid = False
        while not Valid:
            try:
                # Prompts user to enter the measurement of a real-world object in real-world units
                real_units = float(
                    input(f"Enter the {real_world_objects} in real-world units (in m): "))
                # Displays an error message if 0 is entered
                if real_units == 0:
                    print('Diameter cannot be 0!\n')
                    continue
                # Displays an error messgae if a negative value is entered
                elif real_units < 0:
                    print('Please enter a positive value.\n')
                    continue
                Valid = True
            except:
                # Displays an error message if a non-numerical response is given
                print('Please enter a valid float/integer.')

        # Calculates the conversion_ratio
        conversion_ratio = real_units / pixel_units

        return conversion_ratio

    def convert_pixel_units_to_real_world_units(self, pixel_units, conversion_ratio):
        # Converts pixel units to real-world units
        real_units = pixel_units * conversion_ratio
        return real_units

    def convert_radians_to_degrees(self, radians):
        # Converts angle in radians to degrees
        return radians * 180/math.pi

    def convert_degrees_to_radians(self, degrees):
        # Converts angle in degrees to radians
        return degrees * math.pi/180


class Coordinates:
    def __init__(self):
        self.threshold = 2.5

    def get_opencv_coordinates(self):
        # Obtains coordinates of centroids in opencv format from a video source
        opencv_coords = self.video.get_centroid_coords()
        return opencv_coords

    def get_matplotlib_coordinates(self, opencv_coords):
        # Determines maximum y-value from the list of opencv coordinates
        height = max(opencv_coords, key=lambda x: x[1])[1]
        # Subtracts each y-value from the maximum y-value to obtain matplotlib y-coordinates
        matplotlib_coords = [(x, height - y) for x, y in opencv_coords]
        # Returns resulting coordinates as a list of tuples
        return matplotlib_coords

    def remove_outlier_coords(self, coordinates):
        # Extract the x and y coordinates into separate lists
        xvalues, yvalues = self.split_coords(coordinates)

        # Calculate the median for the x and y values
        medianx = np.median(xvalues)
        mediany = np.median(yvalues)

        # Calculate the median absolute deviation (MAD) for the x and y values
        madx = np.median(np.abs(xvalues - medianx))
        mady = np.median(np.abs(yvalues - mediany))

        # Calculate the upper and lower bounds for the x and y values using the self.threshold value
        upperx = medianx + self.threshold * madx
        lowerx = medianx - self.threshold * madx
        uppery = mediany + self.threshold * mady
        lowery = mediany - self.threshold * mady

        # Create a new list of coordinates without outliers
        filtered_coords = []
        for coord in coordinates:
            x, y = coord
            if (lowerx <= x <= upperx) and (lowery <= y <= uppery):
                filtered_coords.append(coord)

        # Returns a list of coordinates stored in the form of tuples with no outliers
        return filtered_coords

    def remove_close_coords(self, coordinates):
        result = []
        for i in range(len(coordinates)):
            too_close = False
            for j in range(i+1, len(coordinates)):
                # Uses pythogoras theorem to calculate the distance between two points
                dist = math.sqrt(
                    (coordinates[i][0]-coordinates[j][0])**2 + (coordinates[i][1]-coordinates[j][1])**2)
                if dist < self.threshold:
                    too_close = True
                    break
            if not too_close:
                result.append(coordinates[i])

        return result

    def split_coords(self, tuple_list):
        # Splits a list of tuples into two separate lists
        xlist = [x for x, y in tuple_list]
        ylist = [y for x, y in tuple_list]

        return xlist, ylist

    def scale_coords(self, xlist, ylist, conversion_ratio):
        xarr = np.array(xlist)
        yarr = np.array(ylist)

        # Matrix scalar multiplication to scale elements in the array by conversion_ratio
        scaledxarr = xarr * conversion_ratio
        scaledyarr = yarr * conversion_ratio

        scaledxlist = list(scaledxarr)
        scaledylist = list(scaledyarr)

        return scaledxlist, scaledylist

    def get_horizontal_translation_units(self, xlist):
        # Gets the first x-coordinate of the list of x-coordinates
        hunit = xlist[0]

        return hunit

    def get_vertical_translation_units(self, ylist):
        # Gets the first y-coordinate of the list of y-coordinates
        vunit = ylist[0]

        return vunit

# Multiple Inheritance
class ProjectileMotion(Calculate, Coordinates):
    def __init__(self):
        super().__init__()
        self.video = Video()

        self.threshold = 2.5

        self.conversion_ratio = self.get_pixel_to_real_world_conversion_ratio(
            self.get_pixel_diameter(), 'diameter of the ball')

        self.hcoords, self.vcoords = self.get_scaled_coordinates()
        self.projectile_type = self.check_projectile_type()

        self.g = 9.81
        self.a, self.b, self.c = self.get_projectile_function_coeffs()
        self.theta = self.estimate_initial_angle()
        self.initial_velocity = self.estimate_initial_velocity()
        self.hdistance_travelled = self.get_horizontal_distance_travelled()

    def get_pixel_diameter(self):
        # Get list of radius values with anomalies removed
        anomalies_removed = self.remove_list_anomalies(
            self.video.get_radius_values())

        # Get average radius value
        average_radius = self.get_average(anomalies_removed)

        # Multiply radius value by two to get diameter value in pixels
        pixel_diameter = average_radius * 2

        if pixel_diameter < 0:
            # Displays error message if no projectile detected
            print(
                'Error in detecting projectile. Please relaunch the program and try again.')

        return pixel_diameter

    def get_scaled_coordinates(self):
        # Translates opencv coordinates into matplotlib coordinates
        # Get unprocessed matplotlib coorindtaes
        raw_coords = self.get_matplotlib_coordinates(
            self.get_opencv_coordinates())
        # Process matplotlib coordinates by removing outliers and coordinates that are too close to each other
        coordinates = self.remove_outlier_coords(
            self.remove_close_coords(raw_coords))

        # Get scaled horizontal and vertical coordinates
        hcoords, vcoords = self.split_coords(coordinates)
        scaledhcoords, scaledvcoords = self.scale_coords(
            hcoords, vcoords, self.conversion_ratio)

        return scaledhcoords, scaledvcoords

    def get_projectile_function_coeffs(self):
        # Get the coefficients of the projectile function
        coeffs = self.get_curve_function_coeffs(2, self.hcoords, self.vcoords)
        a = coeffs[0]
        b = coeffs[1]
        c = coeffs[2]

        return a, b, c

    def check_projectile_type(self):
        # Estimate the gradient of the first five points of the projectile function
        gradient = self.estimate_initial_gradient(self.hcoords, self.vcoords)
        if gradient > 0:
            return 'A'
        else:
            return 'H'

    def estimate_initial_angle(self):
        # Compare linear coefficient to obtain the value of theta
        if self.projectile_type == 'A':
            angle = math.atan(self.b)
        # Angle = 0 for horizontal projectile motion
        elif self.projectile_type == 'H':
            angle = 0

        # Returns angle in radians
        return angle

    def estimate_initial_velocity(self):
        # Compare quadratic coefficient and substitute value of theta obtained earlier to obtain value of initial velocity
        initial_velocity = math.sqrt(
            (self.g) / (2 * abs(self.a) * (math.cos(self.theta)) ** 2))

        return initial_velocity

    def get_time_of_flight(self):
        # Calculate the time of flight
        if self.projectile_type == 'H':
            tmax = math.sqrt(
                (2 * self.get_vertical_distance_travelled()) / self.g)
        elif self.projectile_type == 'A':
            tmax = 2 * self.initial_velocity * np.sin(self.theta) / self.g

        return tmax

    def get_vertical_distance_travelled(self):
        vcoords = sorted(self.vcoords)
        height = vcoords[-1]

        return height

    def get_horizontal_distance_travelled(self):

        if self.projectile_type == 'H':
            theta = 0
        elif self.projectile_type == 'A':
            theta = self.theta

        hdistance = self.initial_velocity * \
            np.cos(theta) * self.get_time_of_flight()

        return hdistance

    def get_actual_trajectory_coords(self):
        xactual = [(x - self.get_horizontal_translation_units(self.hcoords))
                   for x in self.hcoords]
        yactual = [(y - self.get_vertical_translation_units(self.vcoords))
                   for y in self.vcoords]

        return xactual, yactual

    def get_predicted_trajectory_coords(self):
        x0 = 0
        y0 = 0

        # Create an array of time values
        t = np.linspace(0, self.get_time_of_flight(), len(self.hcoords))

        # Initialize lists to store x and y coordinates
        xpredicted = []
        ypredicted = []

        # Calculate and append the x and y coordinates of the projectile to the lists
        for i in range(len(t)):
            x = x0 + self.initial_velocity * np.cos(self.theta) * t[i]
            y = y0 + self.initial_velocity * \
                np.sin(self.theta) * t[i] - 0.5 * self.g * t[i]**2
            xpredicted.append(x)
            ypredicted.append(y)

        return xpredicted, ypredicted

    def plot_trajectories(self):
        xactual, yactual = self.get_actual_trajectory_coords()
        xpredicted, ypredicted = self.get_predicted_trajectory_coords()

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(
            10, 5), num='Graphical Representation')
        # Set a heading shared among both graphs
        fig.suptitle(
            'Actual and Predicted Projectile Trajectories', fontsize=14)

        # Set the margin size between the subplots
        fig.subplots_adjust(wspace=0.4)

        # Plot scatter plot on first subplot
        ax1.scatter(xactual, yactual, label='Actual Path', c='midnightblue')
        ax1.scatter(xpredicted, ypredicted,
                    label='Predicted Path', c='darkmagenta')
        ax1.set_xlabel('Horizontal Distance (m)')
        ax1.set_ylabel('Vertical Distance (m)')

        ax1.legend()

        # Plot continuous plot on second subplot
        ax2.plot(xactual, yactual, label='Actual Path', c='midnightblue')
        ax2.plot(xpredicted, ypredicted,
                 label='Predicted Path', c='darkmagenta')
        ax2.set_xlabel('Horizontal Distance (m)')
        ax2.set_ylabel('Vertical Distance (m)')

        ax2.legend()

        # Display the figure
        plt.show()
