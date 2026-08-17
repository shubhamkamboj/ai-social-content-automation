from textwrap import wrap
from PIL import ImageDraw

def render_topic_card(draw,title,category,summary,key_points,fonts):
    title_font, category_font, section_font, body_font=fonts
    draw.rounded_rectangle((70,70,1010,1730),radius=34,outline=160,width=3)
    draw.text((110,115),category.upper(),font=category_font)
    y=190
    for line in wrap(title.upper(),width=24)[:3]: draw.text((110,y),line,font=title_font); y+=title_font.size+8
    y+=24
    draw.rounded_rectangle((110,y,970,y+210),radius=26,outline=160,width=2)
    draw.text((140,y+30),"AT A GLANCE",font=section_font)
    by=y+80
    for line in wrap(summary,width=58): draw.text((140,by),line,font=body_font); by+=body_font.size+8
    y+=250; draw.text((110,y),"KEY CONCEPTS",font=section_font); y+=70
    for point in key_points[:5]:
        draw.ellipse((115,y+8,131,y+24),outline=160,width=2)
        for line in wrap(point,width=60): draw.text((150,y),line,font=body_font); y+=body_font.size+6
        y+=14
    draw.text((110,1650),"TECH CHEAT SHEET • AUTO-GENERATED",font=category_font)
