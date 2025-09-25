from rgbmatrix import graphics
import time

# add a title field fixed to the top (used for calendar, weather, etc to show the date)
def display_text(
    matrix,
    offscreen_canvas,
    text_font,
    title_font,
    lines,
    hasTitle=False,
    title_gap=10,
    text_gap=8,
    color=(255, 0, 0),
    scroll: bool = False,
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
    # pass in offscreen_canvas and make it global or return it so we can update it w/o calling CreateFromCanvas a ton
    text_color = graphics.Color(*color)
    # scrolling logic mainly untested
    if scroll:
        pos = offscreen_canvas.width
        while True:
            offscreen_canvas.Clear()
            for line in lines:
                length = graphics.DrawText(offscreen_canvas, text_font, pos, 20, text_color, line)
                pos -= 1
                if pos + length < 0:
                    pos = offscreen_canvas.width
            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            time.sleep(0.05)  # Scroll speed

    # wrap and title logic
    else:
        # start by clearing the off-screen canvas so clean slate guaranteed to draw on
        offscreen_canvas.Clear()
        first_text_line = 0
        y = 8
        # If there is a title first draw the title in white and then add the given title gap to the Y position (weather, calendar event, clock)
        if hasTitle:
            graphics.DrawText(offscreen_canvas, title_font, 2, y, graphics.Color(255, 255, 255), lines[0])
            y += title_gap
            first_text_line = 1

        # draw the correct # of lines
        for line in lines[first_text_line:]:
            graphics.DrawText(offscreen_canvas, text_font, 2, y, text_color, line)
            y += text_gap

        # swap the off-screen canvas to the matrix (display it all at once)
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    
    return offscreen_canvas

# clears the offscreen canvas and the on screen of the LED -- would be cool if the title stayed - clear only portion of the matrix look into the docs
def clear_canvas(matrix):
    matrix.Clear()

if __name__ == "__main__":
    # Example usage
    display_text("Hello World!", color=(0, 255, 0), scroll=False, wrap=True)
