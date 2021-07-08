import pafy
import cv2


url = "" # Coloque aqui o endereco do video que voce vai utilizar. 
video = pafy.new(url)
best = video.getbest(preftype="mp4")
capture = cv2.VideoCapture(best.url)

while True:
    ret, frame = capture.read()
    if ret:
        cv2.imshow('Frame', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyWindow('Frame')
            break
    else:
        break
