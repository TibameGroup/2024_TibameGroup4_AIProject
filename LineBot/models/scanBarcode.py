from PIL import Image # pip install Pillow==8.0.0
from pyzbar.pyzbar import decode

# 掃描條碼
def scanBarcode(imagePath):
    """return string barcode message = [barcodeType, barcodeContent]"""
    barcode = []
    img = Image.open(imagePath)
    decoded_objects = decode(img)

    if len(decoded_objects) != 0:
        for obj in decoded_objects:
            barcode_data = obj.data.decode('utf-8')
            barcode_type = obj.type
            barcode = [barcode_type, barcode_data]
    return barcode

if __name__ == "__main__":
    imagePath = r'.\image\barcodeImg\example.jpg'
    result = scanBarcode(imagePath)
    print(f"BarcodeType: {result[0]}\nBarcode: {result[1]}")
