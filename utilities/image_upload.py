from PIL import Image
from io import BytesIO

im1 = Image.open("banana_instagram.PNG")
imagefile = BytesIO()
im1.save(imagefile, format="PNG")
imagedata = imagefile.getvalue()
print(type(imagedata))
strimage = str(imagedata)
print("image len: ", len(strimage))
im2 = Image.open(imagefile)
im2.show()

