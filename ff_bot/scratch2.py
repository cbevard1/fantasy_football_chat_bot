from nfl_fantasy import League
from PIL import Image, ImageDraw, ImageFont

if __name__ == '__main__':
    league = League(91, debug=True)
    print(league.teams)

    img = Image.new('RGB', (350, 350), color=(255, 255, 255))

    fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 15)
    d = ImageDraw.Draw(img)
    d.text((10, 10), league.box_scores(), font=fnt, fill=(0, 0, 0))

    img.save('pil_text_font.png')
