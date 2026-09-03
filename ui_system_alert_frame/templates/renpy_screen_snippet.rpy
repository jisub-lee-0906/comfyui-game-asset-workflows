# Review-only non-modal Ren'Py alert preview.
# Copy/adapt only after an exact textless frame candidate is approved.

screen ui_system_alert_frame_review(message, frame_image):
    zorder 100
    modal False

    fixed:
        xpos 48
        ypos 48
        xysize (720, 240)

        add frame_image:
            xysize (720, 240)
            alpha 0.96

        text message:
            xalign 0.5
            yalign 0.5
            xmaximum 620
            textalign 0.5
            size 34
            color "#f6e8d0"
            outlines [(2, "#160606", 0, 0)]
