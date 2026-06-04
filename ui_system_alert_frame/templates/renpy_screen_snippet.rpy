# Review-only Ren'Py screen snippet for ui_system_alert_frame candidates.
# Copy/adapt into a target project only after an exact candidate is approved.

screen ui_system_alert_frame_review(message, frame_image):
    zorder 100
    modal True

    add frame_image xalign 0.5 yalign 0.5

    frame:
        xalign 0.5
        yalign 0.5
        xsize 780
        ysize 230
        background None

        text message:
            xalign 0.5
            yalign 0.5
            textalign 0.5
            size 34
            color "#f6e8d0"
            outlines [(2, "#160606", 0, 0)]
