import streamlit as st
import tempfile
import os
from PIL import Image
import turtle

def create_turtle_image(filename):
    # Set up a hidden turtle screen
    screen = turtle.Screen()
    screen.setup(width=600, height=600)
    screen.bgcolor("white")
    screen.title("Turtle Graphics")
    screen.tracer(0)

    # Create turtle
    t = turtle.Turtle()
    t.speed(0)
    t.pensize(3)
    t.color("blue")

    # Example drawing: colorful spiral
    for i in range(36):
        t.forward(200)
        t.right(170)
        t.color("red" if i % 2 == 0 else "blue")
    t.hideturtle()

    # Save the drawing as a PostScript file
    canvas = turtle.getcanvas()
    canvas.postscript(file=filename + ".ps", colormode='color')

    # Convert PostScript to PNG
    img = Image.open(filename + ".ps")
    img.save(filename)

    # Cleanup
    turtle.bye()

# Streamlit app layout
st.title("Turtle Graphics in Streamlit")
st.write("Click the button to generate and display a Turtle drawing.")

if st.button("Generate Drawing"):
    with st.spinner("Generating Turtle drawing..."):
        # Create a temporary file to save the image
        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = os.path.join(tmpdirname, "turtle_image")
            create_turtle_image(filename)
            # Load the saved image
            image = Image.open(filename)
            # Display the image
            st.image(image, caption="Turtle Graphics", use_column_width=True)
