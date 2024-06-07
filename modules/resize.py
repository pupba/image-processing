# Resize and Fill
from PIL import ImageFilter
from PIL import ImageOps

# 이미지를 비율에 맞게 리사이즈하고 빈공간을 채움
# 기본 업스케일러
LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)

sd_upscalers = []
# resize 이미지
def resize_image(im:Image, width:int, height:int, upscaler_name=None):
    """
    im: 리사이즈할 이미지
    width: 변경할 width
    height: 변경할 height
    upscaler_name: 업스케일러 이름
    """
    def resize(im, w, h):
        if upscaler_name is None or upscaler_name == "None" or im.mode == 'L':
            return im.resize((w, h), resample=LANCZOS)

        scale = max(w / im.width, h / im.height)
        if scale > 1.0:
            upscalers = [x for x in sd_upscalers if x.name == upscaler_name]
            if len(upscalers) == 0:
                upscaler = sd_upscalers[0]
                print(f"could not find upscaler named {upscaler_name or '<empty string>'}, using {upscaler.name} as a fallback")
            else:
                upscaler = upscalers[0]

            im = upscaler.scaler.upscale(im, scale, upscaler.data_path)

        if im.width != w or im.height != h:
            im = im.resize((w, h), resample=LANCZOS)

        return im
    
    ratio = width / height
    src_ratio = im.width / im.height

    src_w = width if ratio < src_ratio else im.width * height // im.height
    src_h = height if ratio >= src_ratio else im.height * width // im.width

    resized = resize(im, src_w, src_h) # upscaling

    res = Image.new("RGB", (width, height)) # resize
    res.paste(resized, box=(width // 2 - src_w // 2, height // 2 - src_h // 2))

    if ratio < src_ratio:
        fill_height = height // 2 - src_h // 2
        if fill_height > 0:
            res.paste(resized.resize((width, fill_height), box=(0, 0, width, 0)), box=(0, 0))
            res.paste(resized.resize((width, fill_height), box=(0, resized.height, width, resized.height)), box=(0, fill_height + src_h))
    elif ratio > src_ratio:
        fill_width = width // 2 - src_w // 2
        if fill_width > 0:
            res.paste(resized.resize((fill_width, height), box=(0, 0, 0, height)), box=(0, 0))
            res.paste(resized.resize((fill_width, height), box=(resized.width, 0, resized.width, height)), box=(fill_width + src_w, 0))

    return res
  
# 리사이즈 한 이미지를 원본 상태로 변경
def resizeOriginal(image:Image,owidth:int,oheight:int)->Image:
   """
    image: 리사이즈할 이미지
    owidth: 원본 width
    oheight: 원본 height
    """
    if oheight > owidth:
        # 가로의 길이가 Fill 된 경우
        # 원본의 세로 크기로 resize
        resize_im = resize_image(image,oheight,oheight)
        # 좌,우,위,아래 값 구하기
        left = (oheight - owidth) // 2
        right = (left + owidth)
        top = 0
        bottom = oheight
    elif oheight < owidth:
        # 세로의 길이가 Fill 된 경우
        resize_im = resize_image(image,owidth,owidth)
        left = 0
        right = owidth
        top = (owidth - oheight) // 2
        bottom = (top + oheight)
    else: # 정방 형태는 그냥 resize만 해주면됨
        resize_im = resize_image(image,owidth,oheight)
        return resize_im
    crop_img = resize_im.crop((left,top,right,bottom))
    return crop_img
