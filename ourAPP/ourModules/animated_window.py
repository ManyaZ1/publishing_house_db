import tkinter as tk
import math
import time

class AnimatedWindow:
    def __init__(self, window, start_size=(100, 100), final_size=(400, 400), duration=1500):
        """
        Initialize the AnimatedWindow instance.

        :param window: The Tkinter window to animate.
        :param start_size: Tuple (width, height) for the initial window size.
        :param final_size: Tuple (width, height) for the target window size.
        :param duration: Animation duration in milliseconds.
        """
        self.window = window
        self.start_width, self.start_height = start_size
        self.final_width, self.final_height = final_size
        self.duration = duration

        # These will store the starting position for consistent animations
        self.start_x = None
        self.start_y = None

        return;

    @staticmethod
    def ease_in_out(progress):
        """
        Easing function for smooth acceleration and deceleration.

        :param progress: A value between 0 and 1 representing animation progress.
        :return: Adjusted progress using cosine easing.
        """
        return -0.5 * (math.cos(math.pi * progress) - 1);

    def open_animation(self, start_x=None, start_y=None):
        """
        Animates the window opening with a smooth resizing and movement effect.

        :param start_x: Starting x-coordinate (optional). Defaults to the current mouse x position.
        :param start_y: Starting y-coordinate (optional). Defaults to the current mouse y position.
        """
        # Determine start position and save it for the closing animation
        self.start_x = start_x or self.window.winfo_pointerx()
        self.start_y = start_y or self.window.winfo_pointery()

        # Calculate deltas for size and position
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        final_x = (screen_width - self.final_width) // 2
        final_y = (screen_height - self.final_height) // 2

        width_delta = self.final_width - self.start_width
        height_delta = self.final_height - self.start_height
        x_delta = final_x - self.start_x
        y_delta = final_y - self.start_y

        start_time = time.time()
        total_time = self.duration / 1000.0 # Convert duration to seconds

        def update_frame():
            elapsed_time = time.time() - start_time
            progress = min(elapsed_time / total_time, 1.0)
            eased_progress = self.ease_in_out(progress)

            # Calculate current size and position
            current_width = max(1, int(self.start_width + width_delta * eased_progress))
            current_height = max(1, int(self.start_height + height_delta * eased_progress))
            current_x = int(self.start_x + x_delta * eased_progress)
            current_y = int(self.start_y + y_delta * eased_progress)

            # Update window size and position
            self.window.geometry(f"{current_width}x{current_height}+{current_x}+{current_y}")

            if progress < 1.0: # Continue animation if not complete
                self.window.after(5, update_frame)

            return;

        update_frame()

        return;

    def close_animation(self):
        """
        Animates the window closing with a smooth resizing and movement effect,
        returning to the same starting position as the open animation.
        """
        # Get the current position and size of the window
        self.window.update_idletasks()
        geometry = self.window.geometry()
        current_width, current_height, current_x, current_y = map(int, geometry.replace("x", "+").split("+"))

        # Calculate deltas for size and position
        width_delta = current_width - self.start_width
        height_delta = current_height - self.start_height
        x_delta = current_x - self.start_x
        y_delta = current_y - self.start_y

        start_time = time.time()
        total_time = self.duration / 1000.0 # Convert duration to seconds

        def update_frame():
            nonlocal current_width, current_height, current_x, current_y

            elapsed_time = time.time() - start_time
            progress = min(elapsed_time / total_time, 1.0)
            eased_progress = self.ease_in_out(progress)

            # Calculate current size and position
            current_width = max(1, int(self.start_width + width_delta * (1 - eased_progress)))
            current_height = max(1, int(self.start_height + height_delta * (1 - eased_progress)))
            current_x = int(self.start_x + x_delta * (1 - eased_progress))
            current_y = int(self.start_y + y_delta * (1 - eased_progress))

            # Update window size and position
            self.window.geometry(f"{current_width}x{current_height}+{current_x}+{current_y}")

            if progress < 1.0: # Continue animation if not complete
                self.window.after(5, update_frame)
            else:
                self.window.destroy()

            return;

        update_frame()

        return;

def main():
    # Create the main application window
    root = tk.Tk()
    root.withdraw() # Hide the root window

    # Create a new window
    new_window = tk.Toplevel(root)
    new_window.title("Animated Window")

    # Initialize animator and set up animations
    animator = AnimatedWindow(new_window, start_size=(150, 150), final_size=(500, 300), duration=500)
    new_window.protocol("WM_DELETE_WINDOW", animator.close_animation) # Attach close animation

    # Animate the window opening
    animator.open_animation()

    root.mainloop()

    return;

if __name__ == "__main__":
    main()
