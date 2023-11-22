import mediapipe as mp
import cv2
import numpy as np
import time

# constants
ml = 150
max_x, max_y = 250 + ml, 50
curr_tool = "select tool"
time_init = True
rad = 40
var_inits = False
thick = 4
prevx, prevy = 0, 0

# Colors
RED_COLOR = (0, 0, 255)
BLUE_COLOR = (255, 0, 0)
YELLOW_COLOR = (0, 255, 255)
GREEN_COLOR = (0, 255, 0)
BLACK_COLOR = (0, 0, 0)

# selectedColor
selected_color = RED_COLOR  # สีเริ่มต้น

def get_color_name(color):
    if color == RED_COLOR:
        return "Red"
    elif color == BLUE_COLOR:
        return "Blue"
    elif color == YELLOW_COLOR:
        return "Yellow"
    elif color == GREEN_COLOR:
        return "Green"
    elif color == BLACK_COLOR:
        return "BLACK"
    else:
        return "Unknown"

# get tools function
def getTool(x):
    if x < 50 + ml:
        return "line"
    elif x < 100 + ml:
        return "rectangle"
    elif x < 150 + ml:
        return "draw"
    elif x < 200 + ml:
        return "circle"
    elif x < 250 + ml:
        return "erase"

def index_raised(yi, y9):
    if (y9 - yi) > 40:
        return True
    return False

hands = mp.solutions.hands
hand_landmark = hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6, max_num_hands=1)
draw = mp.solutions.drawing_utils

# drawing tools
tools = cv2.imread("tools.png")
tools = tools.astype('uint8')

# Create a binary mask for the non-white pixels in the tools image
tools_mask = cv2.cvtColor(tools, cv2.COLOR_BGR2GRAY)
tools_mask = cv2.threshold(tools_mask, 1, 255, cv2.THRESH_BINARY)[1]

mask = np.ones((480, 640)) * 255
mask = mask.astype('uint8')

# เพิ่มตัวแปร
index_finger_up = False

cap = cv2.VideoCapture(1)
while True:
    _, frm = cap.read()
    frm = cv2.flip(frm, 1)
    rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
    op = hand_landmark.process(rgb)

    # วาดปุ่มสี
    cv2.rectangle(frm, (ml + 400, max_y), (ml + 450, max_y + 30), RED_COLOR, -1)
    cv2.putText(frm, "Red", (ml + 405, max_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(frm, (ml + 400, max_y + 40), (ml + 450, max_y + 70), BLUE_COLOR, -1)
    cv2.putText(frm, "Blue", (ml + 405, max_y + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(frm, (ml + 400, max_y + 80), (ml + 450, max_y + 110), YELLOW_COLOR, -1)
    cv2.putText(frm, "Yellow", (ml + 405, max_y + 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(frm, (ml + 400, max_y + 120), (ml + 450, max_y + 150), GREEN_COLOR, -1)
    cv2.putText(frm, "Green", (ml + 405, max_y + 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(frm, (ml + 400, max_y + 160), (ml + 450, max_y + 190), BLACK_COLOR, -1)
    cv2.putText(frm, "Black", (ml + 405, max_y + 185), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    # ที่ส่วนของการตรวจสอบนิ้ว
    if op.multi_hand_landmarks:
        for i in op.multi_hand_landmarks:
            draw.draw_landmarks(frm, i, hands.HAND_CONNECTIONS)
            x, y = int(i.landmark[8].x * 640), int(i.landmark[8].y * 480)
            xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)
            y9 = int(i.landmark[9].y * 480)

            # ตรวจสอบว่านิ้วชี้ยกขึ้นหรือไม่
            index_finger_up = index_raised(yi, y9)
            red_button = (ml + 450, max_y + 30)
            blue_button = (ml + 450, max_y + 70)
            yellow_button = (ml + 450, max_y + 110)
            green_button = (ml + 450, max_y + 150)
            black_button = (ml + 450, max_y + 190)

            print("Index Finger Coordinates: ", xi, yi)
            print("Index Finger Up: ", index_finger_up)

            if x < max_x and y < max_y and x > ml:
                if time_init:
                    ctime = time.time()
                    time_init = False
                ptime = time.time()

                cv2.circle(frm, (x, y), rad, (0, 255, 255), 2)
                rad -= 1

                if (ptime - ctime) > 0.8:
                    curr_tool = getTool(x)
                    print("your current tool set to : ", curr_tool)
                    time_init = True
                    rad = 40
            else:
                time_init = True
                rad = 40

                in_color_button_area = False
                if red_button[0] < x < red_button[0] + 50 and red_button[1] < y < red_button[1] + 30:
                    in_color_button_area = True
                    selected_color = RED_COLOR
                    temp_selected_color = RED_COLOR
                    cv2.circle(frm, (x, y), rad, selected_color, thick)
                    rad -= 1
                elif blue_button[0] < x < blue_button[0] + 50 and blue_button[1] < y < blue_button[1] + 30:
                    in_color_button_area = True
                    selected_color = BLUE_COLOR
                    temp_selected_color = BLUE_COLOR
                    cv2.circle(frm, (x, y), rad, selected_color, thick)
                    rad -= 1
                elif yellow_button[0] < x < yellow_button[0] + 50 and yellow_button[1] < y < yellow_button[1] + 30:
                    in_color_button_area = True
                    selected_color = YELLOW_COLOR
                    temp_selected_color = YELLOW_COLOR
                    cv2.circle(frm, (x, y), rad, selected_color, thick)
                    rad -= 1
                elif green_button[0] < x < green_button[0] + 50 and green_button[1] < y < green_button[1] + 30:
                    in_color_button_area = True
                    selected_color = GREEN_COLOR
                    temp_selected_color = GREEN_COLOR
                    cv2.circle(frm, (x, y), rad, selected_color, thick)
                    rad -= 1
                elif green_button[0] < x < green_button[0] + 50 and green_button[1] < y < green_button[1] + 30:
                    in_color_button_area = True
                    selected_color = GREEN_COLOR
                    temp_selected_color = GREEN_COLOR
                    cv2.circle(frm, (x, y), rad, selected_color, thick)
                    rad -= 1
                elif black_button[0] < x < black_button[0] + 50 and black_button[1] < y < black_button[1] + 30:
                    in_color_button_area = True
                    selected_color = BLACK_COLOR
                    temp_selected_color = BLACK_COLOR
                    cv2.circle(frm, (x, y), rad, selected_color, thick)
                    rad -= 1
                else:
                    rad = max(1, rad - 1)

            if curr_tool == "draw":
                xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)
                y9 = int(i.landmark[9].y * 480)
                if index_raised(yi, y9):
                    # แปลง selected_color ให้เป็น tuple ของจำนวนเต็ม
                    color_tuple = tuple(map(int, selected_color))
                    cv2.line(mask, (prevx, prevy), (x, y), color_tuple, thick)
                    prevx, prevy = x, y
                else:
                    prevx = x
                    prevy = y


            elif curr_tool == "line":

                xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)

                y9 = int(i.landmark[9].y * 480)

                if index_raised(yi, y9):

                    if not (var_inits):
                        xii, yii = x, y

                        var_inits = True

                    # Convert selected_color to a tuple of integers

                    color_tuple = tuple(int(c) for c in selected_color)

                    cv2.line(frm, (xii, yii), (x, y), color_tuple, thick)

                else:

                    if var_inits:
                        cv2.line(mask, (xii, yii), (x, y), color_tuple, thick)

                        var_inits = False

            elif curr_tool == "rectangle":
                xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)
                y9 = int(i.landmark[9].y * 480)
                if index_raised(yi, y9):
                    if not (var_inits):
                        xii, yii = x, y
                        var_inits = True
                    # Convert selected_color to a tuple of integers
                    color_tuple = tuple(int(c) for c in selected_color)
                    cv2.rectangle(frm, (xii, yii), (x, y), color_tuple, thick)
                else:
                    if var_inits:
                        cv2.rectangle(mask, (xii, yii), (x, y), color_tuple, thick)
                        var_inits = False

            elif curr_tool == "circle":
                xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)
                y9 = int(i.landmark[9].y * 480)
                if index_raised(yi, y9):
                    if not (var_inits):
                        xii, yii = x, y
                        var_inits = True
                    # Convert selected_color to a tuple of integers
                    color_tuple = tuple(int(c) for c in selected_color)
                    cv2.circle(frm, (xii, yii), int(((xii - x) ** 2 + (yii - y) ** 2) ** 0.5), color_tuple, thick)
                else:
                    if var_inits:
                        cv2.circle(mask, (xii, yii), int(((xii - x) ** 2 + (yii - y) ** 2) ** 0.5), color_tuple, thick)
                        var_inits = False

            elif curr_tool == "erase":
                xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)
                y9 = int(i.landmark[9].y * 480)
                if index_raised(yi, y9):
                    cv2.circle(frm, (x, y), 30, (0, 0, 0), -1)
                    cv2.circle(mask, (x, y), 30, 255, -1)

    # Apply the tools image on the frame using the binary mask
    tools_mask_inv = cv2.bitwise_not(tools_mask)
    frm[:max_y, ml:max_x] = cv2.bitwise_and(frm[:max_y, ml:max_x], frm[:max_y, ml:max_x], mask=tools_mask_inv)
    frm[:max_y, ml:max_x] = cv2.addWeighted(frm[:max_y, ml:max_x], 1, tools, 0.7, 0)
    op = cv2.bitwise_and(frm, frm, mask=mask)
    frm[:max_y, ml:max_x] = cv2.addWeighted(frm[:max_y, ml:max_x], 1, op[:max_y, ml:max_x], 1, 0)
    frm[:, :, 2] = op[:, :, 2]
    frm[:, :, 1] = op[:, :, 1]
    frm[:, :, 0] = op[:, :, 0]
    frm = cv2.bitwise_and(frm, frm, mask=mask)

    color_name = get_color_name(selected_color)
    cv2.putText(frm, f"Color: {color_name}", (270 + ml, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, selected_color, 2)
    cv2.putText(frm, f"Tool: {curr_tool}", (270 + ml, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, selected_color, 2)
    cv2.imshow("paint app", frm)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        cap.release()
        break
