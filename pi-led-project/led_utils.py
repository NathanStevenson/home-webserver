from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# add a title field fixed to the top (used for calendar, weather, etc to show the date)
def display_text(
    text: str,
    title: None,
    color=(255, 0, 0),
    scroll: bool = False,
    wrap: bool = False,
    font_path: str = "/home/pi/rpi-rgb-led-matrix/fonts/7x13.bdf",
    duration: int = 10
):
    """
    Display text on 32x64 LED matrix.

    Args:
        text: Text string to display
        color: (R, G, B) tuple
        scroll: Scroll text if too long
        wrap: Wrap text onto new lines if too long
        font_path: Path to .bdf font
        duration: Seconds to display text (ignored if scroll=True)
    """
    # Configure LED matrix
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = "led_gpio_mapping"  # Adjust if different HAT/Bonnet; may just remove once we have LED; think i did not need chainlength/parallel either
    matrix = RGBMatrix(options=options)

    # Load font
    font = graphics.Font()
    font.LoadFont(font_path)

    text_color = graphics.Color(*color)
    offscreen_canvas = matrix.CreateFrameCanvas()

    if scroll:
        pos = offscreen_canvas.width
        while True:
            offscreen_canvas.Clear()
            length = graphics.DrawText(offscreen_canvas, font, pos, 20, text_color, text)
            pos -= 1
            if pos + length < 0:
                pos = offscreen_canvas.width
            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            time.sleep(0.05)  # Scroll speed
    else:
        # if there is a title first line is title next line is text for (weather, calendar event, clock)
        if title:
            offscreen_canvas.Clear()
            y = 15
            # Only 2 lines fit on 32px height - title is always white
            graphics.DrawText(offscreen_canvas, font, 2, y, graphics.Color(255, 255, 255), title)
            y += 15
            graphics.DrawText(offscreen_canvas, font, 2, y, text_color, text)

            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            time.sleep(duration)

        else:
            lines = [text]
            if wrap:
                max_chars = 15  # Rough estimate for 64px wide panel
                lines = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

            offscreen_canvas.Clear()
            y = 15
            for line in lines[:2]:  # Only 2 lines fit on 32px height
                graphics.DrawText(offscreen_canvas, font, 2, y, text_color, line)
                y += 15
            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            time.sleep(duration)

# clears the canvas of the LED screen
def clear_canvas():
    # Configure LED matrix
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = "led_gpio_mapping"  # Adjust if different HAT/Bonnet
    matrix = RGBMatrix(options=options)

    offscreen_canvas = matrix.CreateFrameCanvas()
    offscreen_canvas.Clear()

if __name__ == "__main__":
    # Example usage
    display_text("Hello World!", color=(0, 255, 0), scroll=False, wrap=True)
