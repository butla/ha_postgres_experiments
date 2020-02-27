import json
import time


def experiment():
    data = {
        "widget": {
            "debug": "on",
            "window": {
                "title": "Sample Konfabulator Widget",
                "name": "main_window",
                "width": 500,
                "height": 500
            },
            "image": {
                "src": "Images/Sun.png",
                "name": "sun1",
                "hOffset": 250,
                "vOffset": 250,
                "alignment": "center"
            },
            "text": {
                "data": "Click Here",
                "size": 36,
                "style": "bold",
                "name": "text1",
                "hOffset": 250,
                "vOffset": 100,
                "alignment": "center",
                "onMouseUp": "sun1.opacity = (sun1.opacity / 100) * 90;"
            }
        }
    }

    print('writing f1')
    f1 = open('bla_unicode.txt', 'w')
    start = time.perf_counter()
    while time.perf_counter() - start < 15:
        f1.write(f'{json.dumps(data)}\n')
    f1.close()

    serialized_data = json.dumps(data).encode() + b'\n'

    print('writing f2')
    f2 = open('bla_raw.txt', 'wb')
    start = time.perf_counter()
    while time.perf_counter() - start < 15:
        f2.write(serialized_data)
    f2.close()


if __name__ == '__main__':
    experiment()
