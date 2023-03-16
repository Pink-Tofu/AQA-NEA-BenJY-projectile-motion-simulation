from interface import *

if __name__ == '__main__':
    # Displays the loading screen (splash screen)
    run_splash_screen()
    # Instantiates the Display() class
    display = Display()
    # Prompts user to enter the horizontal distance travelled by the projectile
    display.horizontal_distance_prompt()
    # Displays physics explanations
    display.physics_explanations()
